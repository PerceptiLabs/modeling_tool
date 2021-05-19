import logging
import os
from concurrent.futures import ThreadPoolExecutor

from azure.eventhub import EventData, EventHubProducerClient
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings

from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


AZURE_ACCOUNT_NAME_EU = 'uantumetdisks'
AZURE_ACCOUNT_KEY_EU  = 'CPPtripRA5mLz+LxyssWqeeg8HLKUhPH+8RZ2va4BfDCMy5yx6FrLpK2MqrhAkdUGwuopmpalcW3EVT7du8JHw=='
AZURE_CONTAINER_EU    = 'users'
AZURE_CONNSTR_EU      = 'DefaultEndpointsProtocol=https;AccountName=uantumetdisks;AccountKey=CPPtripRA5mLz+LxyssWqeeg8HLKUhPH+8RZ2va4BfDCMy5yx6FrLpK2MqrhAkdUGwuopmpalcW3EVT7du8JHw==;EndpointSuffix=core.windows.net'
    
AZURE_ACCOUNT_NAME_US = 'quantumnetamerica'
AZURE_ACCOUNT_KEY_US  = 'EAzrkBUJocKcbKD5RgHRZekT/tIVdwWsAS4yhq5BENKaICh4x2LDvbV98q/swUbvevSgZwRwcPCDy4JfaN08DQ=='
AZURE_CONTAINER_US    = 'users'
AZURE_CONNSTR_US     = 'DefaultEndpointsProtocol=https;AccountName=quantumnetamerica;AccountKey=EAzrkBUJocKcbKD5RgHRZekT/tIVdwWsAS4yhq5BENKaICh4x2LDvbV98q/swUbvevSgZwRwcPCDy4JfaN08DQ==;EndpointSuffix=core.windows.net'

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
    def __init__(self, conn_str, container_name):
        """ 
            Uploads files to Azure blob storage.
   
            conn_str: an Azure blob container connection string
            container_name: blob container name
        """
        self._conn_str = conn_str
        self._container = container_name

    def upload(self, file_path):
        """ Uploads a local file to Azure """
        file_name = os.path.basename(file_path)
        
        blob_service_client = BlobServiceClient.from_connection_string(self._conn_str)
        blob_client = blob_service_client.get_blob_client(
            container=self._container,
            blob=file_name
        )
        with open(file_path, "rb") as data:
            blob_client.upload_blob(
                data,
                content_settings=ContentSettings(content_type='application/zip')                
            )
        
    def __repr__(self):
        return self.__class__.__name__ + ":" + self._container
