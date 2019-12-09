# import dask
# import os
# import glob
# import numpy as np

# import logging
# log = logging.getLogger(__name__)

# from s3buckets import S3BucketAdapter

# class DataHandlerLW():
#     def __init__(self,accessProperties):
#         # TEMPORRAY FIX
#         if "Partition_list" not in accessProperties:
#              accessProperties["Partition_list"] = [[70, 20, 10]]*len(accessProperties["Path"])
#              log.error("Partition_list not set in accessProperties!! Setting all splits to [70, 20, 10]")
             
#         if "Batch_size" not in accessProperties:
#              accessProperties["Batch_size"] = 10            
#              log.error("Batch_size not set in accessProperties!! Defaulting to 10")
             
#         # accessProperties["Batch_size"] = 10
#         # accessProperties["Shufflie"] = True
#         # accessProperties["Shuffle"] = True        

        
#         # print(accessProperties)
#         self.accessProperties=accessProperties
#         # print(accessProperties["Path"])
#         if "EnvType" in self.accessProperties:
#             self.FLAG_UNITY=False
#             self.env=self.readEnvironment(accessProperties)
#             self.sample=self.get_enviroment_sample()
#             self.data_size=1
#             self.cols=[]
#             self.action_space=self.getActionSpace()
#         else:
#             self.cols=[]
#             self.data_sizes=[]
#             self.data = self.read_datasets_from_paths(accessProperties["Source"],
#                                                       accessProperties["Partition_list"],
#                                                       columns=self.accessProperties['Columns'])
#             self.sample = self.get_data_sample(self.data)
#             self.data_size = len(np.atleast_1d(self.data))
        


        
#         '''
#         self.FLAG_UNITY=False
#         if "EnvType" in self.accessProperties:
#             self.env=self.readEnvironment(accessProperties)
#             self.sample=self.get_enviroment_sample()
#             self.data_size=1
#             self.cols=[]
#             self.action_space=self.getActionSpace()
#         else:
#             if accessProperties["Category"]=="Local":
#                 if accessProperties["Path"]:
#                     path=accessProperties["Path"]
#                 else:
#                     path=""
#             elif accessProperties["Category"]=="LocalBlob":
#                 path=self._blob(accessProperties["Container"],accessProperties["BlobName"])
#             self.cols=[]
#             self.data=self._read_data(path)
#             self.data_size=self.get_size(self.data)
#         '''

#     def get_size(self):
#         return len(self.data)
    
#     def getActionSpace(self):
#         if self.FLAG_UNITY:
#             return list(self.env.reset().values())[0].previous_vector_actions.size
#         else:
#             return self.env.action_space.n

#     def get_data_sample(self,data):
#         try:
#             return data[0]
#         except:
#             return []

#     def get_enviroment_sample(self):
#         if self.FLAG_UNITY:
#             state=list(self.env.reset().values())[0]
#             return np.squeeze(state.visual_observations)
#         else:
#             return self.env.reset()

#     def updateProperties(self,accessProperties):
#         self.accessProperties=accessProperties
#         if "EnvType" in self.accessProperties:
#             return
#         else:
#             for path in self.datasets.keys():
#                 if path not in accessProperties["Path"]:
#                     del self.datasets[path]

#             self.data = self.read_data(accessProperties["Path"],
#                                 accessProperties["Partition_list"],
#                                 columns=self.accessProperties['Columns'])

#             self.data_size = len(np.atleast_1d(self.data))

#             if self.ext.lower()=='json':
#                 self.cols = [list(self.dframe.keys())[i] for i in self.accessProperties['Columns']]
#                 data = self.dframe[self.cols[0]]
#             elif self.ext.lower()=='csv':
#                 self.cols = [list(self.dframe.columns)[i] for i in self.accessProperties['Columns']]
#                 d=self.dframe[self.cols]
#                 data = d.to_numpy()
#             else:
#                 return
#             self.sample=self.get_data_sample(data)
    
#     def clean_up(self):
#         del self.data

