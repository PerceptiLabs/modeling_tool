import zmq
import time
import logging
import threading
import collections
from typing import List
from abc import ABC, abstractmethod


log = logging.getLogger(__name__)


PORT_PRODUCER = 5566 # Producer facing port.  
PORT_CONSUMER = 5577 # Consumer facing port.


class TcpAddressResolver:
    def __init__(self, port_producer, port_consumer):
        self._port_producer = port_producer
        self._port_consumer = port_consumer
    
    def get_upstream(self, binding_address=False):
        if binding_address:
            return f'tcp://*:{self._port_producer}'
        else:
            return f'tcp://localhost:{self._port_producer}'            

    def get_downstream(self, binding_address=False):
        if binding_address:
            return f'tcp://*:{self._port_consumer}'
        else:
            return f'tcp://localhost:{self._port_consumer}'        
    

class IpcAddressResolver:
    def get_upstream(self, binding_address=False):
        return 'ipc://upstream'

    def get_downstream(self, binding_address=False):
        return 'ipc://downstream'
    
        
class MessageBus:
    POLL_TIMEOUT = 1.0 # msec
    
    def __init__(self, address_resolver=None):
        self._address_resolver = address_resolver or IpcAddressResolver()
        
        self._running = threading.Event()
        self._ctx = zmq.Context.instance()

    def _proxy(self):
        zsock_sub = self._ctx.socket(zmq.SUB) # Subscribe to producers.
        zsock_sub.linger = 0
        zsock_sub.bind(self._address_resolver.get_upstream(binding_address=True)) 
        zsock_sub.setsockopt(zmq.SUBSCRIBE, b'') # Subscribe to every topic

        zsock_pub = self._ctx.socket(zmq.XPUB) # Publish to consumers.
        zsock_pub.bind(self._address_resolver.get_downstream(binding_address=True))

        poller = zmq.Poller()
        poller.register(zsock_sub, zmq.POLLIN)

        deque = collections.deque()
        counter = 0
        
        while self._running.is_set():
            items = dict(poller.poll(timeout=self.POLL_TIMEOUT))

            t = time.time()
            if zsock_sub in items:
                # Read from producers, forward to consumers.
                topic, message = zsock_sub.recv_multipart()
                zsock_pub.send_multipart([topic, message])

                deque.append((t, len(message)))


            # Compute throughput
            if counter % (1000 / self.POLL_TIMEOUT) == 0:
                tot_sz = 0
                t_wnd = 5 # seconds
                i = 0
                while i < len(deque):
                    t0, sz = deque[i]

                    if t - t0 > t_wnd:
                        deque.popleft()
                    else:
                        tot_sz += sz
                        i += 1

                throughput = tot_sz / t_wnd / 1000
                log.info(f"Proxy throughput: {throughput} kb/s")                
            counter += 1
            
                
                
        zsock_sub.close()
        zsock_pub.close()

    def start(self):
        if not self._running.is_set():
            self._running.set()
            self._proxy_thread = threading.Thread(target=self._proxy)
            self._proxy_thread.start()
        
    def stop(self):
        if self._running.is_set():        
            self._running.clear()
            self._proxy_thread.join()


class MessageProducer:
    def __init__(self, topic, address_resolver=None):
        self._address_resolver = address_resolver or IpcAddressResolver()
        
        ctx = zmq.Context.instance()
        self._zsock = ctx.socket(zmq.PUB)
        self._topic = topic
        
    def start(self):        
        self._zsock.connect(self._address_resolver.get_upstream())
        time.sleep(0.1) # Messages can be dropped if sent too soon after connect. ZMQ flaw.

    def stop(self):
        self._zsock.close()

    def send(self, message):
        try:
            self._zsock.send_multipart([self._topic, message])
        except zmq.error.ContextTerminated as e:
            print("MessageProducer " + repr(e))
            

class MessageConsumer:
    def __init__(self, topics, address_resolver=None):
        self._address_resolver = address_resolver or IpcAddressResolver()
        
        ctx = zmq.Context.instance()        
        self._zsock = ctx.socket(zmq.SUB)
        
        for topic in topics:
            self._zsock.setsockopt(zmq.SUBSCRIBE, topic)
            
        self._poller = zmq.Poller()
        self._poller.register(self._zsock, zmq.POLLIN)

    def start(self):
        self._zsock.connect(self._address_resolver.get_downstream())
        time.sleep(0.1)

    def stop(self):
        self._zsock.close()

    def get_messages(self, per_message_timeout=0.1):
        messages = []        
        try:
            per_message_timeout *= 1000 # convert to msec
            items = dict(self._poller.poll(timeout=per_message_timeout))
            while self._zsock in items:
                topic, message = self._zsock.recv_multipart()
                messages.append(message)
                items = dict(self._poller.poll(timeout=per_message_timeout))
        except zmq.error.ContextTerminated as e:
            print("MessageConsumer " + repr(e))            
        finally:
            return messages
            

_event_bus = None

def get_message_bus():
    global _event_bus
    if _event_bus is None:
        _event_bus = MessageBus()
    return _event_bus
    


if __name__ == "__main__":
    import time
    
    bus = get_message_bus()
    bus.start()
    time.sleep(1)

    c = MessageConsumer([b'some-topic'])
    c.start()
    
    p = MessageProducer(b'some-topic')
    p.start()
    p.send(b'hello')


    time.sleep(2)

    print('REEECV',c.get_messages())

    p.stop()
    c.stop()    

    
    bus.stop()
