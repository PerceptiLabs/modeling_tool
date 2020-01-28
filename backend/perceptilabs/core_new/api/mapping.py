import zmq
import copy
import time
import uuid
import queue
import struct
import threading
import collections
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Tuple, Callable, List
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
        self._messages_received = 0
        self._messages_sent = 0
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

    @property
    def is_running(self):
        return self._is_running.is_set()
    
        
class MapServer(MapBase):
    POLL_INTERVAL = 0.1 # [ms]
    
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
        identity, request, subtree = snapshot_socket.recv_multipart()
        assert request == b'snapshot-get'
        
        with self._lock:
            for key, message in self._messages.items():
                if not key.startswith(subtree):
                    continue                
                
                snapshot_socket.send_multipart([
                    identity, b'snapshot-set',
                    int2bytes(message.index),
                    message.key, message.body
                ])
                self._messages_sent += 1                

            snapshot_socket.send_multipart([identity, b'snapshot-end', int2bytes(0), b'', b''])

            
    def _on_update(self, collector_socket, publisher_socket):
        key, op, _, body = collector_socket.recv_multipart()
        op_str = op.decode('utf-8')
        with self._lock:
            index = self._messages_received
            publisher_socket.send_multipart([key, op, int2bytes(index), body])
            self._messages_sent += 1
            
            if op_str == 'update-set':
                self._messages[key] = MappedMessage(index, key, body)
            elif op_str == 'update-del':
                if key in self._messages:
                    del self._messages[key]
            else:
                raise RuntimeError(f"Unknown operation {op_str}")
            
            self._messages_received += 1

            
class MapClient(MapBase):
    POLL_INTERVAL = 1 # [ms]
    
    def __init__(self, dealer_addr: str, sub_addr: str, push_addr: str, subtree: str='',
                 on_set: Callable=None, on_delete: Callable=None):
        self._reset()
        self._dealer_addr = dealer_addr
        self._sub_addr = sub_addr
        self._push_addr = push_addr
        self._subtree = subtree
        self.set_callbacks(on_set, on_delete)

    def set_callbacks(self, on_set: Callable=None, on_delete: Callable=None):
        self._on_set_callback = on_set
        self._on_del_callback = on_delete
        
        if (on_set is not None or on_delete is not None):
            self._callback_pool = ThreadPoolExecutor(1)
        else:
            self._callback_pool = None
            
    def _worker_func(self):
        ctx = zmq.Context()
        snapshot_socket = self._init_socket(ctx, zmq.DEALER, self._dealer_addr)
        subscriber_socket = self._init_socket(ctx, zmq.SUB, self._sub_addr, [(zmq.SUBSCRIBE, self._subtree)])
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
                key, op, index, body = subscriber_socket.recv_multipart()
                self._messages_received += 1                
                op = op.decode('utf-8')
                index = bytes2int(index)
                
                with self._lock:
                    if op == 'update-set':
                        message = MappedMessage(index, key, body)                        
                        self._messages[key] = message
                        self._on_set_message(message)
                    elif op == 'update-del':
                        if key in self._messages:
                            self._on_del_message(self._messages[key])
                            del self._messages[key]
                    else:
                        raise RuntimeError(f"Unknown operation {op}")                        
                    
            if self._queue.qsize() > 0:
                op, key, body = self._queue.get()
                assert op in ['update-set', 'update-del']
                publisher_socket.send_multipart([key, op.encode(), int2bytes(-1), body])
                self._messages_sent += 1

    def _get_snapshot(self, snapshot_socket):
        snapshot_socket.send_multipart([b'snapshot-get', self._subtree.encode()])
        
        poller = zmq.Poller()
        poller.register(snapshot_socket, zmq.POLLIN)
        
        new_messages = []
        while self._is_running.is_set():
            items = dict(poller.poll(timeout=self.POLL_INTERVAL))
            
            if snapshot_socket in items:
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
                self._messages_received += 1
                self._on_set_message(message)                

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
        self._messages_sent = 0
        self.set_callbacks(None, None)
                
    @property
    def mapping(self) -> Dict[bytes, bytes]:
        with self._lock:
            # Since bytes are immutable, a shallow copy is enough.
            mapping = {
                m.key.split(b' ')[1]: m.body for m in self._messages.values()
            }
        return mapping

    @property
    def sequence(self) -> Tuple[Tuple[bytes, bytes]]:
        with self._lock:
            sorted_messages = sorted(
                [x for x in self._messages.values()],
                key=lambda x: x.index
            )
            sequence = [
                (m.key.split(b' ')[1], m.body) for m in sorted_messages
            ]
        return sequence
        
    def put(self, operation: str, key: bytes, value: bytes=None) -> None:
        if ' ' in key.decode('utf-8'):
            raise ValueError("Keys cannot contain value \x20 (space)")
        
        if operation == 'update-del':
            value = b''
        if not isinstance(operation, str):
            raise TypeError("Operation must be of type 'str'")
        if not isinstance(key, bytes):
            raise TypeError("Key must be of type 'bytes'")
        if not isinstance(value, bytes):
            raise TypeError("Value must be of type 'bytes'")

        full_key = bytes(self._subtree + ' ', encoding='utf-8') + key
        self._queue.put((operation, full_key, value))

    def _on_set_message(self, message):
        if self._on_set_callback is not None:
            key = message.key.split(b' ')[1]
            self._callback_pool.submit(self._on_set_callback, key, message.index, message.body)

    def _on_del_message(self, message):
        if self._on_del_callback is not None:
            key = message.key.split(b' ')[1]
            self._callback_pool.submit(self._on_del_callback, key, message.index)

            
