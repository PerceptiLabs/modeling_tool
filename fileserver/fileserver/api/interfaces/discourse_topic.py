import requests, os

# discourse direct interaction here
class CreateDiscourseAPI():
    def __init__(self, api_username, api_key, timeout=None):
        
        self.api_username = api_username
        self.api_key = api_key

    def create_post(
        self, title, content, tags=[]):
    
        url = "https://forum.perceptilabs.com/posts"
        data={'title': title,
        'category': 5, # change this number if we add more categories
        'raw': content} # can add a check to test body is 20 letters or more
        headers = {
        'Content-Type': 'multipart/form-data;',
        'api-key': self.api_key,
        'api-username': self.api_username
        }

        response = requests.request("POST", url, headers=headers, data=data)

        return(response["topic_id"],response["topic_slug"])


    def upload_image(self, image_path):

        url = "https://forum.perceptilabs.com/uploads"

        payload={'type': 'upload',
        'synchronous': 'true'}
        files=[
        ('files[]',(os.path.basename(image_path) ,open(image_path,'rb'),'image/png'))
        ]
        headers = {
        'api-key': self.api_key,
        'api-username': self.api_username
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        return(response)