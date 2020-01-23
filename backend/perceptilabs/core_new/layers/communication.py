from perceptilabs.core_new.api.mapping import ByteMap, EventBus, MapServer
import dill


class BaseClient:
    pass


class BaseServer:
    pass


class InProcessClient(BaseClient):
    def __init__(self, server):
        self._server = server
        self._events = []
        
    def add_event(self, topic, event):
        self._events.append((topic, event))

    def read(self, topic, key):
        self._server.get(topic, key)

    def commit(self):
        for topic, event in self._events:
            self._server.on_event(topic, event)
        self._events = []
        
    
class InProcessServer(BaseServer):
    def __init__(self, event_handlers):
        self._state = {}
        self._event_handlers = event_handlers

        self._tmp_state = {}
    
    def on_event(self, topic, event, *args, **kwargs):
        fn = self._event_handlers[f'{topic}-{event}']
        fn(*args, **kwargs)        

    def add_assign(self, topic, key, value):
        self._tmp_state[f'{topic}-{key}'] = value

    def read(self, topic, key):
        return self._state[f'{topic}-{key}']

    def commit(self):
        self._state.update(self._tmp_state)
        self._tmp_state = {}    

    
class ZmqClient(BaseClient):
    def __init__(self):
        self._mapping = ByteMap(
            'map',
            'tcp://localhost:5556',
            'tcp://localhost:5557',
            'tcp://localhost:5558'
        )

        self._bus = EventBus(
            'bus',
            'tcp://localhost:5556',
            'tcp://localhost:5557',
            'tcp://localhost:5558'
        )

        self._staged_events = []

    def start(self):
        self._mapping.start()
        self._bus.start()
        
    def stop(self):
        self._bus.stop()                
        self._mapping.stop()
        
    def add_event(self, topic, event):
        self._staged_events.append((topic, event))

    def read(self, topic, key):
        key = f'{topic}-{key}'
        b_key = key.encode('utf-8')
        b_val = self._mapping.get(b_key)

        if b_val is not None:
            value = dill.loads(b_val)
            return value
        else:
            return None        

    def commit(self):
        staged_events = self._staged_events.copy()
        self._staged_events = []
        for topic, event in staged_events:
            full_event = f'{topic}-{event}'
            b_event = full_event.encode('utf-8')
            self._bus.post(b_event)
            

class ZmqServer(BaseServer):
    def __init__(self, event_handlers):
        self._event_handlers = event_handlers
        self._staging = {}
        
        self._map_server = MapServer(
            'tcp://*:5556',
            'tcp://*:5557',
            'tcp://*:5558'
        )        
        
        self._mapping = ByteMap(
            'map',
            'tcp://localhost:5556',
            'tcp://localhost:5557',
            'tcp://localhost:5558'
        )

        self._bus = EventBus(
            'bus',
            'tcp://localhost:5556',
            'tcp://localhost:5557',
            'tcp://localhost:5558'
        )

        self._bus.set_on_event(self.on_event)

    def start(self):
        self._map_server.start()
        self._mapping.start()
        self._bus.start()

    def stop(self):
        self._bus.stop()                
        self._mapping.stop()
        self._map_server.stop()
        
    def on_event(self, b_event):
        event = b_event.decode('utf-8')
        fn = self._event_handlers[event]
        fn()        

    def add_assign(self, topic, key, value):
        self._staging[f'{topic}-{key}'] = value

    def read(self, topic, key):
        full_key = f'{topic}-{key}'
        b_key = key.encode('utf-8')
        value = dill.loads(self._mapping[b_key])
        return value

    def commit(self):
        staging = self._staging.copy()
        self._staging = {}

        for key, value in staging.items():
            b_key = key.encode('utf-8')
            b_val = dill.dumps(value)
            self._mapping[b_key] = b_val



        


