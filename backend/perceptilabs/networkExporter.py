import os
import tensorflow as tf
import shutil

from perceptilabs.core_new.utils import set_tensorflow_mode


class exportNetwork():
    def __init__(self,saverObj):
        self.sess=saverObj["sess"]
        self.saver=saverObj["saver"]
        self.network_inputs=saverObj["network_inputs"]
        self.network_outputs=saverObj["network_outputs"]

    def asTfModel(self,path,epoch):
        set_tensorflow_mode('graph')
        export_path=path
        if os.path.exists( export_path+"/1"):
            shutil.rmtree( export_path+"/1")
        export_path = export_path+"/1"

        tf.saved_model.simple_save(self.sess, export_path, inputs={"input":self.network_inputs}, outputs={"output":self.network_outputs})
        return os.path.abspath(self.saver.save(self.sess, path+'/model.ckpt', global_step=epoch))

    # def asTfModel(self,path,epoch):
    #     graph=self.graphObj.graphs

    #     start_nodes=self.graphObj.start_nodes
    #     end_points=self.graphObj.end_points
    #     network_outputs=[]
    #     for end_point in end_points:
    #         if graph[end_point]["Info"]["Type"]=="TrainNormal":
    #             for connection in graph[end_point]["Con"]:
    #                 if connection!=graph[end_point]["Info"]["Properties"]["Labels"]:
    #                     network_outputs.append(connection)
    #         elif graph[end_point]["Info"]["Type"]=="TrainReinforce":
    #             for connection in graph[end_point]["Con"]:
    #                 if not graph[connection]["Info"]["Copy"]:
    #                     network_outputs.append(connection)

    #     network_inputs=[]
    #     queue=network_outputs[:]
    #     while queue:
    #         Id=queue.pop()
    #         if not graph[Id]["Info"]["backward_connections"]:
    #             network_inputs.append(Id)
    #         else:
    #             queue.extend(graph[Id]["Info"]["backward_connections"])
    #     export_path=path
    #     if os.path.exists( export_path+"/1"):
    #         shutil.rmtree( export_path+"/1")

    #     export_path = export_path+"/1"

    #     tf.saved_model.simple_save(self.sess, export_path, inputs={'input': [graph[node]['Info']["Data"].placeholder for node in network_inputs][0]}, outputs={'output':[self.outputDict[node] for node in network_outputs][0]})
    #     # saver = tf.train.Saver()
    #     return os.path.abspath(self.saver.save(self.sess, path+'/model.ckpt', global_step=epoch))

    def asCompressedTfModel(self,path):
        set_tensorflow_mode('graph')
        # graph=self.graphObj.graphs

        # start_nodes=self.graphObj.start_nodes
        # end_points=self.graphObj.end_points
        # network_outputs=[]
        # for end_point in end_points:
        #     if graph[end_point]["Info"]["Type"]=="TrainNormal":
        #         for connection in graph[end_point]["Con"]:
        #             if connection==graph[end_point]["Info"]["Properties"]["Labels"]:
        #                 pass
        #             else:
        #                 network_outputs.append(connection)
        #     elif graph[end_point]["Info"]["Type"]=="TrainReinforce":
        #         for connection in graph[end_point]["Con"]:
        #             if not graph[connection]["Info"]["Copy"]:
        #                 network_outputs.append(connection)

        # network_inputs=[]
        # queue=network_outputs[:]
        # while queue:
        #     Id=queue.pop()
        #     if not graph[Id]["Info"]["backward_connections"]:
        #         network_inputs.append(Id)
        #     else:
        #         queue.extend(graph[Id]["Info"]["backward_connections"])

        # converter = tf.lite.TFLiteConverter.from_session(self.sess, [graph[node]['Info']["Data"].placeholder for node in network_inputs], [self.outputDict[node] for node in network_outputs])
        converter = tf.lite.TFLiteConverter.from_session(self.sess, [self.network_inputs], [self.network_outputs])
        converter.post_training_quantize=True
        # print(converter)
        tflite_model = converter.convert()
        
        # print("Got tflite_model")
        tflitePath=os.path.abspath(path+".tflite")
        open(tflitePath, "wb").write(tflite_model)
        return tflitePath
