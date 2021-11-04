import json
import pprint
import logging
import threading
import redis
from abc import abstractmethod, ABC
from urllib.parse import urlparse
from queue import Queue
from contextlib import contextmanager

from perceptilabs.logconf import APPLICATION_LOGGER
import perceptilabs.settings as settings


logger = logging.getLogger(APPLICATION_LOGGER)


class BaseBroker(ABC):
    def __init__(self):
        self._queues = set()

    @contextmanager
    def subscription(self):
        queue = Queue()
        self._queues.add(queue)
        
        yield queue
        
        self._queues.remove(queue)

    @abstractmethod
    def publish(self, message):
        raise NotImplementedError

    def _broadcast_internal(self, message):
        for queue in self._queues:
            queue.put_nowait(message)
    

class QueueBroker(BaseBroker):
    def publish(self, message):
        self._broadcast_internal(message)


REDIS_DEFAULT_PORT = 6379


class RedisBroker(BaseBroker):
    CHANNEL = 'rendering-to-trainer'
    
    def __init__(self, redis_url):
        super().__init__()
        
        parsed = urlparse(redis_url)
        host = parsed.hostname
        port = parsed.port if parsed.port is not None else REDIS_DEFAULT_PORT

        self._conn = redis.Redis(host=host, port=port)
        
        thread = threading.Thread(target=self._worker, daemon=True)
        thread.start()

    def _worker(self):
        pubsub = self._conn.pubsub()
        pubsub.subscribe(self.CHANNEL)

        for raw_message in pubsub.listen():
            if raw_message.get('type') != 'message':  # Only handle messages
                continue

            try:
                data = raw_message['data'].decode()
                message = json.loads(data)
            except:
                logger.exception(
                    "Exception in Redis broker. Raw message: " + pprint.pformat(raw_message))
            else:
                self._broadcast_internal(message)

    def publish(self, message):
        self._conn.publish(self.CHANNEL, json.dumps(message))        


global _MESSAGE_BROKER
_MESSAGE_BROKER = None


def get_message_broker():
    global _MESSAGE_BROKER

    if not _MESSAGE_BROKER:
        redis_url = settings.PUBSUB_REDIS_URL
    
        if redis_url is not None:
            _MESSAGE_BROKER = RedisBroker(redis_url)
        else:
            _MESSAGE_BROKER = QueueBroker()
            
        logger.info(f"Created {type(_MESSAGE_BROKER)} for rendering <-> training messaging...")

    return _MESSAGE_BROKER

