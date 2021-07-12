import logging
import os
from concurrent.futures import ThreadPoolExecutor

from azure.eventhub import EventData, EventHubProducerClient
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings

from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


AZURE_CONTAINER_EU    = 'users'
AZURE_WRITEONLY_URL_EU = 'https://uantumetdisks.blob.core.windows.net/users?sp=w&st=2021-07-09T15:48:18Z&se=2023-07-09T23:48:18Z&spr=https&sv=2020-08-04&sr=c&sig=o4hm78V4MOpD%2Bfi4EQGp%2BC4T0sDcB3RZlWH6jTbx6cs%3D'

AZURE_CONTAINER_US    = 'users'
AZURE_WRITEONLY_URL_US = 'https://quantumnetamerica.blob.core.windows.net/users?sp=w&st=2021-07-09T15:05:10Z&se=2023-07-09T23:05:10Z&spr=https&sv=2020-08-04&sr=c&sig=L5pV9C1HN7r2HYbI%2BnSQbnWbP%2Bs%2F4OatO58kwGbDCSg%3D'


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
    def __init__(self, writeonly_url, container_name):
        """
            Uploads files to Azure blob storage.

            writeonly_url: an Azure blob container SAS url
            container_name: blob container name
        """

        # disallow uploading to anything but write-only urls
        if not 'sp=w&' in writeonly_url:
            print("Integration error: attempt to upload to readable url")
            exit()

        self._writeonly_url = writeonly_url
        self._container = container_name

    def upload_file(self, file_path):
        """ Uploads a local file to Azure """
        try:
            file_name = os.path.basename(file_path)

            blob_service_client = BlobServiceClient(self._writeonly_url)
            blob_client = blob_service_client.get_blob_client(
                container=self._container,
                blob=file_name
            )
            with open(file_path, "rb") as data:
                blob_client.upload_blob(
                    data,
                    content_settings=ContentSettings(content_type='application/zip')
                )

            logger.info(f"Uploaded logs: {file_path}")

        except:
            # This is for uploading logs. We don't want to crash on the user if we can't upload
            logger.error(f"Couldn't upload {file_path}")

    def __repr__(self):
        return self.__class__.__name__ + ":" + self._container

    @classmethod
    def get_defaults(cls):
        return [
            AzureUploader(AZURE_WRITEONLY_URL_EU, AZURE_CONTAINER_EU),
            AzureUploader(AZURE_WRITEONLY_URL_US, AZURE_CONTAINER_US)
        ]

    @classmethod
    def upload(cls, zip_full_path):
        for uploader in cls.get_defaults():
            uploader.upload_file(zip_full_path)