#     # def _blob(self,container_name,blob_name):
#     #     # block_blob_service = BlockBlobService(account_name='storagedatablob', account_key='AGQpCfJmaMcVjTM2WVOy/xv8vE/YyoOvt4dxIV4wuasr+bqgPg8KNZbfb9mXGXliT8CxJOhKaLJgLzWvr/pHWw==')
#     #     local_path=os.path.expanduser("~/Documents")
#     #     local_file_name ="mnist.pkl.gz"
#     #     full_path_to_file =os.path.join(local_path, local_file_name)
#     #     # block_blob_service.get_blob_to_path(container_name, blob_name, full_path_to_file) 
#     #     return full_path_to_file

#     # def _read_data(self,path):
#     #     return self._read_file(path)

#     # def _read_file(self,paths):
#     #     dataList=[]
#     #     for path in paths:
#     #         self.ext,path=self._get_ext(os.path.abspath(path))
#     #         method_name='_{0}'.format(self.ext.lower())
#     #         # print(method_name)
#     #         method = getattr(self, method_name, lambda: "Error")
#     #         dataList.append(method(path))     
#     #     data=np.vstack(dataList)
#     #     self.sample=self.get_data_sample(data)  
#     #     return data

#     # def _get_ext(self,path):
#     #     if os.path.isfile(path):
#     #         return os.path.splitext(path)[1][1:],path
#     #     elif os.path.isdir(path):
#     #         ext=os.listdir(path)[0].split('.')[-1]
#     #         return ext,''.join((path,'/*.',ext))
#     #     else:
#     #         raise NameError("Could not find path")

#     # def _get_filenames(self,path):
#     #     if len(self.accessProperties['Path'])==1:
#     #         return sorted(glob.glob(path))
#     #     else:
#     #         return [os.path.abspath(file_path) for file_path in self.accessProperties['Path']]

#     # def _array(self,path,type_):
#     #     filenames = self._get_filenames(path)
#     #     # print("Filenames:", filenames)
#     #     if type_ == "img":
#     #         import skimage.io
#     #         data=[]
#     #         for file_path in filenames:
#     #             tmpData=skimage.io.imread(file_path)
#     #             if tmpData.ndim<2:
#     #                 tmpData=np.atleast_2d(tmpData).T
#     #             data.append(tmpData)

#     #         # self.sample=self.get_data_sample(data)
#     #     if type_=='npy':
#     #         data=[]
#     #         for file_path in filenames:
#     #             tmpData=np.load(file_path)
#     #             if tmpData.ndim<2:
#     #                 tmpData=np.atleast_2d(tmpData).T
#     #             data.extend(tmpData)

#     #         # self.sample=self.get_data_sample(data)
#     #     elif type_=='mat':
#     #         import scipy.io as sio
#     #         data=[]
#     #         for file_path in filenames:
#     #             tmpData=sio.loadmat(file_path)
#     #             if tmpData.ndim<2:
#     #                 tmpData=np.atleast_2d(tmpData).T
#     #             data.extend(tmpData)
        
#     #         # self.sample=self.get_data_sample(data)
#     #     return data

#     # def _dataframe(self,path,type_):
#     #     import dask.dataframe as df
#     #     path=self._get_filenames(path)
#     #     if type_=='js':
#     #         self.dframe = df.read_json(path, orient='columns')
#     #         self.cols=list(self.dframe.columns)
#     #         data = self.dframe.to_dask_array(lengths=True)
#     #     elif type_=='txt':
#     #         dframe = df.read_csv(path).dropna()
#     #         data = dframe.to_records()
#     #     elif type_=='csv':
#     #         self.dframe = df.read_csv(path).dropna()
#     #         self.cols=list(self.dframe.columns)
#     #         data = self.dframe.to_dask_array(lengths=True)
#     #     self.sample=self.get_data_sample(data)
#     #     return data

#     # def _csv(self,path):
#     #     return self._dataframe(path,'csv')

#     # def _png(self,path):
#     #     return self._array(path,'img')

#     # def _jpg(self,path):
#     #     return self._array(path,'img')

#     # def _jpeg(self,path):
#     #     return self._array(path,'img')

#     # def _tif(self,path):
#     #     return self._array(path,'img')

#     # def _tiff(self,path):
#     #     return self._array(path,'img')

#     # def _mat(self,path):
#     #     return self._array(path,'mat')

#     # def _npy(self,path):
#     #     return self._array(path,'npy')

#     # def _npz(self,path):
#     #     return self._array(path,'npy')

