import os
import pprint
import logging

from code_generator import CustomCodeGenerator, CodePart
from code_generator.datadata import DataDataCodeGenerator
from code_generator.tensorflow import ReshapeCodeGenerator, FullyConnectedCodeGenerator, ConvCodeGenerator, RecurrentCodeGenerator, CropCodeGenerator, WordEmbeddingCodeGenerator, GrayscaleCodeGenerator, OneHotCodeGenerator, ArgmaxCodeGenerator, MergeCodeGenerator, SoftmaxCodeGenerator


log = logging.getLogger(__name__)


class CodeHqNew:
    @staticmethod
    def get_code_generator(id_, content):
        type_ = content["Type"]
        props = content["Properties"]

        # if type_ == 'DataData':
        #     file_paths = content["Info"]["Properties"]["accessProperties"]["Path"]

        #     ######################################        
        #     # HACK TO MIMIC NEW STYLE USING SOURCE DICTS INSTEAD OF PATHS!
        #     sources = []
        #     partitions = []
        #     for path in file_paths:
        #         if os.path.isfile(path):
        #             src = {'path': path, 'type': 'file'}
        #         elif os.path.isdir(path):
        #             src = {'path': path, 'type': 'directory'}
        #         sources.append(src)
        #         partitions.append([70, 20, 10])
        #     ######################################
            
        #     code_generator = DataDataCodeGenerator(sources, partitions)
        #     return code_generator
        if type_ == 'DeepLearningFC':
            code_gen = FullyConnectedCodeGenerator(n_neurons=props["Neurons"],
                                                   activation=props["Activation_function"],
                                                   dropout=props["Dropout"],
                                                   keep_prob=1.0) # TODO: from where?
            return code_gen
        elif type_ == 'DeepLearningConv':
            code_gen = ConvCodeGenerator(conv_dim=props["Conv_dim"],
                                         patch_size=props["Patch_size"],
                                         feature_maps=props["Feature_maps"],
                                         stride=props["Stride"],
                                         padding=props["Padding"],
                                         dropout=props["Dropout"],
                                         keep_prob=1.0, # TODO: where does this come from?
                                         activation=props["Activation_function"],
                                         pool=props["PoolBool"],
                                         pooling=props["Pooling"],
                                         pool_area=props["Pool_area"],
                                         pool_stride=props["Pool_stride"])
            return code_gen
        elif type_ == 'DeepLearningDeconv':
            raise NotImplementedError("Deconv not implemented")
        elif type_ == 'DeepLearningRecurrent':
            code_gen = RecurrentCodeGenerator(version=props["Version"],
                                              time_steps=props["Time_steps"],
                                              neurons=props["Neurons"],
                                              return_sequences=False) # TODO: return_sequences from frontend
            return code_gen
        elif type_ == 'ProcessCrop':
            code_gen = CropCodeGenerator(offset_height=props["Offset_height"],
                                         offset_width=props["Offset_width"],
                                         target_height=props["Target_height"],
                                         target_width=props["Target_width"])
            return code_gen
        elif type_ == 'ProcessEmbed':            
            code_gen = WordEmbeddingCodeGenerator()
            return code_gen
        elif type_ == 'ProcessGrayscale':
            code_gen = GrayScaleCodeGenerator()
            return code_gen        
        elif type_ == 'ProcessOneHot':
            code_gen = OneHotCodeGenerator(n_classes=props["N_class"])
            return code_gen
        elif type_ == 'ProcessReshape':
            code_gen = ReshapeCodeGenerator(shape=props["Shape"], permutation=props["Permutation"])
            return code_gen
        elif type_ == 'TrainNormal':
            raise NotImplementedError("Train normal not implemented")
        elif type_ == 'TrainGenetic':
            raise NotImplementedError("Train genetic algorithm not implemented")
        elif type_ == 'TrainDynamic':
            raise NotImplementedError("Train dynamic routing not implemented")
        elif type_ == 'TrainReinforce':
            raise NotImplementedError("Train reinforce not implemented")
        elif type_ == 'MathArgmax':
            code_gen = ArgmaxCodeGenerator(dim=props["Dim"])
            return code_gen
        elif type_ == 'MathMerge':
            code_gen = MergeCodeGenerator(type_=props["Type"], merge_dim=props["Merge_dim"])
            return code_gen                                          
        elif type_ == 'MathSoftmax':
            code_gen = SoftmaxCodeGenerator()
            return code_gen
        elif type_ == 'MathSplit':
            raise NotImplementedError("Math split not implemented")
        elif 'Code' in content["Info"]:
            code_parts = [CodePart(name, code) for name, code in content["Info"]["Code"].items()]
            code_generator = CustomCodeGenerator(code_parts)
            return code_generator        
        else:
            log.error("Unrecognized layer. Type {}: {}".format(type_, pprint.pformat(content)))
            return None
        

if __name__ == "__main__":
    import json
    from graph import Graph
    
    with open('net.json', 'r') as f:
        json_network = json.load(f)

    graph = Graph(json_network["Layers"])

    generator_graph = dict()
    
    for id_, content in graph.graphs.items():
        code_gen = CodeHqNew.get_code_generator(id_, content)
        generator_graph[id_] = code_gen
        print("-----------------")
        print(code_gen)
        print(code_gen.get_code())
        print("-----------------")        
        


