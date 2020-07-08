import logging
import os
from concurrent.futures import ThreadPoolExecutor

from azure.eventhub import EventData, EventHubProducerClient
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings

from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


AZURE_ACCOUNT_NAME_EU = 'uantumetdisks'
AZURE_ACCOUNT_KEY_EU  = '65rzvvM8RGmELHhQy3PrJdIQH1fQFH0J9CIdJd5U0zNMwz2V7ifhbJNtub/jLaN0P+3lsYWQQg4wjVsXi/1RWQ=='
AZURE_CONTAINER_EU    = 'users'
    
AZURE_ACCOUNT_NAME_US = 'quantumnetamerica'
AZURE_ACCOUNT_KEY_US  = 'QyCugvLSHZo/AMsevEgU1LVqGA5UX2b7PxpKmM3Uco50v+krDpRnEJ3vtkia77XgR9OAdTwYrYhLs+KZmzn7tQ=='
AZURE_CONTAINER_US    = 'users'

EVENTHUB_NAME = 'pipkernelkpi'
EVENTHUB_CONNECTION_STRING = 'Endpoint=sb://kernelstreams-ns.servicebus.windows.net/;SharedAccessKeyName=kernelStreamsSharedAccessKey;SharedAccessKey=N1rlZl+91nSiyD19GParplRI6jHECl/HB3PpE8gRRoU='


class AzureHandler(logging.Handler):
    def __init__(self, conn_str, eventhub_name, max_workers=1):
        super().__init__()
        self._max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

        try:
            self._producer = EventHubProducerClient.from_connection_string(
                conn_str=conn_str,
                eventhub_name=eventhub_name
            )
        except:
            logger.exception("Failed setting up Azure Event Hub Handler")
            self._producer = None

    def emit(self, record):
        #if self._producer is not None:
        message = self.format(record)

        if (self._max_workers == 0) or (self._max_workers is None):
            self._push_message(message)            
        else:
            future = self._executor.submit(self._push_message, message)
            future.add_done_callback(self._on_sent_message)

    def _push_message(self, message):
        batch = self._producer.create_batch()
        batch.add(EventData(message))
        self._producer.send_batch(batch)

    def _on_sent_message(self, future):
        exception = future.exception()
        if exception is not None:
            logger.warning("Azure handler raised exception " + repr(exception))
        else:
            logger.debug("Azure handler done!")
        
    @classmethod
    def get_default(cls):
        return cls(
            EVENTHUB_CONNECTION_STRING,
            EVENTHUB_NAME,
            max_workers=1
        )
    

class AzureUploader:
    def __init__(self, account_name, account_key, container_name):
        self._acc_name = account_name
        self._acc_key = account_key
        self._container = container_name

    def upload(self, file_path):
        block_blob_service = BlockBlobService(account_name=self._acc_name,
                                              account_key=self._acc_key)
        file_name = os.path.basename(file_path)
        
        block_blob_service.create_blob_from_path(
            self._container,
            file_name,
            file_path,            
            content_settings=ContentSettings(content_type='application/zip')
        )

    def __repr__(self):
        return self.__class__.__name__ + ":" + self._acc_name
