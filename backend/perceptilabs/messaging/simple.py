from queue import Queue, Empty

from perceptilabs.messaging import MessageBus, MessageProducer, MessageConsumer, MessagingFactory


class SimpleMessageProducer(MessageProducer):
    def __init__(self, topic, queues):
        self._topic = topic
        self._queues = queues

    def send(self, message):
        for queue in self._queues:
            queue.put((self._topic, message))        

    def start(self):
        pass

    def stop(self):
        pass


class SimpleMessageConsumer(MessageConsumer):
    def __init__(self, topics, queue):
        self._topics = topics
        self._queue = queue
    
    def get_messages(self, per_message_timeout=0.1):
        messages = []

        while not self._queue.empty():
            try:
                topic, message = self._queue.get(timeout=per_message_timeout)
            except Empty:
                pass
            else:
                if topic in self._topics:
                    messages.append(message)
        return messages

    def start(self):
        pass

    def stop(self):
        pass


_consumer_queues = []
    
class SimpleMessagingFactory(MessagingFactory):
    def make_producer(self, topic, address_resolver=None):
        global _consumer_queues
        return SimpleMessageProducer(topic, _consumer_queues)

    def make_consumer(self, topics, address_resolver=None):
        queue = Queue()

        global _consumer_queues
        _consumer_queues.append(queue)
        return SimpleMessageConsumer(topics, queue)
        

