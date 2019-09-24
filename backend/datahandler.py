import dask
import os
import glob
import numpy as np
import tensorflow as tf
import re
import itertools

import logging
log = logging.getLogger(__name__)

from datahandler_lw import DataHandlerLW

class DataHandler():
    def __init__(self,accessProperties,hyperparameters):
        
        
        # TEMPORRAY FIX
        # accessProperties["Partitions"] = [[70, 20, 10]]*len(accessProperties["Path"])
        # accessProperties["Batch_size"] = 10
        # accessProperties["Shufflie"] = True
        # accessProperties["Shuffle"] = True        
        
        data_handler_lw = DataHandlerLW(accessProperties)
        self.data_handler_lw = data_handler_lw
        self.data = data_handler_lw.data
        
        self.accessProperties=accessProperties
        # self.accessProperties["Key"]=self.accessProperties["Type"]
        # if accessProperties["Category"]=="Local":
        #     path=os.path.abspath(accessProperties["Path"][0])
        # elif accessProperties["Category"]=="LocalBlob":
        #     path=self._blob(accessProperties["Container"],accessProperties["BlobName"])
        self.dtype=''
        #self.train_dataset,self.validation_dataset,self.test_dataset,self.data=self._get_datasets(accessProperties)

        self.train_dataset = tf.data.Dataset.from_tensor_slices(data_handler_lw.train_stacked)
        self.validation_dataset = tf.data.Dataset.from_tensor_slices(data_handler_lw.validation_stacked)
        self.test_dataset = tf.data.Dataset.from_tensor_slices(data_handler_lw.test_stacked)        

        self.train_data_size = len(data_handler_lw.train_stacked)
        self.validation_data_size = len(data_handler_lw.validation_stacked)
        self.test_data_size = len(data_handler_lw.test_stacked)                

        self.trainingIterations=int(self.train_data_size/int(accessProperties["Batch_size"]))
        self.maxIter=int((self.train_data_size+self.validation_data_size)/int(accessProperties["Batch_size"]))
        self.maxTestIter=self.test_data_size

        
        self.batch_size=int(accessProperties["Batch_size"])
        # self.placeholder=self._get_placeholder(self.get_sample(self.data))


        if not 'Shuffle_data' in accessProperties:
            log.error("'Shuffle_data' not present in in accessProperties. Setting it to False.")
            accessProperties['Shuffle_data'] = False

        if accessProperties["Shuffle_data"]:
            # self.dataset.shuffle(self.data_size,seed=self.accessProperties['Seed'],reshuffle_each_iteration=False)
            # train_dataset = self.dataset.take(train_size)
            # validation_dataset = self.dataset.skip(train_size)
            # test_dataset = validation_dataset.skip(validation_size)
            np.random.seed(self.accessProperties['Seed'])
            np.random.shuffle(self.data)
            self.train_dataset=self.train_dataset.shuffle(self.train_data_size,seed=self.accessProperties['Seed']).batch(int(accessProperties['Batch_size'])).repeat()
            self.validation_dataset=self.validation_dataset.repeat().batch(int(accessProperties['Batch_size']))
        else:
            # np.random.seed(self.accessProperties['Seed'])
            # np.random.shuffle(self.data)
            self.train_dataset=self.train_dataset.repeat().batch(int(accessProperties['Batch_size']))
            self.validation_dataset=self.validation_dataset.repeat().batch(int(accessProperties['Batch_size']))

        self.test_dataset=self.test_dataset.repeat(1).batch(1)
                                                  

        
        # self.dataset,self.data=self._read_data(path)
        # self.data_size=self._get_size(self.data)
        # self.maxIter=0
        # self.maxTestIter=0
        # self.train_dataset,self.validation_dataset,self.test_dataset=self._get_split_dataset(hyperparameters)

    # def clean_up(self,lazy_data):
    #     del lazy_data

    # def _get_datasets(self,accessProperties):
    #     total_train_dataset=None
    #     total_validation_dataset=None
    #     total_test_dataset=None

    #     train_data_size=0
    #     validation_data_size=0
    #     test_data_size=0
    #     total_data_size=0
    #     for path,partition in itertools.zip_longest(accessProperties["Path"],accessProperties["Partition_list"]):
    #         # partial_dataset,partial_data=self._read_data(path,partition)
    #         partial_train_dataset, partial_validation_dataset, partial_test_dataset, data, data_size = self._read_data(path,partition)
    #         # data_size=self._get_size(partial_data)

    #         train_data_size+=int(data_size*partition[0]/100)
    #         validation_data_size+=int(data_size*partition[1]/100)
    #         test_data_size+=int(data_size*partition[2]/100)
    #         # total_data_size+=data_size
    #         # partial_train_dataset,partial_validation_dataset,partial_test_dataset=self._get_split_dataset(partial_dataset,partition)

    #         if total_train_dataset:
    #             total_train_dataset=total_train_dataset.concatenate(partial_train_dataset)
    #         else:
    #             total_train_dataset=partial_train_dataset

    #         if total_validation_dataset:
    #             total_validation_dataset=total_validation_dataset.concatenate(partial_validation_dataset)
    #         else:
    #             total_validation_dataset=partial_validation_dataset

    #         if total_test_dataset:
    #             total_test_dataset=total_test_dataset.concatenate(partial_test_dataset)
    #         else:
    #             total_test_dataset=partial_test_dataset            

    #     self.trainingIterations=int(train_data_size/int(accessProperties["Batch_size"]))
    #     self.maxIter=int((train_data_size+validation_data_size)/int(accessProperties["Batch_size"]))
    #     self.maxTestIter=test_data_size
    #     total_train_dataset,total_validation_dataset,total_test_dataset,data=self._dataset_post_processing(accessProperties,data,total_train_dataset,total_validation_dataset,total_test_dataset,train_data_size)
    #     return total_train_dataset, total_validation_dataset, total_test_dataset, data

    # def _dataset_post_processing(self,accessProperties,data,train_dataset,validation_dataset,test_dataset,train_data_size):
    #     if accessProperties['Shufflie']:
    #         np.random.seed(accessProperties['Seed'])
    #         np.random.shuffle(data)
    #         train_dataset=train_dataset.shuffle(train_data_size,seed=self.accessProperties['Seed']).batch(int(accessProperties['Batch_size'])).repeat()
    #         validation_dataset=validation_dataset.repeat().batch(int(accessProperties['Batch_size']))
    #     else:
    #         train_dataset=train_dataset.repeat().batch(int(accessProperties['Batch_size']))
    #         validation_dataset=validation_dataset.repeat().batch(int(accessProperties['Batch_size']))
        
    #     test_dataset=test_dataset.repeat(1).batch(1)

    #     return train_dataset,validation_dataset,test_dataset, data

    # def _get_split_dataset(self,dataset,partition):
    #     train_size=float(partition[0])/100
    #     validation_size=float(partition[1])/100
    #     test_size=float(partition[2])/100

    #     train_dataset = dataset.take(train_size)
    #     test_dataset = dataset.skip(train_size)
    #     validation_dataset = test_dataset.skip(validation_size)
    #     test_dataset = test_dataset.take(test_size)
        
    #     return train_dataset,validation_dataset,test_dataset

    # def _get_placeholder(self,sample=None):
    #     sample = sample.squeeze()
    #     print("SAMPLE!!!!", sample, sample.shape)
    #     if self.dtype=="filenames":
    #         return tf.placeholder(tf.string)
    #     else:
    #         dimLen=len(np.shape(sample))+1
    #         print("dimLen", dimLen)
    #         if dimLen<=1:
    #             return tf.placeholder(tf.float32, shape=[None])
    #         else:
    #             return tf.placeholder(tf.float32, shape=[None]+[dim for dim in np.shape(sample)])
        
    # def _get_size(self,lazy_data):
    #     return len(lazy_data)
    #     if self.dtype=="filenames":
    #         return int(self.accessProperties['Dataset_size'])
    #     else:
    #         return lazy_data.shape[0]

    # def get_sample(self,lazy_data):
    #     return self.data_handler_lw.data[0]

    # def _blob(self,container_name,blob_name):
    #     # block_blob_service = BlockBlobService(account_name='storagedatablob', account_key='AGQpCfJmaMcVjTM2WVOy/xv8vE/YyoOvt4dxIV4wuasr+bqgPg8KNZbfb9mXGXliT8CxJOhKaLJgLzWvr/pHWw==')
    #     local_path=os.path.expanduser("~/Documents")
    #     local_file_name ="mnist.pkl.gz"
    #     full_path_to_file =os.path.join(local_path, local_file_name)
    #     # block_blob_service.get_blob_to_path(container_name, blob_name, full_path_to_file)
    #     return full_path_to_file

    # def _read_data(self,path,partition):
    #     return self._read_file(path,partition)

    # def _read_file(self,path,partition):
    #     ext,path=self._get_ext(path)
    #     method_name='_{0}'.format(ext.lower())
    #     method = getattr(self, method_name, lambda: "Error")
    #     return method(path,partition)

    # def _get_ext(self,path):
    #     if os.path.isfile(path):
    #         return os.path.splitext(path)[1][1:],path
    #     elif os.path.isdir(path):
    #         ext=os.listdir(path)[0].split('.')[-1]
    #         return ext,''.join((path,'/*.',ext))
    #     else:
    #         raise NameError("Could not find path")

    # def numericalSort(self,value):
    #     numbers = re.compile(r'(\d+)')
    #     parts = numbers.split(value)
    #     parts[1::2] = map(int, parts[1::2])
    #     return parts

    # def _get_filenames(self,path):
    #     #if len(self.accessProperties['Path'])==1:
    #     if True:
    #         return sorted(glob.glob(path), key=self.numericalSort)
    #     else:
    #         return [os.path.abspath(file_path) for file_path in self.accessProperties['Path']]

    # # --------------------------------------- TF FileReaders ---------------------------------------

    # def _csvreader(self,path,partition):
    #     self.placeholder=self._get_placeholder()
    #     filenames = self._get_filenames(path)
    #     cols=self.accessProperties["Columns"]
    #     n_columns=len(cols)
    #     record_defaults = [[0.0]]*n_columns
    #     # train_dataset=tf.data.experimental.CsvDataset(self.placeholder,record_defaults, header=True, select_cols=cols)
    #     # validation_dataset=tf.data.experimental.CsvDataset(self.placeholder,record_defaults, header=True, select_cols=cols)
    #     # test_dataset=tf.data.experimental.CsvDataset(self.placeholder,record_defaults, header=True, select_cols=cols)
    #     dataset=tf.data.experimental.CsvDataset(self.placeholder,record_defaults, header=True, select_cols=cols)

    #     return self._get_split_dataset(dataset,partition), self._get_size(filenames)
    #     # return tf.data.experimental.CsvDataset(self.placeholder,record_defaults, header=True, select_cols=cols),filenames

    # def _parse_png_function(self,filename,partition):
    #     image_string = tf.read_file(filename)
    #     image_decoded = tf.image.decode_png(image_string)
    #     (newH,newW)=np.shape(self.sample)[0:2]
    #     image_resized = tf.image.resize_images(image_decoded, [newH,newW])
    #     # image_resized = tf.image.resize_images(image_decoded, [dim for dim in np.shape(self.sample)[:-1]])
    #     return image_resized  

    # def _parse_jpg_function(self,filename,partition):
    #     image_string = tf.read_file(filename)
    #     image_decoded = tf.image.decode_jpeg(image_string)
    #     (newH,newW)=np.shape(self.sample)[0:2]
    #     image_resized = tf.image.resize_images(image_decoded, [newH,newW])
    #     # image_resized /= 255.0  # normalize to [0,1] range

    #     # image_resized = tf.image.resize_images(image_decoded, [dim for dim in np.shape(self.sample)[:-1]])
    #     # #CHANGED
    #     # return filename,image_resized  
    #     return image_resized

    # def _parse_bmp_function(self,filename,partition):
    #     image_string = tf.read_file(filename)
    #     image_decoded = tf.image.decode_bmp(image_string)
    #     (newH,newW)=np.shape(self.sample)[0:2]
    #     image_resized = tf.image.resize_images(image_decoded, [newH,newW])
    #     # image_resized = tf.image.resize_images(image_decoded, [dim for dim in np.shape(self.sample)[:-1]])
    #     return image_resized  

    # def _imagereader(self,path,partition,type_):
    #     self.placeholder=self._get_placeholder()
    #     self.sample=self._array(path,'img')
    #     filenames = self._get_filenames(path)
    #     data_size=self._get_size(filenames)

    #     train_dataset=tf.data.Dataset.from_tensor_slices(filenames[0:int(data_size*partition[0])])
    #     validation_dataset=tf.data.Dataset.from_tensor_slices(filenames[int(data_size*partition[0]):int(data_size*partition[1])])
    #     test_dataset=tf.data.Dataset.from_tensor_slices(filenames[int(data_size*partition[1]):int(data_size*partition[2])])

    #     dataset = tf.data.Dataset.from_tensor_slices(self.placeholder)
    #     if type_=='png:':
    #         return dataset.map(self._parse_png_function),filenames
    #     elif type_=='jpg':
    #         return dataset.map(self._parse_jpg_function),filenames
    #     elif type_=='bmp':
    #         return dataset.map(self._parse_bmp_function),filenames

    # def _textreader(self,path,partition):
    #     self.placeholder=self._get_placeholder()
    #     filenames = self._get_filenames(path)
    #     return tf.data.TextLineDataset(self.placeholder),

    # # -------------------------------------- Dask FileReaders --------------------------------------

    # # def _array(self,path,partition,type_):
    # #     import dask.array as da
    # #     from dask import delayed
    # #     if type_=='img':
    # #         import skimage.io
    # #         readarray = delayed(skimage.io.imread, pure=True)
    # #         filenames = self._get_filenames(path)
    # #         lazy_arrays = [readarray(file_path) for file_path in filenames]   # Lazily evaluate read function on each path
    # #         sample = lazy_arrays[0].compute()  # load the first array (assume rest are same shape/dtype)
    # #         self.clean_up(lazy_arrays)
    # #         return sample
    # #     if type_=='npy':
    # #         readarray = delayed(np.load, pure=True)
    # #     elif type_=='mat':
    # #         import scipy.io as sio
    # #         readarray = delayed(sio.loadmat, pure=True)
        
    # #     filenames = self._get_filenames(path)
    # #     lazy_arrays = [readarray(file_path) for file_path in filenames]   # Lazily evaluate read function on each path
    # #     sample = self.get_sample(lazy_arrays[0])  # load the first array (assume rest are same shape/dtype)
    # #     arrays = [da.from_delayed(lazy_array,dtype=sample.dtype, shape=sample.shape) for lazy_array in lazy_arrays] # Construct a small Dask array for every lazy value
    # #     data = da.stack(arrays, axis=0)[0] # Stack all small Dask arrays into one
    # #     self.placeholder=self._get_placeholder(sample)
    # #     return tf.data.Dataset.from_tensor_slices(self.placeholder),data.compute()
    # def _array(self,path,partition,type_):
    #     # if type_=='img':
    #     #     import skimage.io
    #     #     readarray = delayed(skimage.io.imread, pure=True)
    #     filenames = self._get_filenames(path)
    #     #     lazy_arrays = [readarray(file_path) for file_path in filenames]   # Lazily evaluate read function on each path
    #     #     sample = lazy_arrays[0].compute()  # load the first array (assume rest are same shape/dtype)
    #     #     self.clean_up(lazy_arrays)
    #     #     return sample
    #     if type_=='img':
    #         import skimage.io
    #         data=[]
    #         for file_path in filenames:
    #             tmpData=skimage.io.imread(file_path)
    #             if tmpData.ndim<2:
    #                 tmpData=np.atleast_2d(tmpData).T
    #             data.append(tmpData)

    #     if type_=='npy':
    #         data=[]
    #         if len(filenames)>1:
    #             for file_path in filenames:
    #                 tmpData=np.load(file_path)
    #                 if tmpData.ndim<2:
    #                     tmpData=np.atleast_2d(tmpData).T
    #                 data.extend(tmpData)
    #         else:
    #             tmpData=np.load(filenames[0])
    #             if tmpData.ndim<2:
    #                 tmpData=np.atleast_2d(tmpData).T
    #             data=tmpData
    #     elif type_=='mat':
    #         import scipy.io as sio
    #         data=[]
    #         for file_path in filenames:
    #             tmpData=sio.loadmat(file_path)
    #             if tmpData.ndim<2:
    #                 tmpData=np.atleast_2d(tmpData).T
    #             data.extend(tmpData)
        
    #     # import pdb
    #     # pdb.set_trace()
    #     data_size=self._get_size(data)
    #     train_dataset=tf.data.Dataset.from_tensor_slices(data[0:int(data_size*partition[0]/100)])
    #     validation_dataset=tf.data.Dataset.from_tensor_slices(data[int(data_size*partition[0]/100):int(data_size*(partition[0]+partition[1])/100)])
    #     test_dataset=tf.data.Dataset.from_tensor_slices(data[int(data_size*(partition[0]+partition[1])/100):int(data_size*(partition[0]+partition[1]+partition[2])/100)])
    #     self.placeholder=self._get_placeholder(self.get_sample(data))
    #     return train_dataset,validation_dataset,test_dataset,data,data_size



    # def _dataframe(self,path,partition,js=False):
    #     import dask.dataframe as df
    #     if js:
    #         dframe = df.read_json(path, orient='columns')
    #         cols = [list(dframe.columns)[i] for i in self.accessProperties['Columns']]
    #         data = dframe[cols].to_dask_array(lengths=True)
    #     else:
    #         dframe = df.read_csv(path).dropna()
    #         cols = [list(dframe.columns)[i] for i in self.accessProperties['Columns']]
    #         d=dframe[cols]
    #         data = d.to_dask_array(lengths=True)
    #     self.placeholder=self._get_placeholder(self.get_sample(data))
    #     return tf.data.Dataset.from_tensor_slices(self.placeholder),data.compute()

    # # ------------------------------------- TF FileReaders EXT -------------------------------------

    # def _csv(self,path,partition):
    #     self.dtype='filenames'
    #     return self._csvreader(path,partition)

    # def _png(self,path,partition):
    #     self.dtype='filenames'
    #     return self._imagereader(path,partition,'png')

    # def _jpg(self,path,partition):
    #     self.dtype='filenames'
    #     return self._imagereader(path,partition,'jpg')

    # def _jpeg(self,path,partition):
    #     self.dtype='filenames'
    #     return self._imagereader(path,partition,'jpg')
        
    # def _bmp(self,path,partition):
    #     self.dtype='filenames'
    #     return self._imagereader(path,partition,'bmp')

    # def _txt(self,path,partition):
    #     self.dtype='filenames'
    #     return self._textreader(path,partition)

    # # ------------------------------------ Dask FileReaders EXT ------------------------------------

    # def _tif(self,path,partition):
    #     return self._array(path,partition,'img')

    # def _tiff(self,path,partition):
    #     return self._array(path,partition,'img')

    # def _mat(self,path,partition):
    #     return self._array(path,partition,'mat')

    # def _npy(self,path,partition):
    #     return self._array(path,partition,'npy')

    # def _npz(self,path,partition):
    #     return self._array(path,partition,'npy')

    # def _json(self,path,partition):
    #     return self._dataframe(path,partition,js=True)





if __name__=="__main__":
    acc={'Batch_size': 10,
 'Category': 'Local',
 'Columns': [],
 'Content': '',
 'Dataset_size': 3000,
 'Partition_list': [[70, 20, 10],[70, 20, 10]],
 'Path': ['C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\mnist_split\\mnist_input.npy',
            'C:\\Users\\Robert\\Documents\\PerceptiLabs\\PereptiLabsPlatform\\Data\\mnist_split\\mnist_input - Copy.npy'],
 'Seed': 71,
 'Shufflie': True,
 'Type': 'Data',
 'Warning': 'Could not find path'}
    hyp={'Batch_size': '2',
 'Data_partition': {'Test': '10', 'Training': '70', 'Validation': '20'},
 'Dropout_rate': '0.5',
 'Epochs': '1',
 'MaxSteps': '1000',
 'Save_model_every': '0',
 'Shuffle_data': True}
    dh=DataHandler(acc,hyp)
    
    
        
    
