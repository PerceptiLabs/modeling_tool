import logging
import numpy as np
import pandas as pd
import logging
import pickle
import os


from perceptilabs.logconf import APPLICATION_LOGGER

logger = logging.getLogger(APPLICATION_LOGGER)


_ESTIMATOR = None
MODEL_AND_META_PATH = 'insights/csv_ram_estimator/model_and_meta.pkl'


class CsvRamEstimator:
    def __init__(self, model, dtypes):
        self._model = model
        self._dtypes = dtypes

    def __call__(self, csv_path):
        if not os.path.isfile(csv_path):
            return -1

        file_sz = os.path.getsize(csv_path) # If the prediction goes bad.        
        x = np.zeros((1, len(self._dtypes))).astype(np.float32)
        x[0, 0] = file_sz
        unseen = {}

        df = pd.read_csv(csv_path, nrows=1)        
        for dtype in df.dtypes:
            dtype = str(dtype)

            if dtype in self._dtypes:
                idx = self._dtypes.index(dtype)
                x[0, idx] += 1
            else:
                if dtype not in unseen:
                    unseen[dtype] = 0
                unseen[dtype] += 1

        for dtype, count in unseen.items():
            logger.warning(f"File '{csv_path}' contains {count} columns of unseen dtype '{dtype}'")

        y = self._model.predict(x)
        est_sz = round(y.squeeze().tolist())

        # Arbitrary safety margins
        return np.clip(1.5*file_sz, est_sz, 5*file_sz)
        

def get_instance():
    global _ESTIMATOR
    if _ESTIMATOR is not None:
        return _ESTIMATOR

    try:
        with open(MODEL_AND_META_PATH, 'rb') as f:
            mam = pickle.load(f)
            model = mam['model']
            dtypes = mam['columns']
            rmse_train = mam['rmse_train']
            rmse_test = mam['rmse_test']

            logger.info(f"Loading csv ram estimator with rMSE train: {rmse_train} and rMSE test: {rmse_test} from {MODEL_AND_META_PATH}. Seen dtypes are {dtypes}")
            _ESTIMATOR = CsvRamEstimator(model, dtypes)
    except:
        logger.exception(f"Failed loading csv ram estimator from {MODEL_AND_META_PATH}")

    return _ESTIMATOR

            
            

            



            
    
    
    
    

        
            
                
