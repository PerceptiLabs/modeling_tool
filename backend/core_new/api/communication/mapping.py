import collections
import threading
import struct
import queue
import zmq
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream

def int2bytes(x):
    return struct.pack('!q', x)

def bytes2int(x):
    return struct.unpack('!q', x)[0]    

'''
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
        raw_message = socket.recv_multipart()
        return cls.from_raw_message(raw_message, counter)

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

    def __repr__(self):
        return f"key: {self._key}, seq: {self._counter}, body: {self._body}"
'''

MappedMessage = collections.namedtuple(
    'MappedMessage',
    ['index', 'key', 'body']
)

class MapServer:
    POLL_INTERVAL = 1
    
    def __init__(self, router_addr, pub_addr, pull_addr):
        self._reset()
        self._router_addr = router_addr
        self._pub_addr = pub_addr
        self._pull_addr = pull_addr
        
    def _reset(self):
        self._lock = threading.RLock()        
        self._queue = None        
        self._worker = None        
        self._stop_event = None 
        self._update_counter = 0
        self._messages = {}
        
    def _worker_func(self):
        ctx = zmq.Context()        
        snapshot_socket = ctx.socket(zmq.ROUTER)
        publisher_socket = ctx.socket(zmq.PUB)
        collector_socket = ctx.socket(zmq.PULL)
        
        snapshot_socket.bind(self._router_addr)
        publisher_socket.bind(self._pub_addr)
        collector_socket.bind(self._pull_addr)
        
        poller = zmq.Poller()
        poller.register(snapshot_socket, zmq.POLLIN)
        poller.register(collector_socket, zmq.POLLIN)        

        while not self._stop_event.is_set():
            items = dict(poller.poll(timeout=self.POLL_INTERVAL))
            
            if snapshot_socket in items:
                self._on_snapshot(snapshot_socket)
            if collector_socket in items:
                self._on_update(collector_socket, publisher_socket)        
                
    def _on_snapshot(self, snapshot_socket):
        identity, request = snapshot_socket.recv_multipart()
        assert request == b'snapshot-get'

        with self._lock:
            for key, message in self._messages.items():
                snapshot_socket.send_multipart([
                    identity, b'snapshot-set',
                    int2bytes(message.index),
                    message.key, message.body
                ])                

            snapshot_socket.send_multipart([identity, b'snapshot-end', int2bytes(0), b'', b''])
            
    def _on_update(self, collector_socket, publisher_socket):
        descr, _, key, body = collector_socket.recv_multipart()
        assert descr in [b'update-set']
        
        with self._lock:
            index = self._update_counter
            publisher_socket.send_multipart([descr, int2bytes(index), key, body])
            self._messages[key] = MappedMessage(index, key, body)
            self._update_counter += 1
            
    def start(self):
        self._stop_event = threading.Event()        
        
        self._worker = threading.Thread(target=self._worker_func, daemon=True)
        self._worker.start()

    def stop(self):
        if self._stop_event is not None:
            self._stop_event.set()
            self._worker.join()
        self._reset()

        
class MapClient:
    POLL_INTERVAL = 1 # [ms]
    
    def __init__(self, dealer_addr, sub_addr, push_addr):
        self._reset()
        self._dealer_addr = dealer_addr
        self._sub_addr = sub_addr
        self._push_addr = push_addr
        
    def _reset(self):
        self._lock = threading.RLock()                
        self._queue = queue.Queue()        
        self._worker = None        
        self._stop_event = None 
        self._index = 0
        self._messages = {}

    def _worker_func(self):
        ctx = zmq.Context()
        snapshot_socket = self._init_socket(ctx, zmq.DEALER, self._dealer_addr)
        subscriber_socket = self._init_socket(ctx, zmq.SUB, self._sub_addr, [(zmq.SUBSCRIBE, '')])
        publisher_socket = self._init_socket(ctx, zmq.PUSH, self._push_addr)        

        self._get_snapshot(snapshot_socket)
        
        if self._stop_event.is_set():
            return

        self._get_updates(subscriber_socket, publisher_socket)

    def _get_updates(self, subscriber_socket, publisher_socket):
        poller = zmq.Poller()
        poller.register(subscriber_socket, zmq.POLLIN)
        
        while not self._stop_event.is_set():
            items = dict(poller.poll(timeout=self.POLL_INTERVAL))

            if subscriber_socket in items:
                descr, index, key, body = subscriber_socket.recv_multipart()
                index = bytes2int(index)
                
                with self._lock:
                    if self._index != index:
                        raise RuntimeError(f"Unexpected index. Expected {self._index + 1} but got {index}!")
                    self._messages[key] = MappedMessage(index, key, body)                
                    self._index += 1
                    
            if self._queue is not None and self._queue.qsize() > 0:
                descr, key, body = self._queue.get()
                assert descr in [b'update-set']
                publisher_socket.send_multipart([descr, int2bytes(-1), key, body])

    def _get_snapshot(self, snapshot_socket):
        snapshot_socket.send_string('snapshot-get')
        
        new_messages = []
        while not self._stop_event.is_set():
            descr, index, key, body = snapshot_socket.recv_multipart()
            index = bytes2int(index)
            
            if descr == b'snapshot-set':
                message = MappedMessage(index, key, body)
                new_messages.append(message)
            elif descr == b'snapshot-end':
                break
            else:
                raise ValueError(f"Unknown descriptor {descr} received over snapshot socket")
            
        with self._lock:
            for message in new_messages:
                self._messages[message.key] = message
                self._index = max(self._index, message.index)

                
    def start(self):
        self._stop_event = threading.Event()                        
        self._worker = threading.Thread(target=self._worker_func, daemon=True)
        self._worker.start()

    def stop(self):
        if self._stop_event is not None:
            self._stop_event.set()
            self._worker.join()
        self._reset()

    def _init_socket(self, ctx, zmq_type, address, opts=None):
        socket = ctx.socket(zmq_type)
        socket.linger = 0

        opts = opts or []
        for opt in opts:
            socket.setsockopt_string(opt[0], opt[1])

        socket.connect(address)
        return socket    
                
    @property
    def messages(self):
        with self._lock:
            messages = self._messages.copy()
        return messages

    @property
    def queue(self):
        return self._queue


class ByteMapping(collections.MutableMapping):
    def __init__(self, client):
        self._client = client
    
    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __keytransform__(self, key):
        raise NotImplementedError
    
