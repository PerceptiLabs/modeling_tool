from abc import ABC, abstractmethod


class MessageBus(ABC):
    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod    
    def stop(self):
        raise NotImplementedError        
    

class MessageProducer(ABC):
    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod    
    def stop(self):
        raise NotImplementedError        
    
    @abstractmethod    
    def send(self, message):
        raise NotImplementedError        
    

class MessageConsumer(ABC):
    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod    
    def stop(self):
        raise NotImplementedError        
    
    @abstractmethod    
    def get_messages(self, per_message_timeout=0.1):
        raise NotImplementedError        
    
    
class MessagingFactory(ABC):
    def make_producer(self, topic, address_resolver=None):
        raise NotImplementedError

    def make_producer(self, topics, address_resolver=None):
        raise NotImplementedError        
