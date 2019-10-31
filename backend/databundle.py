import os
import time
import uuid
import shutil
import logging
import tempfile

from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings

log = logging.getLogger(__name__)

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

    
class DataBundle:
    def __init__(self, uploaders=None):
        self._contents_path = tempfile.mkdtemp(prefix='bundle_contents_')
        self._archives_path = tempfile.mkdtemp(prefix='bundle_archives_')                
        self._uploaders = uploaders or []

    def compress(self):
        files = os.listdir(self._contents_path)
        if len(files) == 0:
            log.info("No files to compress.")
            return None
        else:
            log.info("Compressing files: {}".format(", ".join(files)))

            zip_name = "{}_{}".format(int(time.time()), uuid.uuid4().hex)        
            path_no_ext = os.path.join(self._archives_path, zip_name)
            full_path = path_no_ext + '.zip'

            print(full_path)
            
            shutil.make_archive(path_no_ext, 'zip', root_dir=self._contents_path, logger=log)
            shutil.copyfile(full_path, 'bundle.zip') # TODO: only in debug mode??
            return full_path
        
    def clear(self):
        shutil.rmtree(self._contents_path)
        shutil.rmtree(self._archives_path)        
        
    @property
    def path(self):
        return self._contents_path

    def upload(self, path):
        n_uploaders = len(self._uploaders)

        if n_uploaders == 0:
            log.info("No uploaders to run.")            
            return
        
        succeeded = 0        
        for counter, uploader in enumerate(self._uploaders, 1):
            log.info("Running uploader {}/{} [{}]".format(counter, n_uploaders, repr(uploader)))
            try:
                uploader.upload(path)
            except:
                log.exception("Uploader {} failed. ".format(counter))
            else:
                succeeded += 1

        if succeeded > 0:
            log.info("{}/{} uploaders ran without error.".format(succeeded, n_uploaders))
        else:
            log.error("All data bundle uploaders failed!")            

    def upload_and_clear(self):
        try:
            archive_path = self.compress()
            
            if archive_path is not None:
                self.upload(archive_path)
        except:
            log.exception("Error in upload and clear")
        finally:
            self.clear()