# class CodeHQ(object):
#     def get_code(self, layer_type, properties, X):
#         """Dispatch method"""
#         #method_name = str(layer.type)
#         method_name=layer_type
#         # Get the method from 'self'. Default to a lambda.
#         method = getattr(self, method_name, lambda: "Error")
#         # Call the method as we return it
#         return method(properties, X)
 
#     def ProcessOneHot(self,properties, X):
#         hiddenstring="""
        
#         """

#         # train_tmp=np.zeros((np.shape(train_output_data)[0],X))
                        
#         # train_output_data=list(np.array(train_output_data).astype("int"))
        
#         # if len(outputList[0].output)>1:
#         #         idx=np.meshgrid(*([np.arange(np.shape(train_output_data)[0])]+[np.arange(i) for i in X[0:-1]]),indexing='ij')
#         #         train_tmp[[i for i in idx]+[train_output_data]]=1
#         # else:
#         #         train_tmp[np.arange(np.shape(train_output_data)[0]),train_output_data]=1
                
#         # Y=train_tmp

#         showstring="Y=tf.one_hot(tf.cast(X,dtype=tf.int32),"+properties['N_class']+")"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring
 
#     def ProcessCrop(self,properties, X):
#         hiddenstring="""

#         """
#         #showstring="Y=X[X[x1]:X[x2],X[y1]:X[y2]]"
#         showstring="Y=tf.image.crop_to_bounding_box(X, "+properties["Offset_height"]+", "+properties["Offset_width"]+", "+properties["Target_height"]+", "+properties["Target_width"]+")"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring
 
#     def ProcessReshape(self,properties, X):
#         hiddenstring="""

#         """
#         showstring="Y=tf.reshape(X, [-1]+[layer_output for layer_output in "+str(properties["Shape"])+"]);    \
#         Y=tf.transpose(Y,perm="+str([0]+[i+1 for i in properties["Permutation"]])+")"
#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring

#     def ProcessEmbed(self,properties, X):
#         hiddenstring="""

#         """

#         # showstring="vocab=[];   \
#         # sentence_len=[];    \
#         # for sentence in X:; \
#         #     vocab+=list(np.unique(sentence));   \
#         #     sentence_len.append(len(sentence)); \
#         # vocab_id=list(enumerate(list(np.unique(vocab))));   \
#         # max_sentence_len=max(sentence_len); \
#         # Y=np.zeros([len(X),max_sentence_len]);  \
#         # for i in range(len(X)):;    \
#         #     for id_tuple in vocab_id:;  \
#         #         idx=np.where(id_tuple[1]==np.array(X[i]));  \
#         #         Y[i][idx]=id_tuple[0]+1;    \
#         # Y=tf.constant(Y)"

#         # showstring="sentences = tf.constant(lines); \
#         # words = tf.string_split(sentences);    \
#         # PADWORD='XZYQ'; \
#         # sentence_lengths=tf.strings.length(words, unit='UTF8_CHAR');  \
#         # MAX_DOCUMENT_LENGTH=tf.argmax(string_lengths);  \
#         # N_WORDS=words.get_shape().as_list()[0];  \
#         # EMBEDDING_SIZE=10;    \
#         # densewords = tf.sparse_tensor_to_dense(words, default_value=PADWORD);   \
#         # numbers = table.lookup(densewords); \
#         # padding = tf.constant([[0,0],[0,MAX_DOCUMENT_LENGTH]]); \
#         # padded = tf.pad(numbers, padding);  \
#         # sliced = tf.slice(padded, [0,0], [-1, MAX_DOCUMENT_LENGTH]);    \
#         # embeds = tf.contrib.layers.embed_sequence(sliced, vocab_size=N_WORDS, embed_dim=EMBEDDING_SIZE);    \
#         # Y=embeds"

#         showstring="words = tf.string_split(X); \
#         vocab_size=words.get_shape().as_list()[0]; \
#         embed_size=10;  \
#         embedding = tf.Variable(tf.random_uniform((vocab_size, embed_size), -1, 1));    \
#         Y = tf.nn.embedding_lookup(embedding, X)"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring
 
#     def ProcessGrayscale(self,properties, X):
#         hiddenstring="""

#         """
#         # showstring="r, g, b = X[:,:,0], X[:,:,1], X[:,:,2]; \
#         # Y = 0.2989 * r + 0.5870 * g + 0.1140 * b"
#         if X.get_shape().as_list()[-1]==3:
#             showstring="Y=tf.image.rgb_to_grayscale(X)"
#         else:
#             showstring="Y=X"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring
 
#     def DeepLearningFC(self,properties, X):
#         hiddenstring="""

#         """
#         input_size=1
#         #for element in [1024,683,3]:
#         #for element in [4]:
#         #for element in [784,1]:
#         for element in X.get_shape().as_list()[1:]:
#             input_size*=element
#         input_size=str(input_size)

