import os
import boto3
import tempfile

import logging
log = logging.getLogger(__name__)

class S3BucketAdapter:
    def __init__(self, bucket: str, region_name=None,
                 aws_access_key_id: str=None, aws_secret_access_key: str=None):
        log.warning("No AWS access credentials provided. This may lead to system wide credentials being used")
        
        self._bucket = bucket
        self._temp_files = []
        
        self._conn = boto3.client('s3', region_name=region_name,
                                  aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key)

    def get_keys(self, delimiter: str='', prefix: str=''):
        response = self._conn.list_objects(Bucket=self._bucket,
                                           Delimiter=delimiter,
                                           Prefix=prefix)
        contents = response.get('Contents', [])
        keys = [c['Key'] for c in contents]
        return keys

    def download_file(self, key: str, target_path: str=None):
        if target_path is None:
            _, ext = os.path.splitext(key)
            f = tempfile.NamedTemporaryFile(mode='wb', suffix=ext, delete=False)
            self._temp_files.append(f.name)                        
            self._conn.download_fileobj(self._bucket, key, f)
            f.close()
            return f.name
        else:    
            self._conn.download_file(self._bucket, key, target_path)
            return target_path

    def __enter__(self):
        return self
 
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):        
        for path in self._temp_files:
            if not os.path.isfile(path):
                continue
            os.remove(path)

    


if __name__ == "__main__":
    id_ = None
    secret = None
    #id_ = "AKIAZYLA7ETUIOS73NHX"
    #secret = "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"
    bucket = "perceptitest"

    adapter = S3BucketAdapter(bucket, None, id_, secret)
    print(adapter.get_keys())

    
