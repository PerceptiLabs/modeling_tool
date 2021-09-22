import requests

from rygg import settings

class GitHubService():

    def __init__(self):
        self.apiKey = settings.GITHUB_API_KEY
        self.apiEndpoint = settings.GITHUB_API_ENDPOINT

    def createIssue(self, title = '', body = ''):
        """
        Sends request to create GitHub issue

        Arguments: 
            title:  title of issue
            body:   body of issue
            
        Returns:
            URL to the created issue
        """
        headers = {
            "Authorization": f"Bearer {self.apiKey}",
            "content-type": "application/json"
        }

        jsonPayload = {
            "title": title,
            "body": body,
            "labels": [
                'user-feedback'
            ]
        }

        r = requests.post(self.apiEndpoint, headers = headers, json = jsonPayload)

        return r

        
