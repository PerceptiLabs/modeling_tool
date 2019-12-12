import tensorflow as tf
from tensorflow.python import pywrap_tensorflow
import re
from tensorflow.core.protobuf import saver_pb2
from tensorflow.python.training import saver as saver_lib
from tensorflow.python.framework import importer
from tensorflow.python.platform import gfile
from google.protobuf import text_format
from tensorflow.python.framework import importer
from tensorflow.python.framework import tensor_util
import traceback

class extractCheckpointInfo():
    def __init__(self, end_points=[], graph_def_path=None, input_checkpoint=None, sess=None):
        self.remove_name_list=[]
        self.end_points=end_points
        self.graph_def_path=graph_def_path
        self.input_checkpoint=input_checkpoint
        self.sess=sess
        print("Session:", self.sess)
        # self.sess=self.initializeSession(end_points,graph_def_path,input_checkpoint)
        

    # def getFiles(value):
    #     if type(value).__name__=="str" and not value.split("/")[-1].split(".")[-1]:
    #         #Then its a folder
    #         return ""
    #     else:
    #         graph_def_path=""
    #         checkpoint=""
    #         for _file in value:
    #             if ".ckpt" in _file:
    #                 path, fileName=os.path.split(_file)
    #                 if "ckpt" in fileName.split(".")[-1]:
    #                 checkpoint=_file
    #                 else:
    #                 newFileName=".".join(fileName.split(".")[0:-1])
    #                 print("NewFileName: ", newFileName)
    #                 checkpoint=os.path.join(path, newFileName)
                    
    #             elif any([pb in _file for pb in [".pb", ".pbtxt"]]):
    #                 graph_def_path=_file
    #             else:
    #                 raise Exception("File type not recognised")
    #         if graph_def_path and checkpoint:
    #             print(graph_def_path)
    #             print(checkpoint)
    #             return [graph_def_path, checkpoint]
    #         else:
    #             return ""

    def _has_no_variables(self,sess):
        for op in sess.graph.get_operations():
            if op.type.startswith("Variable") or op.type.endswith("VariableOp"):
                return False
        return True

    def getGraphDef(self,graph_def_path):
        type_pb=graph_def_path.split(".")[-1]=="pb"
        graph_def = tf.GraphDef()
        mode = "rb" if type_pb else "r"
        with gfile.GFile(graph_def_path, mode) as f:
            if type_pb:
                graph_def.ParseFromString(f.read())
            else:
                text_format.Merge(f.read(), graph_def)
        return graph_def


    def restoreSession(self):
        if not self.input_checkpoint or not self.graph_def_path:
            raise Exception("Missing checkpoint or graph def")

        tf.reset_default_graph()
        sess=tf.Session()
        sess.graph.as_default()
        graph_def=self.getGraphDef(self.graph_def_path)
        for node in graph_def.node:
            node.device = ""
        graph_def = tf.compat.v1.graph_util.extract_sub_graph(graph_def, self.end_points)

        self.graph_def=graph_def
        tf.import_graph_def(graph_def, name='')
        # _ = importer.import_graph_def(graph_def, name="")
        input_saver_def=None #If they have a SaverDef
        input_meta_graph_def=None  #If they have a MetaGraphDef
        input_saved_model_dir=None #If they have a folder with SavedModel inside

        checkpoint_version=saver_pb2.SaverDef.V2
        initializer_nodes=[]
        saved_model_tags=None



        if input_saver_def:
            saver = saver_lib.Saver(
                saver_def=input_saver_def, write_version=checkpoint_version)
            saver.restore(sess, self.input_checkpoint)
        elif input_meta_graph_def:
            restorer = saver_lib.import_meta_graph(
                input_meta_graph_def, clear_devices=True)
            restorer.restore(sess, self.input_checkpoint)
            if initializer_nodes:
                sess.run(initializer_nodes.replace(" ", "").split(","))
        elif input_saved_model_dir:
            if saved_model_tags is None:
                saved_model_tags = []
            # loader.load(sess, saved_model_tags, input_saved_model_dir)
        else:
            var_list = {}
            
            reader = pywrap_tensorflow.NewCheckpointReader(self.input_checkpoint)
            var_to_shape_map = reader.get_variable_to_shape_map() #Map between name and variable shape

            all_parition_variable_names = [
                tensor.name.split(":")[0]
                for op in sess.graph.get_operations()
                for tensor in op.values()
                if re.search(r"/part_\d+/", tensor.name)
                ]

            has_partition_var=False
            for key in var_to_shape_map:
                try:
                    tensor = sess.graph.get_tensor_by_name(key + ":0")
                    if any(key in name for name in all_parition_variable_names):
                        has_partition_var = True
                except KeyError:
                    # print(key)
                    self.remove_name_list.append(key)
                # This tensor doesn't exist in the graph (for example it's
                # 'global_step' or a similar housekeeping element) so skip it.
                    continue
                var_list[key] = tensor  #Map between name and tensor

            
            try:
                saver = saver_lib.Saver(
                    var_list=var_list, write_version=checkpoint_version)
            except TypeError as e:
                # `var_list` is required to be a map of variable names to Variable
                # tensors. Partition variables are Identity tensors that cannot be
                # handled by Saver.
                if has_partition_var:
                    raise ValueError(
                        "Models containing partition variables cannot be converted "
                        "from checkpoint files. Please pass in a SavedModel using "
                        "the flag --input_saved_model_dir.")
                # Models that have been frozen previously do not contain Variables.
                elif self._has_no_variables(sess):
                    raise ValueError(
                        "No variables were found in this model. It is likely the model "
                        "was frozen previously. You cannot freeze a graph twice.")
                # return 0
                else:
                    raise e

            saver.restore(sess, self.input_checkpoint)
            initializer_nodes=[]
            if initializer_nodes:
                sess.run(initializer_nodes.replace(" ", "").split(","))
        self.sess=sess
        return sess

    def restoreSessionWithGraphDef(self):
        tf.reset_default_graph()
        sess=tf.Session()
        sess.graph.as_default()
        graph_def=self.getGraphDef(self.graph_def_path)
        for node in graph_def.node:
            node.device = ""
        graph_def = tf.compat.v1.graph_util.extract_sub_graph(graph_def, self.end_points)

        self.graph_def=graph_def
        tf.import_graph_def(graph_def, name='')
        self.sess=sess
        return sess


    def getVariables(self,variable_names):
        # all_parition_variable_names = [
        #             (tensor.op.type,self.sess.run(tensor.name))
        #             for op in self.sess.graph.get_operations()
        #             for tensor in op.values()
        #             if tensor.name.split(":")[0] in variable_names
        #             ]
        runnable_variable_names = [
                    tensor.name
                    for op in self.sess.graph.get_operations()
                    for tensor in op.values()
                    if tensor.name.split(":")[0] in variable_names
                    ]
            
        returned_variables=self.sess.run(runnable_variable_names)
        found_variables = dict(zip(variable_names, returned_variables))

        return found_variables

    def getVariablesFromCheckpoint(self):
        if not self.input_checkpoint:
            return {}

        reader = pywrap_tensorflow.NewCheckpointReader(self.input_checkpoint)
        var_to_shape_map = reader.get_variable_to_shape_map() #Map between name and variable shape
        variable_names=[]
        returned_variables=[]
        for key in sorted(var_to_shape_map):
            variable_names.append(key)
            returned_variables.append(reader.get_tensor(key))
        
        found_variables = dict(zip(variable_names, returned_variables))
        return found_variables

    def getConstantsFromProto(self):
        if not self.graph_def_path:
            return {}

        graph_def=self.getGraphDef(self.graph_def_path)
        constant_names=[]
        returned_constants=[]
        found_constants = {}
        with tf.Session() as sess:
            sess.graph.as_default()
            tf.import_graph_def(graph_def, name='')
            for n in graph_def.node:
                if n.op=='Const':
                    constant_name=n.name.split(":")[0].replace("^","")
                    constant_names.append(constant_name)
                    constant_value=tensor_util.MakeNdarray(n.attr['value'].tensor)
                    returned_constants.append(constant_value)

        found_constants = dict(zip(constant_names, returned_constants))
        return found_constants

    def merge_func(self,value1,value2):
        if value1 is not None:
            return value1
        elif value2 is not None:
            return value2
        else:
            raise Exception("Somehow no value for the key was found")

    def getVariablesAndConstants(self):
        #Makes sure we prioritize the checkpoints data over the pb data
        d1=self.getVariablesFromCheckpoint()
        d2=self.getConstantsFromProto()
        return { key: self.merge_func(d1.get(key, None), d2.get(key, None)) for key in set( list(d1.keys()) + list(d2.keys()))}
        # return {**self.getVariablesFromCheckpoint(),**self.getConstantsFromProto()}

    def getVariablesFromSess(self):
        """
            Returns a dictionary of names:variables
        """
        if not self.graph_def:
            return {}

        if not self.sess:
            _=self.restoreSession()

        found_variables = {}
        variable_names = []
        variable_dict_names = []
        returned_variables=[]
        for node in self.graph_def.node:
            if node.op in ["Variable", "VariableV2", "VarHandleOp","Const"]:
                variable_name = node.name
                variable_dict_names.append(variable_name)
                variable_names.append(variable_name)
                if node.op == "VarHandleOp":
                    variable_names.append(variable_name + "/Read/ReadVariableOp:0")
                else:
                    variable_names.append(variable_name + ":0")

        if variable_names:
            returned_variables=self.sess.run(variable_names)

        # if constant_names:
        #     for constant_name in constant_names:
        #         print(constant_name)
        #         constant_tensor=self.sess.graph.get_tensor_by_name(constant_name+":0")
        #         variable_dict_names.append(constant_name)
        #         returned_variables.append(constant_tensor.eval(session=self.sess))

        # for constant_name in variable_names:
        #     print(constant_name)
        #     self.sess.run(constant_name+":0")
            # constant_tensor=self.sess.graph.get_tensor_by_name(constant_name+":0")
            # variable_dict_names.append(constant_name)
            # returned_variables.append(constant_tensor.eval(session=self.sess))

        found_variables = dict(zip(variable_dict_names, returned_variables))
        return found_variables
    
    def isPb(self, file):
        return self.graph_def_path.split(".")[-1]=="pb"

    def getDimensions(self,variable_names):
        if not self.sess:
            if self.input_checkpoint and self.graph_def_path:
                if self.isPb(self.input_checkpoint):
                    _=self.restoreSessionWithGraphDef()
                else:
                    _=self.restoreSession()
            elif self.graph_def_path:
                _=self.restoreSessionWithGraphDef()
            else:
                return [[]]

        dimensionList=[]
        for name in variable_names:
            try:
                tensorSize=self.sess.graph.get_tensor_by_name(variable_names[0]+":0").get_shape().as_list()
            except ValueError:
                tensorSize=[None]
                
            dimensionList.append(tensorSize)

        return dimensionList
        # all_parition_variable_names = [
        #             tensor.get_shape().as_list()
                    
        #             for op in self.sess.graph.get_operations()
        #             for tensor in op.values()
        #             if tensor.name.split(":")[0] in variable_names
        #             ]
        # print(all_parition_variable_names)

        # return all_parition_variable_names

    def getTensor(self,tensorName):
        if not self.sess:
            _=self.restoreSession()

        return self.sess.graph.get_tensor_by_name(tensorName + ":0")

    def getTrainableTensors(self):
        variables = [v.name for v in tf.trainable_variables()]
        return variables
        # values = sess.run(variables_names)
        # for k, v in zip(variables_names, values):
        #     print "Variable: ", k
        #     print "Shape: ", v.shape
        #     print v
    def checkIfTrainable(self, tensorName):
        for v in tf.trainable_variables():
            if tensorName in v.name:
                return True
        return False
        # variable_names = [v.name for v in tf.trainable_variables()]

    def close(self):
        if self.sess:
            self.sess.close()
        