#     # def _json(self,path):
#     #     return self._dataframe(path,'js')

#     # def _txt(self,path):
#     #     return self._dataframe(path,'txt')

#     def readEnvironment(self, accessProperties):
#         if accessProperties['EnvType']=="Gym":
#             import gym
#             #env=SubprocVecEnv([gym.make(accessProperties['Atari']+'-v0'),gym.make(accessProperties['Atari']+'-v0'),gym.make(accessProperties['Atari']+'-v0')])
#             env=gym.make(accessProperties['Atari']+'-v0')
#         elif accessProperties['EnvType']=="Unity":
#             self.FLAG_UNITY=True
#             from unityagents import UnityEnvironment
#             env=UnityEnvironment(file_name=accessProperties["Path"][0])
#             #self.action_space=
#             # pass
#         return env

    
#     def _read_dataset_from_file(self, path, columns, single_file=False):
#         data_mat = None
#         file_ext = os.path.splitext(path)[1][1:]
#         self.ext = file_ext
#         # print("Extension:", self.ext)
        
#         if file_ext == 'npy':
#             data_mat = np.load(path)
#         elif file_ext in ['jpg', 'png', 'jpeg', 'tif', 'tiff']:
#             import skimage.io
#             data_mat = skimage.io.imread(path)

#             if single_file:
#                 data_mat = np.array([data_mat]) #add extra dimension
#         elif file_ext == 'mat':
#             pass
#         elif file_ext == 'json':
#             import pandas as pd
#             import json
#             with open(path,'r') as f:
#                 jsonDict=json.load(f)
#             from pdb import set_trace

#             # for key, value in jsonDict.items():

#             self.dframe = {k: np.asarray(v) for k, v in jsonDict.items()}
            
#             # self.dframe=pd.read_json(path)
#             # set_trace()
#             cols=list(self.dframe.keys())
            
#             if self.cols!=cols and self.cols:
#                 raise Exception("Collumn Mismatch")
#             self.cols=cols
#             # correct_columns=[cols[i] for i in columns]
#             # set_trace()
#             if len(columns) == 0:
#                 data_mat = np.empty((0,))
#             else:
#                 data_mat=self.dframe[cols[columns[0]]]
#         elif file_ext == 'csv':
#             import pandas as pd
#             self.dframe=pd.read_csv(path)
#             cols=list(self.dframe.columns)
#             if self.cols!=cols and self.cols:
#                 raise Exception("Collumn Mismatch")
#             self.cols=cols
#             correct_columns=[cols[i] for i in columns]
#             data_mat=self.dframe[correct_columns].to_numpy()

#         if data_mat is not None:
#             if data_mat.ndim < 2:
#                 data_mat = np.atleast_2d(data_mat).T

#         return data_mat
        

#     def _read_dataset_from_directory(self, path, columns):
#         file_names = sorted(os.listdir(path))
#         file_names=[os.path.join(path,f_n) for f_n in file_names]
#         self._read_dataset_from_files(file_names, columns)

#     def _read_dataset_from_files(self, paths, columns):
#         file_ext = None        
#         data_matrices = []        
#         for file_name in paths:
#             current_ext = os.path.splitext(file_name)[1][1:]
#             if file_ext is None:
#                 file_ext = current_ext
#             elif current_ext != file_ext:
#                 continue
            
#             data_mat = self._read_dataset_from_file(file_name, columns)
#             data_matrices.append(data_mat)

#         data_matrices = np.array(data_matrices)
#         return data_matrices

#     def read_dataset_from_bucket(self, bucket, delimiter, prefix, columns):

#         with S3BucketAdapter(bucket) as adapter:
#             keys = adapter.get_keys(delimiter, prefix)

#             paths = [adapter.download_file(k) for k in keys]
#             data_matrices = self._read_dataset_from_files(paths, columns)
            
#         return data_matrices

#     def read_datasets_from_paths(self, sources, partitions, columns=None):
#         train_list = []
#         validation_list = []
#         test_list = []                
#         dataset_list = []


#         if not sources:
#             raise Exception("No sources were sent!")

#         def sort_together(l1, l2, key):
#             l1, l2 = zip(*sorted(zip(l1, l2), key=key))
#             return l1, l2

