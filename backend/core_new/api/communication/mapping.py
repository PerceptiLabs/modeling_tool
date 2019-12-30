import threading
import struct
import queue
import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream


class MappedMessage:
    def __init__(self, counter: int, key: bytes, body: bytes):
        assert isinstance(key, bytes)
        assert isinstance(body, bytes) or body is None
        assert isinstance(counter, int) 
        
        self._key = key
        self._body = body
        self._counter = counter

    @classmethod
    def recv(cls, socket, counter=None):
        key, b_counter, body = socket.recv_multipart()
        counter = counter or struct.unpack('!q', b_counter)[0]
        return cls(counter, key=key, body=body)

    @classmethod
    def from_raw_message(cls, raw_message, counter=None):
        key, b_counter, body = raw_message
        counter = counter if counter is not None else struct.unpack('!q', b_counter)[0]
        return cls(counter, key, body)

    def send(self, socket):
        key = self._key or b''
        body = self._body or b''
        counter = self._counter
        b_counter = struct.pack('!q', counter)
        socket.send_multipart([key, b_counter, body])

    @property
    def counter(self):
        return self._counter

    @property
    def key(self):
        return self._key
    
    @property
    def body(self):
        return self._body
    
    def store(self, target):
        target[self._key] = self

    def __repr__(self):
        return f"key: {self._key}, seq: {self._counter}, body: {self._body}"

    
class MapServer:
    def __init__(self, router_port, pub_port, pull_port):
        self.state = {}
        self.counter = 0
        
        self.ctx = zmq.Context()
        self.loop = IOLoop.instance()

        self.snapshot = self.ctx.socket(zmq.ROUTER)
        self.publisher = self.ctx.socket(zmq.PUB)
        self.collector = self.ctx.socket(zmq.PULL)
        
        self.snapshot.bind("tcp://*:%d" % router_port)
        self.publisher.bind("tcp://*:%d" % pub_port)
        self.collector.bind("tcp://*:%d" % pull_port)

        # Wrap sockets in ZMQStreams for IOLoop handlers (in this context?)
        self.snapshot = ZMQStream(self.snapshot)
        self.publisher = ZMQStream(self.publisher)
        self.collector = ZMQStream(self.collector)

        # Register our handlers with reactor
        self.snapshot.on_recv(self.handle_snapshot)
        self.collector.on_recv(self.handle_collect)

    def start(self):
        try:
            self.loop.start()
        except KeyboardInterrupt:
            pass        

    def handle_snapshot(self, raw_message):
        identity, request = raw_message

        if request == b'get-snapshot':
            for key, message in self.state.items():
                self.snapshot.send(identity, zmq.SNDMORE)
                message.send(self.snapshot)

            self.snapshot.send(identity, zmq.SNDMORE)
            message = MappedMessage(-1, b'get-snapshot-end', None)
            message.send(self.snapshot)                

    def handle_collect(self, raw_message):
        # pull update and then publish it
        message = MappedMessage.from_raw_message(raw_message, self.counter)
        self.counter += 1
        
        message.send(self.publisher)
        message.store(self.state)


class MapClient:
    POLL_INTERVAL = 1 # [ms]
    
    def __init__(self, dealer_addr, sub_addr, push_addr, queue=None):
        self._queue = queue
        self._messages = {}
        self._counter = 0
        self._lock = threading.RLock()
        
        ctx = zmq.Context()
        self.snapshot = self._init_socket(ctx, zmq.DEALER, dealer_addr)
        self.subscriber = self._init_socket(ctx, zmq.SUB, sub_addr, [(zmq.SUBSCRIBE, '')])
        self.publisher = self._init_socket(ctx, zmq.PUSH, push_addr)        

    def _init_socket(self, ctx, zmq_type, address, opts=None):
        socket = ctx.socket(zmq_type)
        socket.linger = 0

        opts = opts or []
        for opt in opts:
            socket.setsockopt_string(opt[0], opt[1])

        socket.connect(address)
        return socket    

    def start(self):
        self.snapshot.send_string("get-snapshot")

        while True:
            message = Message.recv(self.snapshot)
            print(message.key, message.body, message.counter)
            if message.key == b"get-snapshot-end":
                break
            else:
                self._store_message(message)
            
        poller = zmq.Poller()
        poller.register(self.subscriber, zmq.POLLIN)
        
        while True:
            items = dict(poller.poll(timeout=self.POLL_INTERVAL))

            if self.subscriber in items:
                message = Message.recv(self.subscriber)
                self._store_message(message)
                
            if self._queue is not None and self._queue.qsize() > 0:
                key, value = q.get()
                message = MappedMessage(-1, key, value)
                message.send(self.publisher)
            #else:
            #    from pprint import pprint
            #    pprint(self._messages)
                
    def _store_message(self, message):
        with self._lock:
            if message.counter == self._counter:
                self._counter += 1
                self._messages[message.key] = message
            else:
                raise RuntimeError(f"Expected counter value {self._counter}, "
                                   f"but received message with value {message.counter}")
                
    @property
    def messages(self):
        with self._lock:
            messages = self._messages.copy()
        return messages



