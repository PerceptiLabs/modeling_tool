from codehq import CodeHqNew
from networkBuilder import NetworkBuilder
from networkExporter import exportNetwork

import numpy as np
import tensorflow as tf
from tensorflow.python.saved_model import tag_constants
import math
from graph import Graph
from dataKeeper import dataKeeper as Data
from extractVariables import *

import sys
import time
import copy
import queue
import os
import shutil
import random
from sentry_sdk import capture_exception

import pprint
import logging
log = logging.getLogger(__name__)


# import cv2


# from sklearn.cluster import KMeans, DBSCAN
# from sklearn.neighbors import KNeighborsClassifier,KNeighborsRegressor
# from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
# from sklearn.svm import OneClassSVM,NuSVC,NuSVR

class core():
    def __init__(self,networkName):
        self.networkName=networkName
        
        self.status="Created"
        self.trainingStatus="Waiting"
        self.testStatus="First"
        self.headlessOnFlag=False
        self.headlessOffFlag=False
        self.epoch=0
        self.iter=0
        self._testIter=self.testIter=0
        self.batch_size=0
        self.trainDict=dict()
        self.testDict=dict()

        self.saveDict=dict()
        self.graphObj=None

        self.sess=None
        self.outputDict=None
        self.outputVariables=None
        self.exporter=None

        self.trainingIterations=0
        self.validationIterations=0
        self.maxTestIter=0
        self.maxIter=0
        self.maxEpochs=0
        self.FLAG_REINFORCE=False
        self.done_state=False

        self.outputVariablesStructure=dict()
        
    def startNetwork(self,warningQueue,errorQueue,commandQ,resultQ,dataDict,jsonNetwork):
        dataDict=dataDict.copy()
        if log.isEnabledFor(logging.DEBUG):
            pass#log.debug("startNetwork with jsonNetwork: " + pprint.pformat(jsonNetwork))
            
        #import json
        #with open('net.json', 'w') as f:
        #    json.dump(jsonNetwork, f, indent=4)

        
        # from sentry_sdk import configure_scope

        # with configure_scope() as scope:
        #     scope.set_extra("JsonNetwork", jsonNetwork)
        self.resetVariables()
        self.trainingStatus="Training" #Can be Training, Validating and Testing
        self.status="Running"

        self.randomSeed=int(np.random.random(1)*1000)

        self.maxEpochs=int(jsonNetwork["Hyperparameters"]['Epochs'])
        # self.batch_size=int(jsonNetwork["Hyperparameters"]['Batch_size'])
        dropout_rate=float(jsonNetwork["Hyperparameters"]["Dropout_rate"])
        save_model_every=int(jsonNetwork["Hyperparameters"]["Save_model_every"])

        
        layers=jsonNetwork['Layers']

        try:
            self.graphObj=Graph(layers)
        except Exception as e:
            errorQueue.put("The graph did not build correctly.")
            self.resetVariables()
            raise Exception(str(e))
        print(self.graphObj)

        graph=self.graphObj.graphs   #graph has structure [id]->[id for id in backward_connections]

        #Incase we have loaded a network
        checkpointDict={}
        for Id in list(graph.keys()):
            content=graph[Id]['Info']
            if "checkpoint" in content and content["checkpoint"]!=[] and content["checkpoint"][-1] not in list(checkpointDict.keys()):
                # checkpointDict[content["checkpoint"][-1]]=extractCheckpointInfo(*content["checkpoint"])
                checkpointDict[content["checkpoint"][-1]]=extractCheckpointInfo(content["endPoints"],*content["checkpoint"]).getVariablesAndConstants()
        if checkpointDict:
            tf.reset_default_graph()

        keep_prob = tf.placeholder(tf.float32)
        self.keep_prob_val = 1.0-float(jsonNetwork["Hyperparameters"]["Dropout_rate"])

        # Build network/model
        # Either use FLAG_DISTRIBUTED and have if/else statement when doing sess.run for TensorFlow OR put whole startNetwork() content inside a with strategy.scope()
        try:
            outputDict, outputVariables, self.FLAG_REINFORCE = NetworkBuilder().buildNetwork(self.graphObj,jsonNetwork,self.randomSeed,keep_prob,checkpointDict,self.batch_size,dataDict,warningQueue,errorQueue)
        except Exception as e:
            self.resetVariables()
            # errorQueue.put("The network did not build correctly.")
            raise Exception(e)

        print("Network built!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        #########################################Setup the session###########################################
        self.sess = tf.InteractiveSession()
        self.sess.run(tf.global_variables_initializer())
        self.sess.run(tf.local_variables_initializer())

        self.saver = tf.train.Saver()

        self.exporter=exportNetwork(self.sess,self.saver,self.graphObj,outputDict)

        # self.sess=sess
        self.outputDict=outputDict
        self.outputVariables=outputVariables

        self.epoch=0
        self.iter=0
        self.maxIter=self.maxTestIter=0

        for i in self.graphObj.placeholders:
            if graph[i]['Info']['Type']=="DataEnvironment":
                self.maxIter=int(jsonNetwork["Hyperparameters"]["MaxSteps"])
                self.maxTestIter=self.maxIter
                self.trainingIterations=self.maxIter
                self.batch_size=graph[i]['Info']["Data"].source_obj.batch_size
            elif graph[i]['Info']['Type']=="DataData":
                self.maxIter=graph[i]['Info']["Data"].maxIter
                self.maxTestIter=graph[i]['Info']["Data"].maxTestIter
                self.batch_size=graph[i]['Info']["Data"].batch_size
                self.trainingIterations=graph[i]['Info']["Data"].trainingIterations


        

        # if self.FLAG_REINFORCE:
        #     self.maxIter=int(jsonNetwork["Hyperparameters"]["MaxSteps"])
        #     self.maxTestIter=self.maxIter
        # else:
        #     self.data_partition=jsonNetwork["Hyperparameters"]["Data_partition"]
        #     minData_size=min([int(graph[tI]['Info']["Data"].source_obj.data_size) for tI in self.graphObj.placeholders])
        #     self.trainingIterations=int(minData_size*float(jsonNetwork["Hyperparameters"]["Data_partition"]["Training"])/100)
        #     self.validationIterations=int(minData_size*float(jsonNetwork["Hyperparameters"]["Data_partition"]["Validation"])/100)
        #     self.maxIter=self.trainingIterations+self.validationIterations
        #     self.maxTestIter=int(minData_size*float(jsonNetwork["Hyperparameters"]["Data_partition"]["Test"])/100)

        #Create a "createNetworkStructure" which loops over all the split parts of the network and uses "createTfStructure" when the part of the network is tensorflow
        outputVariablesStructure,nonTensorValues=self.createTfStructure(outputVariables,self.graphObj)
        outputVariablesStructureDay=outputVariablesStructure
        outputVariablesStructureNight=self.createHeadlessTfStructure(outputVariables,self.graphObj)

        #Build it as a finite state machine
        log.info("Entering finite state machine with maxIter = {}, maxTestIter = {}, trainingIterations = {}, batch_size = {}".format(self.maxIter, self.maxTestIter, self.trainingIterations, self.batch_size))

        
        startTime=time.time()
        while(True):
            #print("Status:", self.status, self.trainingStatus)
            if not commandQ.empty():
                commandQueueOverview=commandQ.queue
                print(commandQueueOverview)

                try:
                    function, args, kwargs = commandQ.get(timeout=0.05)
                    if function.__name__=="exportNetwork":
                        # try:
                        self.exportNetwork(self.sess,self.graphObj,outputDict,*args)
                        # self.resultQ.put(self.exportNetwork(self.sess,self.graphObj,outputDict,*args))
                        # except Exception as e:
                            # self.resultQ.put("ExportFailed")
                            # self.errorQueue("Export Failed with this error: ")
                            # self.errorQueue.put(e)
                        # function(sess,*args)
                    # if function.__name__=="setStatus":
                    #     self.status=function(*args)
                    else:
                        function(*args, **kwargs)
                except:
                    directCommand=commandQ.get()
                    print("Direct command to core: ",directCommand)
                    self.status=directCommand
                # except Exception as e:
                    # warningQueue.put("Could not parse the command " + str(commandQueueOverview) + " resulting in following error: " + str(e))
                    # print(e)
                
            else:
                if self.status=="Stop":
                    self.saveTempNetwork()
                    # sess.close()
                    print("Stopping thread but keeping session open")
                    return
                if self.status=="Paused":
                    time.sleep(0.2)
                # if self.status=="Skip":
                #     self.skip()
                if self.headlessOnFlag:
                    outputVariablesStructure=outputVariablesStructureNight
                    self.headlessOnFlag=False
                    print("Headless On")

                if self.headlessOffFlag:
                    outputVariablesStructure=outputVariablesStructureDay
                    self.headlessOffFlag=False
                    print("Headless Off")

                if self.status=="Running":
                    if self.iter%100==0:
                        log.info("ITER: {}".format(self.iter))
                        
                    if self.trainingStatus=="Training":
                        # trainTime=time.time()
                        if self.iter<self.trainingIterations:
                            outValues=self.runTraining(self.sess,outputDict,self.graphObj,outputVariablesStructure,self.batch_size,keep_prob)
                            self.trainDict=self.saveVariables(outValues,nonTensorValues,self.graphObj,self.trainDict)
                            
                        self.trainLogic()
                        resultQ.put(self.getResults())
                        #time.sleep(0.5)
                        # print("TrainingTime: ", time.time()-trainTime)

                    elif self.trainingStatus=="Validation":
                        if self.iter<self.maxIter:
                            outValues=self.runValidation(self.sess,self.graphObj,outputVariablesStructure,keep_prob)
                            self.trainDict=self.saveVariables(outValues,nonTensorValues,self.graphObj,self.trainDict)
                        self.validationLogic()
                        resultQ.put(self.getResults())

                    elif self.trainingStatus=="Testing":
                        if self.testStatus=="First":
                            outValues=self.runTest(self.sess,self.graphObj,outputVariablesStructure,keep_prob)
                            self.testDict=self.saveVariables(outValues,nonTensorValues,self.graphObj,None)
                            resultQ.put(self.getResults())
                            self.testStatus="Waiting"   #Set Status to Waiting to signal to the logic that all calculations are done
                            
                        elif self.testStatus!="Waiting":
                            self.testLogic()

                            try:
                                outValues=self.runTest(self.sess,self.graphObj,outputVariablesStructure,keep_prob)
                                self.testDict=self.saveVariables(outValues,nonTensorValues,self.graphObj,None)
                                resultQ.put(self.getResults())
                            except:
                                print("Someone tried to press run when it was already at the end")

                            self.testIter=self._testIter
                            if self.testStatus=="Running":
                                time.sleep(1.5)

                        else:
                            time.sleep(0.3)

                        
                    elif self.trainingStatus=="Finished":
                        if startTime>0:
                            print("Time to complete: ", time.time()-startTime)
                        startTime=0
                        time.sleep(0.3)



    def runTraining(self,sess,outputDict,graphObj,outputVariablesStructure,batch_size,keep_prob):
        graph=graphObj.graphs
        keys=[]
        values=[]
        save_var=False
        keys.append(keep_prob)
        values.append(self.keep_prob_val)
        for i in graphObj.placeholders:
            if graph[i]['Info']['Type']=="DataEnvironment":
                keys.append(outputDict[i])
                valuekey="State"
                values.append(graph[i]['Info']["Data"].getData(save_var,batch_size,self.iter,self.trainingStatus,valuekey,sess,keep_prob))
                self.done_state = graph[i]['Info']["Data"].putBuffer(self.iter,sess,keep_prob)
            elif graph[i]['Info']['Type']=="TrainReinforce":
                for valuekey,pholder in outputDict[i].items():
                    keys.append(pholder)
                    values.append(graph[i]['Info']["Data"].getData(save_var,batch_size,self.iter,self.trainingStatus,valuekey,sess,keep_prob))
            elif graph[i]['Info']['Type']=="DataData" and self.iter==0:
                sess.run(graph[i]['Info']["Data"].train_iterator)
                # try:
                #     print("Image sample: ",sess.run(graph[i]['Info']["Data"].filename))
                #     self.input=graph[i]['Info']["Data"].filename
                # except:
                #     print("Label sample: ",sess.run(graph[i]['Info']["Data"].placeholder))
                #     self.label=graph[i]['Info']["Data"].placeholder
        #         # keys.append(outputDict[i])
        #         # valuekey=None
        #         # values.append(graph[i]['Info']["Data"].getData(save_var,batch_size,self.iter,self.trainingStatus,valuekey,sess))
        # print("Iteration: ",self.iter)
        # sample=sess.run(self.input)
        # print("Image sample: ",sample)
        # # self.inputList.append(sample[-1])
        # print("Label sample: ",sess.run(self.label))
        #keys=[outputDict[i] for i in graphObj.placeholders]
        #values=[graph[i]['Info']["Data"].getData(graph[i]['Info']["Properties"]["accessProperties"],batch_size,self.iter,self.trainingStatus,self.randomSeed) for i in graphObj.placeholders]
        for Id in graphObj.end_points:
            #Look into running multiple optimizers at the same time
            # if layers[Id]["update_frequency"]%itera==0:

            #Appends all values exceot for the keys and values already in there
            _,outValues=sess.run([outputDict[Id], outputVariablesStructure],feed_dict=dict(zip(keys, values)))
            #sess.run(outputDict[Id])
            # sess.run(outputDict[Id],feed_dict=dict(zip((keys+[self.keep_prob]), (values+[self.Keep_prob_]))))
        return outValues    

    def trainLogic(self):
        self.iter+=1

        if self.iter>=self.trainingIterations and not self.FLAG_REINFORCE:
            #self.iter=0
            self.trainingStatus="Validation"
        elif self.FLAG_REINFORCE:
            if self.done_state:
                self.epoch+=1
                self.iter=0
            if self.epoch>=self.maxEpochs:
                self.saveTempNetwork()
                # self.iter=0
                # self.trainingStatus="Testing"
                self.trainingStatus="Finished"
        

    def runValidation(self,sess,graphObj,outputVariablesStructure, keep_prob,headless=False):
        graph=graphObj.graphs
        keys=[]
        values=[]
        save_var=False
        keys.append(keep_prob)
        values.append(1.0)
        
        for i in graphObj.placeholders:
            if graph[i]['Info']['Type']=="DataData" and self.iter==self.trainingIterations:
                sess.run(graph[i]['Info']["Data"].validation_iterator)
        
        outValues=sess.run(outputVariablesStructure,feed_dict=dict(zip(keys, values)))

        return outValues

    def validationLogic(self):
        self.iter+=1
        if self.iter>=self.maxIter:
            if self.epoch+1>=self.maxEpochs:
                self.saveTempNetwork()
                # self.iter=0
                # self.trainingStatus="Testing"
                # self.status="Finished"
                self.trainingStatus="Finished"
            else:
                self.epoch+=1
                self.iter=0
                self.trainingStatus="Training"
        # else:
            
    def runTest(self,sess,graphObj,outputVariablesStructure, keep_prob,headless=False):
        graph=graphObj.graphs
        keys=[]
        values=[]
        save_var=False
        keys.append(keep_prob)
        values.append(1.0)
        
        for i in graphObj.placeholders:
            if graph[i]['Info']['Type']=="DataData" and self._testIter<=0:
                sess.run(graph[i]['Info']["Data"].test_iterator)
        
        outValues=sess.run(outputVariablesStructure,feed_dict=dict(zip(keys, values)))

        return outValues


    def testLogic(self):
        if self.testStatus=="nextStep":
            if self._testIter<self.maxTestIter-1:
                self._testIter+=1
            else:
                self._testIter=0
            self.testStatus="Waiting"

        if self.testStatus=="previousStep":
            if self._testIter>1:
                self._testIter-=1
            self.testStatus="Waiting"

        if self.testStatus=="Running":
            self._testIter+=1
            if self._testIter>=self.maxTestIter-1:
                self.testStatus="Waiting"
        
        if self.testStatus=="ResetAndRun":
            self._testIter=0
            self.testStatus="Running"
        
        if self.testStatus=="Reset":
            self._testIter=0
            self.testStatus="Waiting"
            
    def createTfStructure(self,outputVariables,graphObj):
        graph=graphObj.graphs
        outputTensorsStructure=dict()
        outputVariablesStructure=dict()

        for outerKey, outerValue in outputVariables.items():
            if outerKey not in graphObj.copykeys:
                if type(outerValue) is dict:
                    outputTensorsStructure[outerKey]=dict()
                    outputVariablesStructure[outerKey]=dict()

                    for innerKey, innerValue in outerValue.items():
                        if type(innerValue) is dict:
                            outputTensorsStructure[outerKey][innerKey]=dict()
                            outputVariablesStructure[outerKey][innerKey]=dict()

                            for extraInnerKey, extraInnerValue in innerValue.items():
                                value = outputVariables[outerKey][innerKey][extraInnerKey]
                                if tf.contrib.framework.is_tensor(value):
                                    outputTensorsStructure[outerKey][innerKey][extraInnerKey]=value
                                elif self._isNumberOrNumberContainer(value):
                                    outputVariablesStructure[outerKey][innerKey][extraInnerKey]=value
                        else:
                            value = outputVariables[outerKey][innerKey]
                            if tf.contrib.framework.is_tensor(value):
                                outputTensorsStructure[outerKey][innerKey]=value
                            elif self._isNumberOrNumberContainer(value):
                                outputVariablesStructure[outerKey][innerKey]=value

                    if graph[outerKey]['Info']["Type"] in ["DeepLearningFC", "DeepLearningConv", "DeepLearningDeconv", "DeepLearningRecurrent"] and "W" in outputVariables[outerKey]:
                        outputTensorsStructure[outerKey]["Gradient"]=dict()

                        if "loss" in outputVariables[graphObj.end_points[0]]:
                            outputTensorsStructure[outerKey]["Gradient"]=tf.gradients(outputVariables[graphObj.end_points[0]]["loss"], outputVariables[outerKey]["W"])
                else:
                    if tf.contrib.framework.is_tensor(outputVariables[outerKey]):
                        outputTensorsStructure[outerKey]=outputVariables[outerKey]
                    elif self._isNumberOrNumberContainer(outputVariables[outerKey]):
                        outputVariablesStructure[outerKey]=outputVariables[outerKey]
        return outputTensorsStructure, outputVariablesStructure

    def createHeadlessTfStructure(self,outputVariables,graphObj):
        graph=graphObj.graphs
        outputVariablesStructure=dict()

        for outerKey, outerValue in outputVariables.items():
            if outerKey not in graphObj.copykeys:
                if type(outerValue) is dict:
                    outputVariablesStructure[outerKey]=dict()

                    for innerKey, innerValue in outerValue.items():
                        if type(innerValue) is dict:
                            outputVariablesStructure[outerKey][innerKey]=dict()

                            for extraInnerKey, extraInnerValue in innerValue.items():
                                if self.keepVariable(graph, outerKey,innerKey,extraInnerKey):
                                    if tf.contrib.framework.is_tensor(outputVariables[outerKey][innerKey][extraInnerKey]):
                                        outputVariablesStructure[outerKey][innerKey][extraInnerKey]=outputVariables[outerKey][innerKey][extraInnerKey]
                        else:
                            if self.keepVariable(graph, outerKey, innerKey):
                                if tf.contrib.framework.is_tensor(outputVariables[outerKey][innerKey]):
                                    outputVariablesStructure[outerKey][innerKey]=outputVariables[outerKey][innerKey]
                else:
                    if self.keepVariable(graph, outerKey):
                        if tf.contrib.framework.is_tensor(outputVariables[outerKey]):
                            outputVariablesStructure[outerKey]=outputVariables[outerKey]
        return outputVariablesStructure

    def _isNumberOrNumberContainer(self, thing):
        def is_number(x):
            try:
                return 0 == x*0
            except:
                return False
        
        if type(thing) in [list, tuple, set, np.ndarray]:
            return all([self._isNumberOrNumberContainer(x) for x in thing])
        elif isinstance(thing, dict):
            return all([self._isNumberOrNumberContainer(x) for x in thing.values()])
        else:
            return is_number(thing) or isinstance(thing, str)
    
    def saveVariables(self,outValues,nonTensorValues,graphObj,resultDict):
        graph=graphObj.graphs

        if not resultDict:
            resultDict=copy.deepcopy(outValues)        

            # Also add non tensor values
            for outerKey, outerValue in nonTensorValues.items():
                if type(outerValue) is dict:
                    for innerKey, innerValue in outerValue.items():
                        if type(innerValue) is dict:
                            for extraInnerKey, extraInnerValue in innerValue.items():
                                resultDict[outerKey][innerKey][extraInnerKey] = extraInnerValue
                        else:
                            resultDict[outerKey][innerKey] = innerValue
                else:
                    resultDict[outerKey] = outerValue

                    
            # hack for displaying qagents state in frontend. also see below in if clause
            for key, value in graph.items():
                # if outerKey not in graphObj.copykeys:
                if type(value) is not dict:
                    continue
                
                if graph[key]['Info']['Type'] in ['TrainReinforce', 'DataEnvironment']:
                    state = graph[key]['Info']['Data'].source_obj.agent.state
                    pred = graph[key]['Info']['Data'].source_obj.agent.pred
                    resultDict[key]['state'] = state
                    resultDict[key]['pred'] = pred

            #First merge them correctly
            for outerKey, outerValue in outValues.items():
                if type(outerValue) is dict:
                    for innerKey, innerValue in outerValue.items():
                        if type(innerValue) is not dict:
                            if self.stackVariable(graph,outerKey,innerKey):
                                if innerKey=="Gradient":
                                    resultDict[outerKey][innerKey]=dict()
                                    resultDict[outerKey][innerKey]["Max"]=np.array([])
                                    resultDict[outerKey][innerKey]["Min"]=np.array([])
                                    resultDict[outerKey][innerKey]["Average"]=np.array([])
                                if innerKey=="accuracy":
                                    resultDict[outerKey]["epochTrainAccuracy"]=np.array([])
                                    resultDict[outerKey]["epochValAccuracy"]=np.array([])
                                if innerKey=="loss":
                                    resultDict[outerKey]["epochTrainLoss"]=np.array([])
                                    resultDict[outerKey]["epochValLoss"]=np.array([])
                                
                                if innerKey=="f1":
                                    resultDict[outerKey]["epochTrainF1"]=np.array([])
                                    resultDict[outerKey]["epochValF1"]=np.array([])
                                if innerKey=="p_and_r":
                                    resultDict[outerKey]["epochTrainPandR"]=np.array([])
                                    resultDict[outerKey]["epochValPandR"]=np.array([])
                                if innerKey=="roc":
                                    resultDict[outerKey]["epochTrainROC"]=np.array([])
                                    resultDict[outerKey]["epochValROC"]=np.array([])
                                if innerKey=="auc":
                                    resultDict[outerKey]["epochTrainAUC"]=np.array([])
                                    resultDict[outerKey]["epochValAUC"]=np.array([])
                        else:
                            for extraInnerKey, extraInnerValue in innerValue.items():
                                if self.stackVariable(graph,outerKey,innerKey,extraInnerKey):
                                    if extraInnerKey=="Reward":
                                        resultDict[outerKey][innerKey]["epochTotalReward"]=np.array([])
                                    if extraInnerKey=="Done":
                                        resultDict[outerKey][innerKey]["epochTotalSteps"]=np.array([])   

        else:
            # Hack for displaying state and pred.
            for key, value in graph.items():
                # if outerKey not in graphObj.copykeys:
                if type(value) is not dict:
                    continue
                
                if graph[key]['Info']['Type'] in ['TrainReinforce', 'DataEnvironment']:
                    state = graph[key]['Info']['Data'].source_obj.agent.state
                    pred = graph[key]['Info']['Data'].source_obj.agent.pred
                    resultDict[key]['state'] = state
                    resultDict[key]['pred'] = pred
            
        #Merge the dictionaries
            for outerKey, outerValue in outValues.items():
                # if outerKey not in graphObj.copykeys:
                if type(outerValue) is dict:
                    for innerKey, innerValue in outerValue.items():
                        if type(innerValue) is dict:
                            for extraInnerKey, extraInnerValue in innerValue.items():
                                if self.stackVariable(graph,outerKey,innerKey,extraInnerKey):                                                        
                                    if graph[outerKey]['Info']["Type"]=="TrainReinforce" and extraInnerKey=="Reward":
                                        if any(outValues[outerKey][innerKey]["Done"]) or self.iter==self.maxIter-1:
                                            try:
                                                resultDict[outerKey][innerKey]["epochTotalReward"]=np.append(resultDict[outerKey][innerKey]["epochTotalReward"], resultDict[outerKey][innerKey][extraInnerKey][-1])
                                            except:
                                                resultDict[outerKey][innerKey]["epochTotalReward"]=np.append(resultDict[outerKey][innerKey]["epochTotalReward"], np.sum(outValues[outerKey][innerKey][extraInnerKey]))
                                            if self.epoch!=self.maxEpochs-1:
                                                resultDict[outerKey][innerKey][extraInnerKey]=np.array([])
                                        try:
                                            for o in outValues[outerKey][innerKey][extraInnerKey]:
                                                resultDict[outerKey][innerKey][extraInnerKey]=np.append(resultDict[outerKey][innerKey][extraInnerKey],o+resultDict[outerKey][innerKey][extraInnerKey][-1])
                                        except:
                                            resultDict[outerKey][innerKey][extraInnerKey]=np.append(resultDict[outerKey][innerKey][extraInnerKey],outValues[outerKey][innerKey][extraInnerKey][0])
                                            for o in outValues[outerKey][innerKey][extraInnerKey][1:]:
                                                resultDict[outerKey][innerKey][extraInnerKey]=np.append(resultDict[outerKey][innerKey][extraInnerKey],o+resultDict[outerKey][innerKey][extraInnerKey][-1])

                                    elif graph[outerKey]['Info']["Type"]=="TrainReinforce" and extraInnerKey=="Done":
                                        if any(outValues[outerKey][innerKey][extraInnerKey]) or self.iter==self.maxIter-1:
                                            resultDict[outerKey][innerKey]["epochTotalSteps"]=np.append(resultDict[outerKey][innerKey]["epochTotalSteps"], self.iter*self.batch_size)

                                    else:
                                        resultDict[outerKey][innerKey][extraInnerKey]=np.append(resultDict[outerKey][innerKey][extraInnerKey],outValues[outerKey][innerKey][extraInnerKey])
                                else:
                                    resultDict[outerKey][innerKey][extraInnerKey]=outValues[outerKey][innerKey][extraInnerKey]
                        else:
                            if self.stackVariable(graph,outerKey,innerKey):
                                if innerKey=="Gradient":
                                    resultDict[outerKey][innerKey]["Max"]=np.append(resultDict[outerKey][innerKey]["Max"],np.max(np.max(outValues[outerKey][innerKey])))
                                    resultDict[outerKey][innerKey]["Min"]=np.append(resultDict[outerKey][innerKey]["Min"],np.min(np.min(outValues[outerKey][innerKey])))
                                    resultDict[outerKey][innerKey]["Average"]=np.append(resultDict[outerKey][innerKey]["Average"],np.average(outValues[outerKey][innerKey]))
                                    if resultDict[outerKey][innerKey]["Average"].size>500:
                                        resultDict[outerKey][innerKey]["Max"]=resultDict[outerKey][innerKey]["Max"][-500:]
                                        resultDict[outerKey][innerKey]["Min"]=resultDict[outerKey][innerKey]["Min"][-500:]
                                        resultDict[outerKey][innerKey]["Average"]=resultDict[outerKey][innerKey]["Average"][-500:]

                                elif graph[outerKey]['Info']["Type"]=="TrainNormal" and innerKey=="accuracy":
                                    if self.iter==self.trainingIterations:
                                        resultDict[outerKey]["epochTrainAccuracy"]=np.append(resultDict[outerKey]["epochTrainAccuracy"], outValues[outerKey][innerKey])
                                    if self.iter==self.maxIter-1:
                                        resultDict[outerKey]["epochValAccuracy"]=np.append(resultDict[outerKey]["epochValAccuracy"], outValues[outerKey][innerKey])
                                        if self.epoch!=self.maxEpochs-1:
                                            resultDict[outerKey][innerKey]=np.array([])
                                    resultDict[outerKey][innerKey]=np.append(resultDict[outerKey][innerKey],outValues[outerKey][innerKey])
                                    
                                elif graph[outerKey]['Info']["Type"]=="TrainNormal" and innerKey=="loss":
                                    if self.iter==self.trainingIterations:
                                        resultDict[outerKey]["epochTrainLoss"]=np.append(resultDict[outerKey]["epochTrainLoss"], outValues[outerKey][innerKey])
                                    if self.iter==self.maxIter-1:
                                        resultDict[outerKey]["epochValLoss"]=np.append(resultDict[outerKey]["epochValLoss"], outValues[outerKey][innerKey])
                                        if self.epoch!=self.maxEpochs-1:
                                            resultDict[outerKey][innerKey]=np.array([])
                                    resultDict[outerKey][innerKey]=np.append(resultDict[outerKey][innerKey],outValues[outerKey][innerKey])

                                elif graph[outerKey]['Info']["Type"]=="TrainNormal" and innerKey=="f1":
                                    if self.iter==self.trainingIterations:
                                        resultDict[outerKey]["epochTrainF1"]=np.append(resultDict[outerKey]["epochTrainF1"], outValues[outerKey][innerKey])
                                    if self.iter==self.maxIter-1:
                                        resultDict[outerKey]["epochValF1"]=np.append(resultDict[outerKey]["epochValF1"], outValues[outerKey][innerKey])
                                        if self.epoch!=self.maxEpochs-1:
                                            resultDict[outerKey][innerKey]=np.array([])
                                    resultDict[outerKey][innerKey]=np.append(resultDict[outerKey][innerKey],outValues[outerKey][innerKey])

                                elif graph[outerKey]['Info']["Type"]=="TrainNormal" and innerKey=="p_and_r":
                                    if self.iter==self.trainingIterations:
                                        resultDict[outerKey]["epochTrainPandR"]=np.append(resultDict[outerKey]["epochTrainPandR"], outValues[outerKey][innerKey])
                                    if self.iter==self.maxIter-1:
                                        resultDict[outerKey]["epochValPandR"]=np.append(resultDict[outerKey]["epochValPandR"], outValues[outerKey][innerKey])
                                        if self.epoch!=self.maxEpochs-1:
                                            resultDict[outerKey][innerKey]=np.array([])
                                    resultDict[outerKey][innerKey]=np.append(resultDict[outerKey][innerKey],outValues[outerKey][innerKey])
                                    
                                elif graph[outerKey]['Info']["Type"]=="TrainNormal" and innerKey=="roc":
                                    if self.iter==self.trainingIterations:
                                        resultDict[outerKey]["epochTrainROC"]=np.append(resultDict[outerKey]["epochTrainROC"], outValues[outerKey][innerKey])
                                    if self.iter==self.maxIter-1:
                                        resultDict[outerKey]["epochValROC"]=np.append(resultDict[outerKey]["epochValROC"], outValues[outerKey][innerKey])
                                        if self.epoch!=self.maxEpochs-1:
                                            resultDict[outerKey][innerKey]=np.array([])
                                    resultDict[outerKey][innerKey]=np.append(resultDict[outerKey][innerKey],outValues[outerKey][innerKey])

                                elif graph[outerKey]['Info']["Type"]=="TrainNormal" and innerKey=="auc":
                                    if self.iter==self.trainingIterations:
                                        resultDict[outerKey]["epochTrainAUC"]=np.append(resultDict[outerKey]["epochTrainAUC"], outValues[outerKey][innerKey])
                                    if self.iter==self.maxIter-1:
                                        resultDict[outerKey]["epochValAUC"]=np.append(resultDict[outerKey]["epochValAUC"], outValues[outerKey][innerKey])
                                        if self.epoch!=self.maxEpochs-1:
                                            resultDict[outerKey][innerKey]=np.array([])
                                    resultDict[outerKey][innerKey]=np.append(resultDict[outerKey][innerKey],outValues[outerKey][innerKey])

                                elif graph[outerKey]['Info']["Type"]=="TrainReinforce" and innerKey=="loss":
                                    if any(outValues[outerKey]["X"]["Done"]) or self.iter==self.maxIter-1:
                                        resultDict[outerKey]["epochTrainLoss"]=np.append(resultDict[outerKey]["epochTrainLoss"], outValues[outerKey][innerKey])
                                        if self.epoch!=self.maxEpochs-1:
                                            resultDict[outerKey][innerKey]=np.array([])
                                    resultDict[outerKey][innerKey]=np.append(resultDict[outerKey][innerKey],outValues[outerKey][innerKey])

                                else:
                                    resultDict[outerKey][innerKey]=np.append(resultDict[outerKey][innerKey],outValues[outerKey][innerKey])
                            else:
                                resultDict[outerKey][innerKey]=outValues[outerKey][innerKey]
                else:
                    if self.stackVariable(graph,outerKey):
                        resultDict[outerKey]=np.append(resultDict[outerKey],outValues[outerKey])
                    else:
                        resultDict[outerKey]=outValues[outerKey]

        return resultDict

    def variableFunction(self, graph, key, outValue, resultValue, tracebackKeys):
        if "Gradient" in tracebackKeys:
            if key=="Max":
                return 

        if key=="accuracy":
            return
    def as_list(self,x):
        if type(x) is list:
            return x
        elif type(x) is np.ndarray:
            return x.tolist()
        else:
            return [x]
            
    def keepVariable(self, graph, outerKey, innerKey=None, extraInnerKey=None):
        if graph[outerKey]['Info']["Type"]=="TrainNormal":
            if innerKey=="accuracy":
                return True 
            if innerKey=="loss":
                return True
            if innerKey=="f1":
                return True 
            if innerKey=="p_and_r":
                return True
            if innerKey=="roc":
                return True
            if innerKey=="auc":
                return True
        if graph[outerKey]['Info']["Type"]=="TrainReinforce":
            if innerKey=="accuracy":
                return True
            if extraInnerKey=="Reward":
                return True
            if extraInnerKey=="Done":
                return True
            if innerKey=="loss":
                return True
        return False

    def stackVariable(self, graph, outerKey, innerKey=None, extraInnerKey=None):
        if graph[outerKey]['Info']["Type"]=="TrainNormal":
            if innerKey=="accuracy":
                return True 
            if innerKey=="loss":
                return True
            if innerKey=="f1":
                return True 
            if innerKey=="p_and_r":
                return True
            if innerKey=="roc":
                return True
            if innerKey=="auc":
                return True
        if graph[outerKey]['Info']["Type"]=="TrainReinforce":
            if innerKey=="accuracy":
                return True
            if extraInnerKey=="Reward":
                return True
            if extraInnerKey=="Done":
                return True
            if innerKey=="loss":
                return True
            # if extraInnerKey=="Action":
            #     return True
        if outerKey=="Gradient" or innerKey=="Gradient" or extraInnerKey=="Gradient":
            return True
        return False

    def getResults(self):
        return {
                "iter":self.iter,
                "epoch":self.epoch,
                "maxIter":self.maxIter,
                "maxEpochs":self.maxEpochs,
                "batch_size":self.batch_size,
                "graphObj":self.graphObj,
                "trainingIterations":self.trainingIterations,
                "trainDict":copy.deepcopy(self.trainDict),
                "testIter":self._testIter,
                "maxTestIter":self.maxTestIter,
                "testDict":copy.deepcopy(self.testDict),
                "trainingStatus":self.trainingStatus,
                "status":self.status
                }


    def setStatus(self,status):
        self.status=status

    def headlessOn(self):
        self.headlessOnFlag=True

    def headlessOff(self):
        self.headlessOffFlag=True

    def nextTestStep(self):
        self.testStatus="nextStep"

    def prevousTestStep(self):
        self.testStatus="previousStep"

    def resetTest(self):
        self.testStatus="Reset"

    def playTest(self):
        if self.testStatus!="Running":
            # if self.testIter>=self.maxTestIter-1:
            #     self.testStatus="ResetAndRun"
            # else:
            self.testStatus="Running"
        else:
            self.testStatus="Waiting"
    
    def startTest(self):
        self.trainingStatus="Testing"
        
    def skip(self):
        if self.trainingStatus=="Validation":
            self.iter=0
            self.epoch+=1
            if self.epoch<self.maxEpochs:
                self.trainingStatus="Training"
            else:
                self.trainingStatus="Test"

    def saveNetwork(self, path, frontendNetwork):
        if not os.path.exists(path):   
            os.mkdir(path)
        checkpoint=[None, os.path.relpath(self.exporter.asTfModel(path,self.epoch),path)]
        print("Checkpoint: ", checkpoint)
        from networkSaver import saveNetwork
        newPath=os.path.abspath(path+"/"+str(self.networkName)+".json")
        saveNetwork(newPath, self.outputVariables, self.graphObj, frontendNetwork, checkpoint)


    # def exportNetwork(self,sess,saver,graphObj,outputDict,value):
    #     print("Exporting")
    #     path=os.path.abspath(value["Location"]+"/"+str(self.networkName))
    #     if value["Type"]=="TFModel":
    #         if value["Compressed"]:
    #             graph=graphObj.graphs

    #             start_nodes=graphObj.start_nodes
    #             end_points=graphObj.end_points
    #             network_outputs=[]
    #             for end_point in end_points:
    #                 if graph[end_point]["Info"]["Type"]=="TrainNormal":
    #                     for connection in graph[end_point]["Con"]:
    #                         if connection==graph[end_point]["Info"]["Properties"]["Labels"]:
    #                             pass
    #                         else:
    #                             network_outputs.append(connection)
    #                 elif graph[end_point]["Info"]["Type"]=="TrainReinforce":
    #                     for connection in graph[end_point]["Con"]:
    #                         if not graph[connection]["Info"]["Copy"]:
    #                             network_outputs.append(connection)

    #             network_inputs=[]
    #             queue=network_outputs[:]
    #             while queue:
    #                 Id=queue.pop()
    #                 if not graph[Id]["Info"]["backward_connections"]:
    #                     network_inputs.append(Id)
    #                 else:
    #                     queue.extend(graph[Id]["Info"]["backward_connections"])

    #             # tf.train.write_graph(sess.graph_def, "./model", "saved_model.pb", False)
    #             # # result,_=sess.run([output1,do_save], {input1: data}) # calculate output1 and assign to 'saved_result'
    #             # saver = tf.train.Saver(tf.all_variables())
    #             # saver.save(sess,"./model/checkpoint.data")
    #             # converter = tf.contrib.lite.TFLiteConverter.from_saved_model("./model")
    #             # print(converter)

    #             # grafDef=tf.graph_util.convert_variables_to_constants(sess, [graph[node]['Info']["Data"].data_placeholder for node in network_inputs], [outputDict[node] for node in network_outputs])
    #             # grafDef.convert()
    #             # converter=tf.contrib.lite.TocoConverter.from_session(sess, [graph[node]['Info']["Data"].data_placeholder for node in network_inputs], [outputDict[node] for node in network_outputs])
    #             # tflite_model = converter.convert()

    #             # saver = tf.train.Saver()
    #             # saver.save(sess, value["Location"]+"/model-1")
    #             # converter = tf.contrib.lite.TFLiteConverter.from_saved_model(value["Location"])
    #             # tflite_model = converter.convert()
    #             # open("converted_model.tflite", "wb").write(tflite_model)

    #             # print([graph[node]['Info']["Data"].placeholder for node in network_inputs])
    #             # print([outputDict[node] for node in network_outputs])
    #             converter = tf.lite.TFLiteConverter.from_session(sess, [graph[node]['Info']["Data"].placeholder for node in network_inputs], [outputDict[node] for node in network_outputs])
    #             converter.post_training_quantize=True
    #             # print(converter)
    #             tflite_model = converter.convert()
                
    #             # print("Got tflite_model")
    #             open(path+".tflite", "wb").write(tflite_model)
    #             # print("Saved tf model")
    #         else:
    #             # saver = tf.train.Saver()
    #             # saver.save(sess, path)
    #             graph=graphObj.graphs

    #             start_nodes=graphObj.start_nodes
    #             end_points=graphObj.end_points
    #             network_outputs=[]
    #             for end_point in end_points:
    #                 if graph[end_point]["Info"]["Type"]=="TrainNormal":
    #                     for connection in graph[end_point]["Con"]:
    #                         if connection!=graph[end_point]["Info"]["Properties"]["Labels"]:
    #                             network_outputs.append(connection)
    #                 elif graph[end_point]["Info"]["Type"]=="TrainReinforce":
    #                     for connection in graph[end_point]["Con"]:
    #                         if not graph[connection]["Info"]["Copy"]:
    #                             network_outputs.append(connection)

    #             network_inputs=[]
    #             queue=network_outputs[:]
    #             while queue:
    #                 Id=queue.pop()
    #                 if not graph[Id]["Info"]["backward_connections"]:
    #                     network_inputs.append(Id)
    #                 else:
    #                     queue.extend(graph[Id]["Info"]["backward_connections"])
    #             export_path=path
    #             if os.path.exists( export_path+"/1"):
    #                 shutil.rmtree( export_path+"/1")

    #             export_path = export_path+"/1"
    #             # builder = tf.saved_model.builder.SavedModelBuilder(export_path)
                
    #             # signature_def = tf.saved_model.build_signature_def(inputs={'input': [graph[node]['Info']["Data"].placeholder for node in network_inputs][0]}, outputs={'output':[outputDict[node] for node in network_outputs][0]})
    #             # with tf.Session(graph=tf.Graph()) as sess:
    #             #     builder.add_meta_graph_and_variables(sess,
    #             #                                         [tag_constants.TRAINING],
    #             #                                         signature_def_map=signature_def,
    #             #                                         strip_default_attrs=True)
    #             # # Add a second MetaGraphDef for inference.
    #             # with tf.Session(graph=tf.Graph()) as sess:
    #             #     builder.add_meta_graph([tag_constants.SERVING], strip_default_attrs=True)

    #             # builder.save()
    #             tf.saved_model.simple_save(sess, export_path, inputs={'input': [graph[node]['Info']["Data"].placeholder for node in network_inputs][0]}, outputs={'output':[outputDict[node] for node in network_outputs][0]})
    #             # saver = tf.train.Saver()
    #             saver.save(sess, export_path+'/model.ckpt', global_step=self.epoch)

    #     if value["Type"]=="Docker":
    #         if value["Compressed"]:
    #             pass
    #         else:
    #             pass
    #     if value["Type"]=="Raw":
    #         pass
    #     return "ExportSuccess"
        

    def Close(self,sess):
        sess.close()
        return

    def saveTempNetwork(self):
        pass

    def closeThread(self):
        pass
    
    def resetVariables(self):
        self.status="Done training"
        self.trainingStatus="Waiting"
        tf.reset_default_graph()
        self.resultDict=None
        self.outputVariablesStructure=dict()

        self.trainingVariables=None
        self.validationVariables=None
        self.resultDict=None
        self.outputVariablesStructure=dict()
        self.outputTensorStructure=dict()
        self.trainDict=dict()
        self.testDict=dict()
        if self.sess:
            self.sess.close()


if __name__ == "__main__":
    
    import queue
    warningQueue=queue.Queue()
    errorQueue=queue.Queue()
    commandQ=queue.Queue()
    resultQ=queue.LifoQueue()

    import json

    with open('net.json', 'r') as f:
        jsonNetwork = json.load(f)
    
    core = core("Name")
    core.startNetwork(warningQueue, errorQueue, commandQ, resultQ, jsonNetwork)

    