#         if properties['Dropout']:
#             showstring="shape=["+input_size+","+properties["Neurons"]+"];  \
#             initial = tf.truncated_normal(shape, stddev=0.1);   \
#             W=tf.Variable(initial); \
#             initial = tf.constant(0.1, shape=["+properties["Neurons"]+"]); \
#             b=tf.Variable(initial); \
#             flat_node=tf.cast(tf.reshape(X,[-1,"+input_size+"]),dtype=tf.float32); \
#             node=tf.matmul(flat_node,W); \
#             node=tf.nn.dropout(node,"+"keep_prob"+");  \
#             node=node+b"
#         else:
#             showstring="shape=["+input_size+","+properties["Neurons"]+"];  \
#             initial = tf.truncated_normal(shape, stddev=0.1);   \
#             W=tf.Variable(initial); \
#             initial = tf.constant(0.1, shape=["+properties["Neurons"]+"]); \
#             b=tf.Variable(initial); \
#             flat_node=tf.cast(tf.reshape(X,[-1,"+input_size+"]),dtype=tf.float32); \
#             node=tf.matmul(flat_node,W)+b"

#         showstring=showstring+"\n"+self.activation(properties, X)

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring

#     def DeepLearningConv(self,properties, X):
#         hiddenstring="""

#         """

#         if properties["Conv_dim"] == "Automatic":
#             properties["Conv_dim"] = str(len(X.get_shape())-1) + "D" 
#         if properties['Dropout']:
#             if properties["Conv_dim"] == "1D":
#                 showstring="shape=["+properties["Patch_size"]+",3,"+properties["Feature_maps"]+"];  \
#                 initial = tf.truncated_normal(shape, stddev=np.sqrt(2 / ("+properties["Patch_size"]+"**2 * "+properties["Feature_maps"]+"))); \
#                 W = tf.Variable(initial);   \
#                 initial = tf.constant(0.1, shape=["+properties["Feature_maps"]+"]);    \
#                 b=tf.Variable(initial); \
#                 node = tf.nn.conv1d(X, W, "+properties["Stride"]+", padding="+properties["Padding"]+");   \
#                 node=tf.nn.dropout(node, "+"keep_prob"+"); \
#                 node=node+b"
#             elif properties["Conv_dim"] == "2D":
#                 showstring="shape=["+properties["Patch_size"]+","+properties["Patch_size"]+",3,"+properties["Feature_maps"]+"];    \
#                 print(X.dtype);\
#                 initial = tf.truncated_normal(shape, stddev=np.sqrt(2 / ("+properties["Patch_size"]+"**2 * "+properties["Feature_maps"]+"))); \
#                 W = tf.Variable(initial);   \
#                 initial = tf.constant(0.1, shape=["+properties["Feature_maps"]+"]);    \
#                 b=tf.Variable(initial); \
#                 node = tf.nn.conv2d(X, W, strides=[1, "+properties["Stride"]+", "+properties["Stride"]+", 1], padding="+properties["Padding"]+");    \
#                 node=tf.nn.dropout(node, "+"keep_prob"+"); \
#                 node=node+b"
#             elif properties["Conv_dim"] == "3D":
#                 showstring="shape=["+properties["Patch_size"]+","+properties["Patch_size"]+","+properties["Patch_size"]+",X.get_shape()[-1].value,"+properties["Feature_maps"]+"];  \
#                 initial = tf.truncated_normal(shape, stddev=np.sqrt(2 / ("+properties["Patch_size"]+"**2 * "+properties["Feature_maps"]+"))); \
#                 W = tf.Variable(initial);   \
#                 initial = tf.constant(0.1, shape=["+properties["Feature_maps"]+"]);    \
#                 b=tf.Variable(initial); \
#                 node = tf.nn.conv3d(X, W, strides=[1, "+properties["Stride"]+", "+properties["Stride"]+", "+properties["Stride"]+", 1], padding="+properties["Padding"]+"); \
#                 node=tf.nn.dropout(node, "+"keep_prob"+"); \
#                 node=node+b"
#         else:
#             if properties["Conv_dim"] == "1D":
#                 showstring="shape=["+properties["Patch_size"]+",X.get_shape()[-1].value,"+properties["Feature_maps"]+"];  \
#                 initial = tf.truncated_normal(shape, stddev=np.sqrt(2 / ("+properties["Patch_size"]+"**2 * "+properties["Feature_maps"]+"))); \
#                 W = tf.Variable(initial);   \
#                 initial = tf.constant(0.1, shape=["+properties["Feature_maps"]+"]);    \
#                 b=tf.Variable(initial); \
#                 node = tf.nn.conv1d(X, W, "+properties["Stride"]+", padding="+properties["Padding"]+");   \
#                 node=node+b"
#             elif properties["Conv_dim"] == "2D":
#                 showstring="shape=["+properties["Patch_size"]+","+properties["Patch_size"]+",3,"+properties["Feature_maps"]+"];    \
#                 initial = tf.truncated_normal(shape, stddev=np.sqrt(2 / ("+properties["Patch_size"]+"**2 * "+properties["Feature_maps"]+"))); \
#                 W = tf.Variable(initial);   \
#                 initial = tf.constant(0.1, shape=["+properties["Feature_maps"]+"]);    \
#                 b=tf.Variable(initial); \
#                 node = tf.nn.conv2d(X, W, strides=[1, "+properties["Stride"]+", "+properties["Stride"]+", 1], padding="+properties["Padding"]+");    \
#                 node=node+b"
#             elif properties["Conv_dim"] == "3D":
#                 showstring="shape=["+properties["Patch_size"]+","+properties["Patch_size"]+","+properties["Patch_size"]+",X.get_shape()[-1].value,"+properties["Feature_maps"]+"];  \
#                 initial = tf.truncated_normal(shape, stddev=np.sqrt(2 / ("+properties["Patch_size"]+"**2 * "+properties["Feature_maps"]+"))); \
#                 W = tf.Variable(initial);   \
#                 initial = tf.constant(0.1, shape=["+properties["Feature_maps"]+"]);    \
#                 b=tf.Variable(initial); \
#                 node = tf.nn.conv3d(X, W, strides=[1, "+properties["Stride"]+", "+properties["Stride"]+", "+properties["Stride"]+", 1], padding="+properties["Padding"]+"); \
#                 node=node+b"

