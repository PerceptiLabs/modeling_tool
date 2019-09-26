# import tensorflow as tf
# from datahandler import DataHandler
# from environmenthandler import EnvironmentHandler

# class Data(object):
#     def __init__(self,dataProperties,hyperparameters):
#         self.type=dataProperties["Type"]
#         self._init_source(dataProperties,hyperparameters)

#     def _init_source(self,dataProperties,hyperparameters):
#         # print(self.type)
#         if self.type=='Data':
#             self.source_obj=DataHandler(dataProperties["accessProperties"],hyperparameters)
#             self.placeholder=self.prepareData(hyperparameters)
#         elif self.type=='Environment':
#             self.source_obj=EnvironmentHandler(dataProperties["accessProperties"])
#             self.placeholder=self.prepareEnvironment()

#     def prepareData(self, hyperparameters):
#         # Creates a placeholder with the data and returns the placeholder
#         # self.data_placeholder=self.source_obj.placeholder     #Not needed since we just return the iterator instead
#         # Creates the different datasets
#         self.data=self.source_obj.data
#         # Creates the different datasets and creates an iterator and return it as input to next op
#         iterator = tf.data.Iterator.from_structure(self.source_obj.train_dataset.output_types, self.source_obj.train_dataset.output_shapes)

#         print("OUTPUT SHAPES", self.source_obj.train_dataset.output_shapes)
        
#         if self.source_obj.train_data_size>0:
#             self.train_iterator = iterator.make_initializer(self.source_obj.train_dataset)
#         if self.source_obj.validation_data_size>0:
#             self.validation_iterator = iterator.make_initializer(self.source_obj.validation_dataset)
#         if self.source_obj.test_data_size>0:
#             self.test_iterator = iterator.make_initializer(self.source_obj.test_dataset)

#         print("DATASET SHAPE!!!!!!!!!!!!!!!", self.source_obj.train_dataset.output_shapes)
#         # #CHANGED
#         # try:
#         #     self.filename,next_elements = iterator.get_next()
#         # except:
#         #     next_elements = iterator.get_next()
#         next_elements = iterator.get_next()
#         return next_elements  

#     def prepareEnvironment(self):
#         self.data_placeholder=self.source_obj.prepareEnvironment()
#         return self.data_placeholder

#     def reinforcePlaceholders(self):
#         return self.source_obj.placeholders
   
#     def getData(self, save_var, batch_size, iteration, status, valuekey, sess, keep_prob):
#         #Decide if DataNormal or DataEnvironment
#         if self.type == "Data":
#             pass
#             # if status=='Training':
#             #     sess.run(self.train_iterator,feed_dict={self.data_placeholder: self.data})
#             # elif status=='Validation':
#             #     sess.run(self.validation_iterator,feed_dict={self.data_placeholder: self.data})
#             # elif status=='Testing':
#             #     sess.run(self.test_iterator,feed_dict={self.data_placeholder: self.data})

#         elif self.type == "Environment":
#             # Read 1 sample at a time or batch from experienced replay
#             # if iteration==0:
#             #     self.source_obj.initBuffer(batch_size)
#             data = self.source_obj.getBuffer(valuekey, iteration, sess, save_var,keep_prob)
#             return data
#         else:
#             raise NameError("Could not find type")

#     def putBuffer(self,iteration,sess,keep_prob):
#         return self.source_obj.putBuffer(iteration, sess, keep_prob)
