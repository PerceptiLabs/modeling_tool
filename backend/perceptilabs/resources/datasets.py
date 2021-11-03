import os
import requests

from perceptilabs.settings import (
    RYGG_BASE_URL,
    RYGG_FILE_SERVING_TOKEN as TOKEN
)



class DatasetAccess:
    def is_perceptilabs_sourced(self, dataset_id):
        try:
            data = requests.get(f"{RYGG_BASE_URL}/datasets/{dataset_id}/?token={TOKEN}").json()
            return bool(data['is_perceptilabs_sourced'])
        except:
            return None

        
    
    