#         showstring=showstring+"\n"+self.activation(properties, X)

#         if properties["PoolBool"]:
#             if properties["Pooling"] == "Max":
#                 showstring_pool="Y=max_pool(Y, "+properties["Pool_area"]+", "+properties["Pool_stride"]+","+properties["Pool_padding"]+","+properties["Conv_dim"]+")"
#             elif properties["Pooling"] == "Mean":
#                 showstring_pool="Y=tf.nn.pool(Y, window_shape="+properties["Pool_area"]+", pooling_type='AVG',"+properties["Pool_padding"]+", strides="+properties["Pool_stride"]+")"
#         else:
#             showstring_pool=""

#         showstring=showstring+"\n"+showstring_pool

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring
 
#     def DeepLearningDeconv(self,properties, X):
#         hiddenstring="""

#         """

#         if properties["Deconv_dim"] == "Automatic":
#             properties["Deconv_dim"] = str(abs(len(X.get_shape())-1)) + "D"
#         if properties['Dropout']:
#             if properties["Deconv_dim"] == "1D":
#                 showstring="shape=["+properties["Stride"]+",X.get_shape()[-1].value,"+properties["Feature_maps"]+"];  \
#                 initial = tf.truncated_normal(shape, stddev=np.sqrt(2 / ("+properties["Stride"]+"**2 * "+properties["Feature_maps"]+"))); \
#                 W = tf.Variable(initial);   \
#                 initial = tf.constant(0.1, shape=["+properties["Feature_maps"]+"]);    \
#                 b=tf.Variable(initial); \
#                 output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*"+properties["Stride"]+" for node_shape in X.get_shape().as_list()[1:-1]]+["+properties["Feature_maps"]+"]);    \
#                 node = tf.nn.conv1d_transpose(X, W, output_shape, "+properties["Stride"]+", padding="+properties["Padding"]+");   \
#                 node=tf.nn.dropout(node, "+"keep_prob"+"); \
#                 node=node+b"
#             elif properties["Deconv_dim"] == "2D":
#                 showstring="shape=["+properties["Stride"]+","+properties["Stride"]+",X.get_shape()[-1].value,"+properties["Feature_maps"]+"];    \
#                 initial = tf.truncated_normal(shape, stddev=np.sqrt(2 / ("+properties["Stride"]+"**2 * "+properties["Feature_maps"]+"))); \
#                 W = tf.Variable(initial);   \
#                 initial = tf.constant(0.1, shape=["+properties["Feature_maps"]+"]);    \
#                 b=tf.Variable(initial); \
#                 output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*"+properties["Stride"]+" for node_shape in X.get_shape().as_list()[1:-1]]+["+properties["Feature_maps"]+"]);    \
#                 node = tf.nn.conv2d_transpose(X, W, output_shape, strides=[1, "+properties["Stride"]+", "+properties["Stride"]+", 1], padding="+properties["Padding"]+");    \
#                 node=tf.nn.dropout(node, "+"keep_prob"+"); \
#                 node=node+b"
#             elif properties["Deconv_dim"] == "3D":
#                 showstring="shape=["+properties["Stride"]+","+properties["Stride"]+","+properties["Stride"]+",X.get_shape()[-1].value,"+properties["Feature_maps"]+"];  \
#                 initial = tf.truncated_normal(shape, stddev=np.sqrt(2 / ("+properties["Stride"]+"**2 * "+properties["Feature_maps"]+"))); \
#                 W = tf.Variable(initial);   \
#                 initial = tf.constant(0.1, shape=["+properties["Feature_maps"]+"]);    \
#                 b=tf.Variable(initial); \
#                 output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*"+properties["Stride"]+" for node_shape in X.get_shape().as_list()[1:-1]]+["+properties["Feature_maps"]+"]);    \
#                 node = tf.nn.conv3d_transpose(X, W, output_shape, strides=[1, "+properties["Stride"]+", "+properties["Stride"]+", "+properties["Stride"]+", 1], padding="+properties["Padding"]+"); \
#                 node=tf.nn.dropout(node, "+"keep_prob"+"); \
#                 node=node+b"
#         else:
#             if properties["Deconv_dim"] == "1D":
#                 showstring="shape=["+properties["Stride"]+",X.get_shape()[-1].value,"+properties["Feature_maps"]+"];  \
#                 initial = tf.truncated_normal(shape, stddev=np.sqrt(2 / ("+properties["Stride"]+"**2 * "+properties["Feature_maps"]+"))); \
#                 W = tf.Variable(initial);   \
#                 initial = tf.constant(0.1, shape=["+properties["Feature_maps"]+"]);    \
#                 b=tf.Variable(initial); \
#                 output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*"+properties["Stride"]+" for node_shape in X.get_shape().as_list()[1:-1]]+["+properties["Feature_maps"]+"]);    \
#                 node = tf.nn.conv1d_transpose(X, W, output_shape, "+properties["Stride"]+", padding="+properties["Padding"]+");   \
#                 node=node+b"
#             elif properties["Deconv_dim"] == "2D":
#                 showstring="shape=["+properties["Stride"]+","+properties["Stride"]+",X.get_shape()[-1].value,"+properties["Feature_maps"]+"];    \
#                 initial = tf.truncated_normal(shape, stddev=np.sqrt(2 / ("+properties["Stride"]+"**2 * "+properties["Feature_maps"]+"))); \
#                 W = tf.Variable(initial);   \
#                 initial = tf.constant(0.1, shape=["+properties["Feature_maps"]+"]);    \
#                 b=tf.Variable(initial); \
#                 output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*"+properties["Stride"]+" for node_shape in X.get_shape().as_list()[1:-1]]+["+properties["Feature_maps"]+"]);    \
#                 node = tf.nn.conv2d_transpose(X, W, output_shape, strides=[1, "+properties["Stride"]+", "+properties["Stride"]+", 1], padding="+properties["Padding"]+");    \
#                 node=node+b"
#             elif properties["Deconv_dim"] == "3D":
#                 showstring="shape=["+properties["Stride"]+","+properties["Stride"]+","+properties["Stride"]+",X.get_shape()[-1].value,"+properties["Feature_maps"]+"];  \
#                 initial = tf.truncated_normal(shape, stddev=np.sqrt(2 / ("+properties["Stride"]+"**2 * "+properties["Feature_maps"]+"))); \
#                 W = tf.Variable(initial);   \
#                 initial = tf.constant(0.1, shape=["+properties["Feature_maps"]+"]);    \
#                 b=tf.Variable(initial); \
#                 output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*"+properties["Stride"]+" for node_shape in X.get_shape().as_list()[1:-1]]+["+properties["Feature_maps"]+"]);    \
#                 node = tf.nn.conv3d_transpose(X, W, output_shape, strides=[1, "+properties["Stride"]+", "+properties["Stride"]+", "+properties["Stride"]+", 1], padding="+properties["Padding"]+"); \
#                 node=node+b"