class ByteMap(collections.MutableMapping):
    def __init__(self, name: str, dealer_addr: str, sub_addr: str, push_addr: str):    
        self._client = MapClient(dealer_addr, sub_addr, push_addr, name)
        self._name = name

    def start(self):
        self._client.start()
        
    def stop(self):
        self._client.stop()

    @property
    def is_running(self):
        return self._client.is_running
        
    @property
    def name(self):
        return self._name

    def keys(self):
        return self._client.mapping.keys()
    
    def items(self):
        return self._client.mapping.items()
    
    def values(self):
        return self._client.mapping.values()

    def __contains__(self, key):
        return key in self._client.mapping
    
    def __getitem__(self, key):
        return self._client.mapping[key]

    def __setitem__(self, key, value):
        self._client.put('update-set', key, value)

    def __delitem__(self, key):
        self._client.put('update-del', key)

    def __iter__(self):
        return iter(self._client.mapping)

    def __len__(self):
        return len(self._client.mapping)

    def __keytransform__(self, key):
        raise key

    def __repr__(self):
        return '{}: {}'.format(self._name, repr(self._client.mapping))
    
    def __dict__(self):
        return self._client.mapping


class ByteSequence():
    def __init__(self, name: str, dealer_addr: str, sub_addr: str, push_addr: str):
        self._client = MapClient(dealer_addr, sub_addr, push_addr, name)
        self._name = name

    def start(self):
        self._client.start()
        
    def stop(self):
        self._client.stop()

    @property
    def is_running(self):
        return self._client.is_running
        
    @property
    def name(self):
        return self._name
    
    def append(self, value: bytes):
        self._client.put('update-set', uuid.uuid4().hex.encode(), value)

    def __getitem__(self, idx):
        return self._client.sequence[idx][1]

    def __setitem__(self, idx: int, value: bytes):
        # An update to an existing key will give it a new index. In order for this to work, the sequence cannot be created by sorting by index. Another metric is needed in MappedMessage
        raise NotImplementedError

    def __delitem__(self, idx: int):
        key = self._client.sequence[idx][0]
        self._client.put('update-del', key)

    def __iter__(self):
        for item in self._client.sequence:
            yield item[1]

    def __contains__(self, value: bytes):
        return value in iter(self)

    def __len__(self):
        return len(self._client.mapping)
            
    def __repr__(self):
        return '{}: {}'.format(self._name, repr(list(self)))


class EventBus:
    def __init__(self, name: str, dealer_addr: str, sub_addr: str, push_addr: str,
                 on_event: Callable=None):
        self._client = MapClient(dealer_addr, sub_addr, push_addr, name)
        self._client.set_callbacks(on_set=self._on_set_handler)
        self._name = name

    def set_on_event(self, on_event: Callable):
        self._on_event = on_event

    def start(self):
        self._client.start()
        
    def stop(self):
        self._client.stop()

    @property
    def is_running(self):
        return self._client.is_running
        
    @property
    def name(self):
        return self._name

    def post(self, value: bytes):
        self._client.put('update-set', uuid.uuid4().hex.encode(), value)        

    def _on_set_handler(self, key, index, value):
        if self._on_event is not None:
            self._on_event(value)
        self._client.put('update-del', key)        

    @property
    def pending_messages(self):
        return len(self._client.mapping)
    
