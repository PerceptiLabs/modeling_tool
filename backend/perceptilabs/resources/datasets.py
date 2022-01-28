import os
import requests
import logging
from io import StringIO
import pandas as pd


logger = logging.getLogger(__name__)


class DatasetAccess:
    def __init__(self, rygg):
        self._rygg = rygg
    
    def is_perceptilabs_sourced(self, dataset_id):
        data = self._rygg.get_dataset(dataset_id)
        try:
            return bool(data['is_perceptilabs_sourced'])
        except:
            logger.exception("Failed checking if dataset is perceptilabs sourced")
            raise

    def get_location(self, dataset_id):
        data = self._rygg.get_dataset(dataset_id)
        
        try:
            location = data['location'].replace('\\', '/')
            logger.info(f"Found dataset {dataset_id} at {location}")
        except:
            logger.exception("Failed getting dataset location")                        
            raise
        else:
            return location

    def get_name(self, dataset_id):
        data = self._rygg.get_dataset(dataset_id)                    
        try:
            return data['name']
        except:
            logger.exception("Failed getting dataset name")            
            raise
            
    def get_dataframe(self, dataset_id, fix_paths_for=None):
        try:
            location = self.get_location(dataset_id)
            df = pd.read_csv(location)
            logger.info(f"Loaded dataframe for dataset {dataset_id}. Head:\n{df.head()}")
            
            # Localize paths
            if fix_paths_for:
                directory = os.path.dirname(location)
                
                df[fix_paths_for] = df[fix_paths_for].applymap(
                    lambda rel_path: os.path.join(directory, rel_path))                
            
            return df
        except:
            logger.exception("Failed getting dataframe")
            raise
        
        return df
        

        

        
        
    