#         showstring=showstring+"\n"+self.activation(properties, X)

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring
 
#     def DeepLearningRecurrent(self,properties, X):
#         hiddenstring="""

#         """
#         if properties['Version'] == "LSTM":
#             showstring="node=tf.reshape(X,[-1, "+properties["Time_steps"]+", np.prod(X.get_shape().as_list()[1:])]); \
#             cell = tf.nn.rnn_cell.LSTMCell("+properties["Neurons"]+", state_is_tuple=True); \
#             rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, node, dtype=node.dtype); \
#             Y=tf.reshape(rnn_outputs,[-1,cell.output_size])"

#         elif properties['Version'] == "GRU":
#             showstring="node=tf.reshape(X,[-1, "+properties["Time_steps"]+", np.prod(X.get_shape().as_list()[1:])]); \
#             cell = tf.nn.rnn_cell.GRUCell("+properties["Neurons"]+"); \
#             rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, node, dtype=node.dtype); \
#             Y=tf.reshape(rnn_outputs,[-1,cell.output_size])"

#         elif properties['Version'] == "RNN":
#             showstring="node=tf.reshape(X,[-1, "+properties["Time_steps"]+", np.prod(X.get_shape().as_list()[1:])]); \
#             cell = tf.nn.rnn_cell.BasicRNNCell("+properties["Neurons"]+"); \
#             rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, node, dtype=node.dtype); \
#             Y=tf.reshape(rnn_outputs,[-1,cell.output_size])"
#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring

#     def activation(self,properties, X):
#         if properties["Activation_function"] == "Sigmoid":
#             node = 'Y=tf.sigmoid(node)'
#         elif properties["Activation_function"] == "ReLU":
#             node = 'Y=tf.nn.relu(node)'
#         elif properties["Activation_function"] == "Tanh":
#             node = 'Y=tf.tanh(node)'
#         elif properties["Activation_function"] == "None":
#             node = 'Y=node'
#         return node

#     def MathArgmax(self,properties, X):
#         hiddenstring="""

#         """
#         showstring="Y=tf.argmax(X,"+properties["Dim"]+")"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring
 
#     def MathSoftmax(self,properties, X):
#         hiddenstring="""

#         """
#         showstring="Y=tf.nn.softmax(X)"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring
 
#     def MathSplit(self,properties, X):
#         hiddenstring="""

#         """
#         showstring="""

#         """
#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring

#     def MathMerge(self,properties, X):
#         hiddenstring="""

