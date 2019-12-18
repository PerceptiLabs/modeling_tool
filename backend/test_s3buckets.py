'''
import pytest
import s3buckets

@pytest.fixture(autouse=True, scope="module")
def aws_credentials():
    """ Recommended for using moto-framework """
    import os    
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'               

    
class Test:
    def test_list_file_empty(self):    
        adapter = s3buckets.S3BucketAdapter(self.bucket)
        keys = adapter.get_keys()            
        assert keys == []            

    def test_list_file_exists(self):
        self.conn.upload_file(self.txt_file, self.bucket, 'test.txt')
        
        adapter = s3buckets.S3BucketAdapter(self.bucket)
        keys = adapter.get_keys()            
        assert keys == ['test.txt']

    def test_download_file_has_content(self):
        self.conn.upload_file(self.txt_file, self.bucket, 'test.txt')
        
        adapter = s3buckets.S3BucketAdapter(self.bucket)
        path = adapter.download_file('test.txt')
        
        with open(path, 'r') as f:
            content = f.read()
            assert content == self.txt_file_content
            
        adapter.close()

    def test_download_file_is_removed_after_close(self):
        import os        
        self.conn.upload_file(self.txt_file, self.bucket, 'test.txt')
        
        adapter = s3buckets.S3BucketAdapter(self.bucket)
        path = adapter.download_file('test.txt')

        assert os.path.isfile(path)
        adapter.close()
        assert not os.path.isfile(path)

    def test_incorrect_credentials(self):
        adapter = s3buckets.S3BucketAdapter(self.bucket,
                                            aws_access_key_id='hello',
                                            aws_secret_access_key='bye')


        print(adapter.get_keys())
        

    @pytest.fixture(autouse=True)
    def wrapper(self):
        import os
        import moto        
        import boto3
        import tempfile

        self.bucket = 'mybucket'
        self.txt_file_content = "Hello world!"
        
        with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8',
                                         suffix='.txt', delete=False) as f:
            f.write(self.txt_file_content)
            self.txt_file = f.name        

        with moto.mock_s3():
            self.conn = boto3.client('s3')
            self.conn.create_bucket(Bucket=self.bucket)
            
            yield # Test is called here
            
            os.remove(self.txt_file)

'''
