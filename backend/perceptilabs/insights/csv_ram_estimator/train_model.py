import sys
import pickle
import numpy as np
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from pprint import pprint

COLUMNS = ['sz_disk']#, 'int64', 'float64', 'object']
OUTPUT_FILE = './model_and_meta.pkl'

path = sys.argv[1]

if os.path.exists(OUTPUT_FILE):
    sys.exit(0)

df = pd.read_csv(path)

X = np.atleast_2d(df[COLUMNS].values).reshape(-1, len(COLUMNS))
y = df['sz_ram'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.33,
    random_state=42,
    shuffle=True
)

model = LinearRegression(normalize=True).fit(X_train, y_train)

y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

rmse_train = mean_squared_error(y_train, y_pred_train, squared=False)
rmse_test = mean_squared_error(y_test, y_pred_test, squared=False)

print(f"rmse_train: {rmse_train/10**6} MB, rmse_test: {rmse_test/10**6} MB")

# Save the model along with some metadata
model_and_meta = {
    'columns': COLUMNS,
    'model': model,
    'rmse_train': rmse_train,
    'rmse_test': rmse_test,
    'train_set_size': len(y_train),
    'test_set_size': len(y_test),
    'train_set_avg_ram': np.mean(y_train),
    'train_set_std_ram': np.std(y_train),
    'train_set_max_ram': np.amax(y_train),    
    'train_set_min_ram': np.amin(y_train),        
    'test_set_avg_ram': np.mean(y_test),
    'test_set_std_ram': np.std(y_train),
    'test_set_max_ram': np.amax(y_train),
    'test_set_min_ram': np.amin(y_train),                
    'data_path': path
}

pprint(model_and_meta)

with open(OUTPUT_FILE, 'wb') as f:
    pickle.dump(model_and_meta, f, protocol=2)

raise SystemExit

import matplotlib.pyplot as plt

x = X_test[:, 0]
y = np.squeeze(y_test)
y_ = model.predict(X_test)

plt.plot(x, y, 'o', label='target')
plt.plot(x, y_, '+', label='pred')
plt.legend()
plt.show()