#         """
#         #import tensorflow as tf
#         #print([list(X.values())[i] for i in range(1,len(list(X.keys())),2)])
#         #print(tf.add_n([list(X.values())[i] for i in range(1,len(list(X.keys())),2)]))
#         #print(tf.add_n([list(X.values())[i] for i in range(1,len(list(X.keys())),2)]).get_shape())
#         idxlist=[]
#         for key,value in X.items():
#             try:
#                 int(key)
#             # if len(key.split("_"))>1:
#                 idxlist.append(key)
#             except:
#                 pass
                
#         if properties["Type"] == "Concat":
#             showstring="Y=X['"+idxlist[0]+"']"
#             showstring=showstring+"\n"+"for c in range(2,len(list(X.values())),2):"+"\n\t"+"Y=tf.concat([Y, list(X.values())[c]],"+properties["Merge_dim"]+")"+"\n"

#         elif properties["Type"] == "Add":
#             if len(idxlist)==2:
#                 showstring="Y=tf.add(X['"+idxlist[0]+"'],X['"+idxlist[1]+"'])"
#             else:
#                 #showstring="Y=tf.add_n([list(X.values())[i] for i in range(1,len(list(X.keys())),2)]).get_shape()"
#                 showstring="Y=X['"+idxlist[0]+"']"
#                 showstring=showstring+"\n"+"for i in range(2,len(list(X.values())),2):"+"\n\t"+"Y=tf.add(list(X.values())[i],Y)"+"\n"

#         elif properties["Type"] == "Multi":
#             if len(idxlist)==2:
#                 showstring="Y=tf.multiply(X['"+idxlist[0]+"'],X['"+idxlist[1]+"'])"
#             else:
#                 showstring="Y=X['"+idxlist[0]+"']"
#                 showstring=showstring+"\n"+"for i in range(2,len(list(X.values())),2):"+"\n\t"+"Y=tf.multiply(list(X.values())[i],Y)"+"\n"

#         elif properties["Type"] == "Sub":
#             if len(idxlist)==2:
#                 showstring="Y=tf.subtract(X['"+idxlist[0]+"'],X['"+idxlist[1]+"'])"
#             else:
#                 showstring="Y=X['"+idxlist[0]+"']"
#                 showstring=showstring+"\n"+"for i in range(2,len(list(X.values())),2):"+"\n\t"+"Y=tf.subtract(list(X.values())[i],Y)"+"\n"

#         elif properties["Type"] == "Div":
#             if len(idxlist)==2:
#                 showstring="Y=tf.div(X['"+idxlist[0]+"'],X['"+idxlist[1]+"'])"
#             else:
#                 showstring="Y=X['"+idxlist[0]+"']"
#                 showstring=showstring+"\n"+"for i in range(2,len(list(X.values())),2):"+"\n\t"+"Y=tf.subtract(list(X.values())[i],Y)"+"\n"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring
    
 
#     def PointWise(self,properties, X):
#         hiddenstring="""

#         """
#         showstring="""

#         """
#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring
 
 
#     def Loss(self,properties, network_output, labels):
#         hiddenstring="""

#         """
        
#         if properties['Loss'] == 'Cross_entropy':
#             showstring="flat_logits = tf.reshape("+network_output+", [-1, "+properties['N_class']+"]);   \
#             flat_labels = tf.reshape("+labels+", [-1, "+properties['N_class']+"]);    \
#             loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=flat_labels, logits=flat_logits))"
        
#         if properties['Loss'] == 'Quadratic':
#             showstring="loss=tf.losses.mean_squared_error("+labels+","+network_output+")"
#             #if RL_Qlearning:
#             #    Y=tf.abs(tf.add(properties['Labels'],X))
#             #else:
        
#         if properties['Loss'] == 'W_cross_entropy':
#             showstring="flat_logits = tf.reshape("+network_output+", [-1, "+properties['N_class']+"]);   \
#             flat_labels = tf.reshape("+labels+", [-1, "+properties['N_class']+"]);    \
#             class_weights = tf.constant("+properties['Class_weights']+", dtype=tf.float32); \
#             loss = tf.reduce_mean(tf.nn.weighted_cross_entropy_with_logits(flat_labels, flat_logits, "+properties['Class_weights']+"))"

#         if properties['Loss'] == 'Dice':
#             showstring="eps = 1e-5; \
#             prediction = "+network_output+"; \
#             intersection = tf.reduce_sum(tf.multiply(prediction, "+labels+"));    \
#             union =  eps + tf.reduce_sum(tf.multiply(prediction, prediction)) + tf.reduce_sum(tf.multiply("+labels+", "+labels+")); \
#             cost_tmp = (2 * intersection/ (union)); \
#             cost_clip = tf.clip_by_value(cost_tmp, eps, 1.0-eps);   \
#             loss = 1 - cost_clip"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring
 
#     def Optimizer(self,properties, X):
#         hiddenstring="""

#         """
#         if properties['Optimizer'] == 'SGD':
#             showstring="optimizer = tf.train.GradientDescentOptimizer("+properties['Learning_rate']+").minimize(loss);  \
#             Y=optimizer"
            
