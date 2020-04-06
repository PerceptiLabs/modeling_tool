uimport zmq
import time
import logging
import threading
import itertools


log = logging.getLogger(__name__)


class ConnectionTimeout(Exception):
    pass


class ConnectionLost(Exception):
    pass


class ConnectionClosed(Exception):
    pass


class NotConnectedError(Exception):
    pass

    

class ZmqClient:
    def __init__(self, subscribe_address, push_address, context=None, tag=None, server_timeout=10):
        self._subscribe_address = subscribe_address
        self._push_address = push_address        
        self._context = context or zmq.Context()
        self._t_last_message = None
        self._tag = tag
        self._connect_called = False
        self._server_timeout = server_timeout
    
    def connect(self, timeout=10):
        log.info(f"Connect called [{self.tag}]")        
        self._connect_called = True
        
        log.info(f"Creating subscribe socket. Address: {self._subscribe_address} [{self.tag}]")
        self._t_last_message = None
        self._subscribe_socket = self._context.socket(zmq.SUB)
        self._subscribe_socket.linger = 0
        self._subscribe_socket.setsockopt(zmq.SUBSCRIBE, b'control')
        self._subscribe_socket.setsockopt(zmq.SUBSCRIBE, b'generic')        
        self._subscribe_socket.connect(self._subscribe_address)

        log.info(f"Creating push socket. Address: {self._push_address} [{self.tag}]")
        self._push_socket = self._context.socket(zmq.PUSH)
        self._push_socket.linger = 0
        self._push_socket.connect(self._push_address)

        log.info(f"Registering subscribe socket for polling [{self.tag}]")                        
        self._poller = zmq.Poller()
        self._poller.register(self._subscribe_socket, zmq.POLLIN)

        t0 = time.perf_counter()        
        for counter in itertools.count():
            log.info(f"Starting connection attempt {counter+1}. [{self.tag}]")
            
            if timeout and time.perf_counter() - t0 >= timeout:
                raise ConnectionTimeout('Connection handshake took too long!')

            self._push_socket.send_multipart([b'control', b'connect'])
            items = dict(self._poller.poll(timeout=1000)) # msec
            if self._subscribe_socket in items:
                # If we receive a message we are connected (most likely a response to our ping)
                self._t_last_message = time.time()                            
                break

        log.info(f"Connection successful after {counter+1} attempt(s). [{self.tag}]")

    def get_messages(self, timeout=0.01):
        if self._t_last_message is None:
            raise NotConnectedError('Not connected. Call connect first!')
        
        items = dict(self._poller.poll(timeout=timeout*1000)) # msec
        if self._subscribe_socket in items:
            messages = []
            while self._subscribe_socket in items:
                key, value = self._subscribe_socket.recv_multipart()
                self._t_last_message = time.time()
                if key == b'generic':
                    messages.append(value)
                elif key == b'control':
                    #log.info(f"Received control message {value} [{self.tag}]")
                    if value == b'ack-shutdown':
                        raise ConnectionClosed                    
                items = dict(self._poller.poll(timeout=timeout*1000)) # msec
            return messages
        else:
            is_dead = time.time() - self._t_last_message >= self._server_timeout
            if is_dead:
                raise ConnectionLost()
            else:
                return []

    def send_message(self, message):
        self._push_socket.send_multipart([b'generic', message])
        
    def stop(self, terminate_context=True):
        if self._connect_called:
            log.info(f"Closing sockets. [{self.tag}]")
            self._subscribe_socket.close()
            self._push_socket.close()

            if terminate_context:
                log.info(f"Terminating ZMQ context. [{self.tag}]")
                self._context.term()

    def shutdown_server(self):
        self._push_socket.send_multipart([b'control', b'shutdown'])        

    @property
    def tag(self):
        if self._tag is None:
            return f"client {id(self)}"
        else:
            return self._tag


