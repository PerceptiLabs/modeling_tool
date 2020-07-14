import tensorflow as tf
import numpy as np
import random
import logging
from datetime import datetime

from perceptilabs.core_new.serialization import serialize, can_serialize, deserialize
from perceptilabs.messaging import MessagingFactory, MessageProducer
from perceptilabs.messaging.zmq_wrapper import ZmqMessagingFactory, ZmqMessageProducer
from perceptilabs.messaging.simple import SimpleMessageProducer
from perceptilabs.logconf import APPLICATION_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)

class Experiment:
    def __init__(self, experiment_name: str = None, producer: SimpleMessageProducer = None):
        '''Initializes Experiment

        Args:
            experiment_name: Name of experiment. If empty, will use datetime format as default.
            producer: ZMQ Messaging producer to be provided during testing
        '''
        self.experiment_name = experiment_name or 'Experiment-' + datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

        if not producer:
            self._messaging_factory = ZmqMessagingFactory()
            self._producer = self._create_producer()
            self._producer.start()
        else:
            self._producer = producer

    def _create_producer(self) -> ZmqMessageProducer:
        '''Creates zmq producer to send messages

        Returns:
            producer: A producer object to publish messages to topic
        '''
        topic_generic = f'generic-experiment'.encode()

        producer = self._messaging_factory.make_producer(topic_generic)
        logger.info(f"Instantiated message producer/consumer pairs for topics {topic_generic} for experiment {self.experiment_name}")

        return producer

    def _process_outgoing_message(self, producer: MessageProducer, message: dict):
        '''Processes experiment message to be sent
        
        Args:
            producer: A producer object to publish messages
            message: a dictionary formatted message to be sent
        '''
        message = serialize(message)
        producer.send(message)

    def log_hyperparameters(self, hyper_params: dict):
        '''Logs the hyperparameters of the experiment

        Args:
            hyper_params: hyperparameters of experiment
        '''
        message = {
            'experiment_name': self.experiment_name,
            'category': 'Hyperparameters',
            'hyper_params': hyper_params
        }

        self._process_outgoing_message(self._producer, message)

    def log_metric(self, name: str, metric: float, step: int = None):
        '''Logs the name and the corresponding value of the metric with the correct
           corresponding time value

        Args:
            name: name of the metric
            metric: value of the metric
            step: current step iteration of metric
        '''
        message = {
            'experiment_name': self.experiment_name,
            'category': 'Metrics',
            'name': name,
            'metric': metric,
            'step': step
        }

        self._process_outgoing_message(self._producer, message)