#         elif properties['Optimizer'] == 'Momentum':
#             showstring="global_step = tf.Variable(0);   \
#             start_learning_rate = "+properties['Learning_rate']+";  \
#             learning_rate_momentum = tf.train.exponential_decay(learning_rate=start_learning_rate, global_step=global_step, decay_steps="+properties['Training_iters']+", decay_rate="+properties['Decay']+", staircase=True);  \
#             Y = tf.train.MomentumOptimizer(learning_rate=learning_rate_momentum, momentum="+properties['Momentum']+").minimize(loss, global_step=global_step)"
            
#         elif properties['Optimizer'] == 'ADAM':
#             showstring="Y = tf.train.AdamOptimizer("+properties['Learning_rate']+",beta1="+properties['Beta_1']+",beta2="+properties['Beta_2']+").minimize(loss)"
            
#         elif properties['Optimizer'] == 'RMSprop':
#             showstring="Y = tf.train.RMSPropOptimizer("+properties['Learning_rate']+",decay="+properties['Decay']+",momentum="+properties['Momentum']+").minimize(loss)"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring

#     def Accuracy(self,properties, network_output, labels):
#         hiddenstring="""

#         """
        
#         if int(properties['N_class'])<=1:
#             showstring="correct_prediction = tf.equal("+network_output+", "+labels+");    \
#             accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))"
#         else:
#             showstring="arg_output=tf.argmax("+network_output+",-1); \
#             arg_label=tf.argmax("+labels+",-1);   \
#             correct_prediction = tf.equal(arg_output, arg_label);   \
#             accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))"
#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring

#     def TrainNormal(self,properties, X):
#         hiddenstring="""

#         """
#         #properties['N_class']=str(list(X.values())[-1].get_shape().as_list()[-1])
#         for key,_ in X.items():
#             if len(key.split("_"))>1:
#                 if str(key.split("_")[0]) == "OneHot" or str(key.split("_")[0]) == "Data":
#                     labels="X['"+str(key)+"']"
#                 else:
#                     network_output="X['"+str(key)+"']"
        
#         loss=self.Loss(properties, network_output, labels)
#         optimizer=self.Optimizer(properties, X)
#         accuracy=self.Accuracy(properties, network_output, labels)
#         showstring=loss+"\n"+optimizer+"\n"+accuracy
#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring

#     def TakeAction(self, properties):

#     #     explore_probability=tf.add(eps_min,tf.multiply(tf.minus(eps,eps_min),tf.exp(tf.multiply(tf.multiply(eps_decay,tf.constant(-1)),decay_step))))
#     #     exp_exp_tradeoff=tf.random()
#     #     def f1(): return tf.random(action_space)
#     #     def f2(): return tf.reduce_max(action)
#     #     taken_action = tf.cond(tf.less(explore_probability, exp_exp_tradeoff), f1, f2)
#                 # actionstring="exp_exp_tradeoff = np.random.rand();    \
#         # explore_probability = "+properties['Eps_min']+" + ("+properties['Eps']+" - "+properties['Eps_min']+") * np.exp(-"+properties['Eps_decay']+" * self.decay_step);  \
#         # if (explore_probability < exp_exp_tradeoff):;   \
#         #     action = self.randomAction();   \
#         # else:;  \
#         #     action = self.predictedAction(sess)"

#         actionString1="exp_exp_tradeoff = np.random.rand()"
#         actionString2=actionString1+"\n"+"explore_probability = "+properties['Eps_min']+" + ("+properties['Eps']+" - "+properties['Eps_min']+") * np.exp(-"+properties['Eps_decay']+" * self.decay_step)"
#         actionstring=actionString2+"\n"+"if (explore_probability < exp_exp_tradeoff):"+"\n\t"+"action = self.randomAction()"+"\n"+"else:"+"\n\t"+"action = self.predictedAction(sess)"+"\n"     
#         return actionstring

#     def LossParameters(self, properties, X):

#         # def f1(): return tf.stack([reward])
#         # def f2(): return tf.add(reward,tf.multiply(gamma,tf.reduce_max(target)))
#         # body = tf.cond(tf.equal(done, tf.constant(True)), f1, f2)
#         # x = tf.constant(list(range(batch_size)))
#         # cond = lambda i, x: i < batch_size
#         # r = tf.while_loop(cond, body, [i])

#         #showstring="tf.where("+properties['Placeholders']['Done']+","+properties['Placeholders']['Reward']+",tf.add("+properties['Placeholders']['Reward']+",tf.multiply(float("+properties['Gamma']+"),tf.reduce_max("+properties['Placeholders']['Target']+"))))"
#         showstring="tf.where(X['Done'],X['Reward'],tf.add(X['Reward'],tf.multiply("+properties['Gamma']+",tf.reduce_max(X['Target']))))"
#         return showstring

#     def TrainReinforce(self, properties, X):
#         hiddenstring="""

#         """
#         # for key,_ in X.items():
#         #     pos = [i for i,e in enumerate(key+'A') if e.isupper()]
#         #     string_parts = [key[pos[j]:pos[j+1]] for j in range(len(pos)-1)]
#         #     if len(string_parts)>1:
#         #         if str(string_parts[0]) == "Process" or str(string_parts[0]) == "Data":
#         #             labels="X['"+str(key)+"']"
#         #         else:
#         #             network_output="X['"+str(key)+"']"
#         #action=self.TakeAction()
#         properties['N_class']=1
#         for key,_ in X.items():
#             if key.isdigit() and key not in properties['Worker_outputs']:
#                 network_output="X['"+str(key)+"']['Y']"
        