class ServerWorker(threading.Thread):
    def __init__(self, context, publish_address, pull_address, ping_interval):
        super().__init__(daemon=True)
        
        self._context = context
        self._publish_address = publish_address
        self._pull_address = pull_address
        self._ping_interval = ping_interval
        self._force_stopped = threading.Event()
        
    def run(self):
        log.info(f"Creating sockets [{self.tag}]")        
        publish_socket = self._context.socket(zmq.PUB)
        publish_socket.linger = 0                
        publish_socket.bind(self._publish_address)

        log.info(f"Binding sockets [{self.tag}]")                
        pull_socket = self._context.socket(zmq.PULL)
        pull_socket.linger = 0                        
        pull_socket.bind(self._pull_address)

        log.info(f"Registering pull socket for poller [{self.tag}]")                        
        poller = zmq.Poller()
        poller.register(pull_socket, zmq.POLLIN)

        stopped = False
        t_ping = None
        while not stopped and not self._force_stopped:
            items = dict(poller.poll(timeout=1)) # msec
            if pull_socket in items:
                stopped = self._process_message(pull_socket, publish_socket)

            t = time.time()
            if t_ping is None or t - t_ping >= self._ping_interval:
                publish_socket.send_multipart([b'control', b'keep-alive'])
                t_ping = t

        if self._force_stopped.is_set():
            log.info(f"Worker force stopped..! [{self.tag}]")

        log.info(f"Closing sockets [{self.tag}]")                                
        publish_socket.close()
        pull_socket.close()
        #self._context.term()
        log.info(f"Leaving worker run method [{self.tag}]")                                        
                    
    def _process_message(self, pull_socket, publish_socket):
        stopped = False
        key, value = pull_socket.recv_multipart()

        if key == b'control':
            if value == b'connect':
                publish_socket.send_multipart([b'control', b'ack-connect'])
            elif value == b'shutdown':
                publish_socket.send_multipart([b'control', b'ack-shutdown'])
                stopped = True
            else:
                raise RuntimeError(f"Unexpected control value: {value}")            
        elif key == b'generic':
            publish_socket.send_multipart([key, value])            
        else:
            raise RuntimeError(f"Unexpected message key: {key}")

        return stopped

    @property
    def tag(self):
        return f"server worker {id(self)}"

    def force_stop(self):
        self._threading_event.set()
    
        
class ZmqServer:
    def __init__(self, publish_address, pull_address, ping_interval=3):
        self._publish_address = publish_address
        self._pull_address = pull_address
        self._ping_interval = ping_interval        
        self._start_called = False
        self._context = zmq.Context()
        self._worker_thread = None

    def is_alive(self):
        return self._worker_thread is not None and self._worker_thread.is_alive

    def start(self):
        self._start_called = True
        log.info(f"Starting worker. Publish address: {self._publish_address}, pull address: {self._pull_address} [{self.tag}]")                        
        self._worker_thread = ServerWorker(
            self._context,
            self._publish_address,
            self._pull_address,
            self._ping_interval
        )
        self._worker_thread.start()

        log.info(f"Creating client [{self.tag}]")                                
        self._client = ZmqClient(
            self._publish_address.replace('*', 'localhost'),
            self._pull_address.replace('*', 'localhost'),
            context=self._context,
            tag=f"internal client of {self.tag}",
        )
        log.info(f"Created {self._client.tag}. Connecting. [{self.tag}]")
        self._client.connect()
        log.info(f"Server running... [{self.tag}]")                        
        
    def stop(self):
        if self._start_called:
            log.info(f"Shutting down server [{self.tag}]")
            self._client.shutdown_server()
            log.info(f"Stopping {self._client.tag}. [{self.tag}]")
            self._client.stop(terminate_context=False)
            
            log.info(f"Joining worker thread [{self.tag}]")        
            self._worker_thread.join(timeout=30)

            if self._worker_thread.is_alive():
                log.info(f"Force stopping worker [{self.tag}]")
                self._worker_thread.force_stop()
                self._worker_thread.join()
                log.info(f"Joining worker thread [{self.tag}]")                    
                
            log.info(f"Terminating ZMQ context. [{self.tag}]")
            self._context.term()

    @property
    def tag(self):
        return f"server {id(self)}"
        
    def send_message(self, message):
        self._client.send_message(message)

    def get_messages(self):
        return self._client.get_messages()
