# https://stackoverflow.com/questions/18089667/how-to-estimate-how-much-memory-a-pandas-dataframe-will-need/47751572

#from tqdm import tqdm
import time
from io import StringIO
import os
import string
import pandas as pd
import numpy as np

N_SAMPLES = 100 # how many samples to create
MAX_ROWS = 1000000
MAX_COLS = 200
MIN_COLS = 10
MIN_STR_LEN = 5
MAX_STR_LEN = 30
RANDOM_SEED = 123

np.random.seed(RANDOM_SEED)

def make_sample():
    n_rows = np.random.randint(0, MAX_ROWS)
    n_cols = np.random.randint(MIN_COLS, MAX_COLS)

    dtypes = [
        np.float32,
        np.float64,
        np.int64,
        np.int32,
        np.str,
    ]
            
    df = pd.DataFrame()
    for i in range(n_cols):
        dtype = np.random.choice(dtypes)        
         
        if dtype is not np.str:
            df[str(i)] = np.random.randint(0, 100, (n_rows,)).astype(dtype)
        else:
            length = np.random.randint(MIN_STR_LEN, MAX_STR_LEN)
            text = ''.join(np.random.choice(['a', 'b', 'c']) for i in range(length))
            df[str(i)] = [text]*n_rows

    size_ram = df.memory_usage(deep=True).sum()

    # Write to a string buffer to measure what would have been the file csv size
    f = StringIO()
    df.to_csv(f)
    f.seek(0, os.SEEK_END)
    size_disk = f.tell()

    # Create a 'bag of words' counting how many columns of each dtype are present
    f.seek(0)    
    df = pd.read_csv(f, nrows=1)
    bag = {}

    for dtype in df.dtypes:
        dtype = str(dtype)
        if dtype not in bag:
            bag[dtype] = 0
        bag[dtype] += 1

    return {'bag': bag,
            'sz_disk': size_disk,
            'sz_ram': size_ram
    }

data = {'sz_disk': [0]*N_SAMPLES, 'sz_ram': [0]*N_SAMPLES}

for i in range(N_SAMPLES):
    sample = make_sample()
    
    data['sz_disk'][i] = sample['sz_disk']
    data['sz_ram'][i] = sample['sz_ram']

    for dtype, count in sample['bag'].items():
        if dtype not in data:
            data[dtype] = [0]*N_SAMPLES
        data[dtype][i] = count


df = pd.DataFrame(data)
path = f'data-{round(time.time())}-{RANDOM_SEED}.csv'
print("writing", N_SAMPLES, "samples to path:", path)
df.to_csv(path)