#         logits="tf.reduce_sum(tf.multiply("+network_output+", X['Action']), reduction_indices = 1)"
#         labels=self.LossParameters(properties, X)
#         loss=self.Loss(properties, logits, labels)
#         optimizer=self.Optimizer(properties, X)
#         accuracy=self.Accuracy(properties, logits, labels)
#         showstring=loss+"\n"+optimizer+"\n"+accuracy
#         actionstring=self.TakeAction(properties)

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring, actionstring
 
#     def ClassicMLKMeans(self,properties, X):
#         hiddenstring="""
#         """
#         from sklearn.cluster import KMeans
#         estimate=KMeans(n_clusters=3, init='k-means++', n_init=10, max_iter=100, tol=0.0001, precompute_distances='auto', verbose=0, random_state=None, copy_x=True, n_jobs=None, algorithm='auto');    \
#         print("Estimate: ",estimate)
#         Y=estimate.fit(X)
#         print("Y: ",Y)

#         showstring="estimate=KMeans(n_clusters=3, init='k-means++', n_init=10, max_iter=100, tol=0.0001, precompute_distances='auto', verbose=0, random_state=None, copy_x=True, n_jobs=None, algorithm='auto');    \
#         Y=tf.constant(estimate.fit(X))"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring

#     def ClassicMLDbscans(self,properties, X):
#         hiddenstring="""
#         """
#         showstring="estimate=DBSCAN(eps=0.5, min_samples=5, metric=’euclidean’, metric_params=None, algorithm=’auto’, leaf_size=30, p=None, n_jobs=None);   \
#         Y=tf.constant(estimate.fit(X))"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring
 
#     def ClassicMLKNN(self,properties, X):
#         hiddenstring="""
#         """
#         if properties["Type"] == "Classification":
#             showstring="estimator=KNeighborsClassifier(n_neighbors=5, weights=’uniform’, algorithm=’auto’, leaf_size=30, p=2, metric=’minkowski’, metric_params=None, n_jobs=None); \
#             Y=tf.constant(estimator.fit(X,properties['Labels']))"
#         elif properties["Type"] == "Regression":
#             showstring="estimator=KNeighborsRegressor(n_neighbors=5, weights=’uniform’, algorithm=’auto’, leaf_size=30, p=2, metric=’minkowski’, metric_params=None, n_jobs=None);  \
#             Y=tf.constant(estimator.fit(X,properties['Labels']))"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring
 
#     def ClassicMLRandomForest(self,properties, X):
#         hiddenstring="""
#         """
#         if properties["Type"] == "Classification":
#             showstring="estimator=RandomForestClassifier(n_estimators=’warn’, criterion=’gini’, max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=’auto’, max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=None, random_state=None, verbose=0, warm_start=False, class_weight=None);  \
#             Y=tf.constant(estimator.fit(X,properties['Labels']))"
#         elif properties["Type"] == "Regression":
#             showstring="estimator=RandomForestRegressor(n_estimators=’warn’, criterion=’mse’, max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=’auto’, max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=None, random_state=None, verbose=0, warm_start=False);   \
#             Y=tf.constant(estimator.fit(X,properties['Labels']))"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring

#     def ClassicMLSVM(self,properties, X):
#         hiddenstring="""
#         """
#         if properties["Type"] == "Anomalie":
#             showstring="estimator=OneClassSVM(kernel=’rbf’, degree=3, gamma=’auto_deprecated’, coef0=0.0, tol=0.001, nu=0.5, shrinking=True, cache_size=200, verbose=False, max_iter=-1, random_state=None);    \
#             Y=tf.constant(estimator.fit_predict(X))"
#         elif properties["Type"] == "Classification":
#             showstring="estimator=NuSVC(nu=0.5, kernel=’rbf’, degree=3, gamma=’auto_deprecated’, coef0=0.0, shrinking=True, probability=False, tol=0.001, cache_size=200, class_weight=None, verbose=False, max_iter=-1, decision_function_shape=’ovr’, random_state=None); \
#             Y=tf.constant(estimator.fit(X,properties['Labels']))"
#         elif properties["Type"] == "Regression":
#             showstring="estimator=NuSVR(nu=0.5, C=1.0, kernel=’rbf’, degree=3, gamma=’auto_deprecated’, coef0=0.0, shrinking=True, tol=0.001, cache_size=200, verbose=False, max_iter=-1);  \
#             Y=tf.constant(estimator.fit(X,properties['Labels']))"

#         #layer["Code"]=(showstring,hiddenstring)
#         return showstring

# #Statscreen for Normal:

# #Statscreen for Reinforcement:

# #Viewbox for FC:

# #Viewbox for Conv:

# #Viewbox for Deconv:

# #Viewbox for Recurrent:

# #Viewbox for Add:

# #Viewbox for Subtract:

# #Viewbox for Divide:

# #Viewbox for Multiply:

# #Viewbox for Argmax:

# #Viewbox for Softmax:
