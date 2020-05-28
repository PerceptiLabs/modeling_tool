import logging
import os

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