#         try:
#             sources, partitions = sort_together(sources, partitions,
#                                                 key=lambda x:x[0]['identifier'])
#         except Exception:
#             raise Exception("No partitions Exist!")

#         for source, partition in zip(paths, partitions):
#             type_ = source['type']
#             if type_ == 'file':
#                 path = source['identifier']
#                 if path not in self.datasets:
#                     dataset = self._read_dataset_from_file(path, columns, single_file=True)
#                     self.datasets[path]=dataset
#             elif type_ == 'directory':
#                 path = source['identifier']  
#                 if path not in self.datasets:              
#                     dataset = self._read_dataset_from_directory(path, columns)
#                     self.datasets[path]=dataset
#             elif type_ == 's3bucket':
#                 bucket = source['identifier']
#                 delimiter = source['delimiter']
#                 prefix = source['prefix']
#                 if bucket+delimiter+prefix not in self.datasets:
#                     dataset = self._read_dataset_from_bucket(bucket, delimiter, prefix, columns)
#                     self.datasets[bucket+delimiter+prefix]=dataset

#             train_vec, validation_vec, test_vec = self._split(dataset, partition)

#             train_list.extend(train_vec)
#             validation_list.extend(validation_vec)
#             test_list.extend(test_vec)                
#             dataset_list.extend(dataset)

#         def stack(array):
#             if len(array) > 0:
#                 return np.stack(array)
#             else:
#                 return np.array([])

#         def resqueeze(t):
#             dim = t.shape[0]
#             t = t.squeeze()
#             if dim == 1:
#                 t = np.array([t])
#             return t

#         self.train_stacked = resqueeze(stack(train_list)).astype(np.float32)
#         self.validation_stacked = resqueeze(stack(validation_list)).astype(np.float32)
#         self.test_stacked = resqueeze(stack(test_list)).astype(np.float32)
#         dataset_stacked = resqueeze(stack(dataset_list)).astype(np.float32)
#         return dataset_stacked

#     def _split(self, dataset, partition):
#         size = len(dataset)

#         if sum(partition) != 100:
#             raise ValueError("Partition rates do not sum to 100!")
        
#         i1 = round(partition[0]*size/100)
#         i2 = i1 + round(partition[1]*size/100)        

#         train = dataset[0:i1]
#         validation = dataset[i1:i2]
#         test = dataset[i2:]
#         return train, validation, test    


    
# if __name__ == "__main__":
#     '''
#     for i in range(10):
#         path = "/home/anton/Data/rand_imgs/"+str(i)+".jpg"
#         import cv2
#         import numpy as np
#         cv2.imwrite(path, np.ones((128, 128, 3)))
#     '''

#     def setup(paths,partitions):
#         accessProperties = {"Category": "Local",
#                             "Path": paths,
#                             "Partition_list":partitions,
#                             "Columns": [0]}        
#         return accessProperties


#     # paths = ['/home/anton/Data/mnist_split/mnist_labels.npy']*2
#     # paths = ['/home/anton/Data/rand_imgs/']
#     # paths = ['/home/anton/Data/rand_imgs_1/']
#     # paths = ['/home/anton/Data/rand_imgs/1.jpg']
#     # paths=['C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\data_banknote_authentication.csv','C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\data_banknote_authentication - Copy.csv']
#     # partitions=[[70,20,10],[50,40,10]]
#     # paths=['C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\data_banknote_authentication.csv']
#     #paths=['C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\json\\test.json']
#     paths = ['/home/anton/Data/test.json']    
#     partitions=[[70,20,10]]
    
#     ap = setup(paths,partitions)
#     dh = DataHandlerLW(ap)
#     #dh.read_data(paths)
#     print(dh.train_stacked.shape)
#     print(dh.validation_stacked.shape)    
#     print(dh.test_stacked.shape)
#     # print("Cols: ",dh.cols)

#     t = dh.train_stacked
#     v = dh.validation_stacked
#     t_ = dh.test_stacked    

#     #t = resqueeze(t)
#     #v = resqueeze(v)
#     #t_ = resqueeze(t_)    

#     print(t.shape, v.shape, t_.shape)
    
#     import pdb;pdb.set_trace()
        
#     print(dh.ext)
            


