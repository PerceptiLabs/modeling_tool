import os
import shutil
import logging
import tempfile

log = logging.getLogger(__name__)

class DataBundle:
    def __init__(self):
        self._path = tempfile.mkdtemp(prefix='bundle_')

    def compress(self, output_path):
        files = os.listdir(self._path)
        if len(files) == 0:
            log.debug("No files to compress.")
        else:
            log.debug("Compressing files: {}" \
                      .format(", ".join(os.listdir(self._path))))
            
        shutil.make_archive(output_path, 'zip', self._path)
    
    def clear(self):
        shutil.rmtree(self._path)
        
    @property
    def path(self):
        return self._path

    def upload(self):
        self.compress('bundle') # TODO: should go to azure, but just zip for now.
        
        '''
        from azure.storage.blob import BlockBlobService
        from azure.storage.blob import ContentSettings

        block_blob_service = BlockBlobService(account_name='<myaccount>', account_key='mykey')
        block_blob_service.create_container('mycontainer')
        
        block_blob_service.create_blob_from_path(
            'mycontainer',
            'myblockblob.zip', # create unique name
            self._path,
            content_settings=ContentSettings(content_type='application/zip')
        )
        '''

    def upload_and_clear(self):
        try:
            self.upload()
        finally:
            self.clear()
