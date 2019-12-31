import zmq
import copy
import queue
import struct
import threading
import collections
from typing import Dict
from abc import ABC, abstractmethod


def int2bytes(x: int):
    return struct.pack('!q', x)


def bytes2int(x: bytes):
    return struct.unpack('!q', x)[0]    


MappedMessage = collections.namedtuple(
    'MappedMessage',
    ['index', 'key', 'body']
)


class MapBase(ABC):
    def _reset(self):
        self._worker = None        
        self._lock = threading.RLock()
        self._messages = {}
        self._index = 0
        self._is_running = threading.Event()
        self._is_running.clear()

    @abstractmethod
    def _worker_func(self):
        raise NotImplementedError
                
    def start(self):
        self._is_running.set()        
        self._worker = threading.Thread(target=self._worker_func, daemon=True)
        self._worker.start()

    def stop(self):
        if self._is_running.is_set():
            self._is_running.clear()                        
            self._worker.join()
        self._reset()
    

class MapServer(MapBase):
    POLL_INTERVAL = 1 # [ms]
    
    def __init__(self, router_addr: str, pub_addr: str, pull_addr: str):
        self._reset()
        self._router_addr = router_addr
        self._pub_addr = pub_addr
        self._pull_addr = pull_addr
        
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

        while self._is_running.is_set():
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
        op, _, key, body = collector_socket.recv_multipart()
        op_str = op.decode('utf-8')
        
        with self._lock:
            index = self._index
            publisher_socket.send_multipart([op, int2bytes(index), key, body])

            if op_str == 'update-set':
                self._messages[key] = MappedMessage(index, key, body)
            elif op_str == 'update-del':
                del self._messages[key]
            else:
                raise RuntimeError(f"Unknown operation {op_str}")
            
            self._index += 1

            
class MapClient(MapBase):
    POLL_INTERVAL = 1 # [ms]
    
    def __init__(self, dealer_addr: str, sub_addr: str, push_addr: str):
        self._reset()
        self._dealer_addr = dealer_addr
        self._sub_addr = sub_addr
        self._push_addr = push_addr
        
    def _worker_func(self):
        ctx = zmq.Context()
        snapshot_socket = self._init_socket(ctx, zmq.DEALER, self._dealer_addr)
        subscriber_socket = self._init_socket(ctx, zmq.SUB, self._sub_addr, [(zmq.SUBSCRIBE, '')])
        publisher_socket = self._init_socket(ctx, zmq.PUSH, self._push_addr)        

        self._get_snapshot(snapshot_socket)
        
        if not self._is_running.is_set():
            return

        self._get_and_send_updates(subscriber_socket, publisher_socket)

    def _get_and_send_updates(self, subscriber_socket, publisher_socket):
        poller = zmq.Poller()
        poller.register(subscriber_socket, zmq.POLLIN)
        
        while self._is_running.is_set():
            items = dict(poller.poll(timeout=self.POLL_INTERVAL))

            if subscriber_socket in items:
                op, index, key, body = subscriber_socket.recv_multipart()
                op = op.decode('utf-8')
                index = bytes2int(index)
                
                with self._lock:
                    if self._index != index:
                        raise RuntimeError(f"Unexpected index. Expected {self._index} but got {index}!")
                    if op == 'update-set':
                        self._messages[key] = MappedMessage(index, key, body)
                    elif op == 'update-del':
                        del self._messages[key]
                    else:
                        raise RuntimeError(f"Unknown operation {op_str}")                        
                        
                    self._index += 1
                    
            if self._queue.qsize() > 0:
                op, key, body = self._queue.get()
                assert op in ['update-set', 'update-del']
                publisher_socket.send_multipart([op.encode(), int2bytes(-1), key, body])

    def _get_snapshot(self, snapshot_socket):
        snapshot_socket.send_string('snapshot-get')
        
        new_messages = []
        while self._is_running.is_set():
            op, index, key, body = snapshot_socket.recv_multipart()
            op = op.decode('utf-8')            
            index = bytes2int(index)
            
            if op == 'snapshot-set':
                message = MappedMessage(index, key, body)
                new_messages.append(message)
            elif op == 'snapshot-end':
                break
            else:
                raise ValueError(f"Unknown operation '{op}' received over snapshot socket")
            
        with self._lock:
            for message in new_messages:
                self._messages[message.key] = message
                self._index = max(self._index, message.index)

    def _init_socket(self, ctx, zmq_type, address, options=None):
        socket = ctx.socket(zmq_type)
        socket.linger = 0

        options = options or []
        for opt in options:
            socket.setsockopt_string(opt[0], opt[1])

        socket.connect(address)
        return socket

    def _reset(self):
        super()._reset()
        self._queue = queue.Queue()
                
    @property
    def messages(self) -> Dict[str, bytes]:
        with self._lock:
            # Since bytes (and strings) are immutable, a shallow copy is enough.            
            messages = self._messages.copy()
        return messages

    def put(self, operation: str, key: bytes, value: bytes=None) -> None:
        if operation == 'update-del':
            value = b''
        if not isinstance(operation, str):
            raise TypeError("Operation must be of type 'str'")
        if not isinstance(key, bytes):
            raise TypeError("Key must be of type 'bytes'")
        if not isinstance(value, bytes):
            raise TypeError("Value must be of type 'bytes'")

        self._queue.put((operation, key, value))

        
class ByteMap(collections.MutableMapping):
    def __init__(self, client: MapClient):
        self._client = client

    def keys(self):
        return self._client.messages.keys()
    
    def items(self):
        return self._client.messages.items()
    
    def values(self):
        return self._client.messages.values()

    def __contains__(self, key):
        return key in self._client.messages
    
    def __getitem__(self, key):
        return self._client.messages[key]

    def __setitem__(self, key, value):
        return self._client.put('update-set', key, value)

    def __delitem__(self, key):
        return self._client.put('update-del', key)

    def __iter__(self):
        return iter(self._client.messages)

    def __len__(self):
        return len(self._client.messages)

    def __keytransform__(self, key):
        raise key
    
