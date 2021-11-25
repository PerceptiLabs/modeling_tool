import requests


class DatasetAccess:
    def __init__(self, rygg):
        self._rygg = rygg
    
    def is_perceptilabs_sourced(self, dataset_id):
        data = self._rygg.get_dataset(dataset_id)
        try:
            return bool(data['is_perceptilabs_sourced'])
        except:
            return None

    def get_location(self, dataset_id):
        data = self._rygg.get_dataset(dataset_id)                    
        try:
            return data['location']
        except:
            return None

    def get_name(self, dataset_id):
        data = self._rygg.get_dataset(dataset_id)                    
        try:
            return data['name']
        except:
            return None
        
        
    
    
