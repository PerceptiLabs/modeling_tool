from CoreThread import CoreThread
from core import core
from createDataObject import createDataObject
import queue
import numpy as np
import time
import psutil
import copy
import traceback
import os

from core_new.core import *
from core_new.data import DataContainer

import logging
log = logging.getLogger(__name__)

class coreLogic():
    def __init__(self,networkName):
        self.networkName=networkName
        self.warningQueue=queue.Queue()
        self.errorQueue=queue.Queue()
        self.commandQ=queue.Queue()
        self.resultQ=queue.LifoQueue()
        # self.resultQ=queue.Queue()
        self.cThread=None

        self.trainResults=None
        self.testResults=None

        self.status="Created"

        self.core=core(self.networkName)

        self.savedResultsDict=dict()

        self.network=None

    def startCore(self,network):
        #Start the backendthread and give it the network
        self.network=network

        # graph = Graph(network).graphs
        # mode = 'headless'

        # data_container = DataContainer()    
        # session_history = SessionHistory()
        
        # layer_extras_reader = LayerExtrasReader()

        # lw_core = LightweightCore(CodeHq, graph_dict, data_container, session_history, layer_extras_reader)    
        # lw_core.run()
        # print(ler.to_dict())

        # import pdb; pdb.set_trace()

        # self.commandQ=queue.Queue()
        # self.resultQ=queue.LifoQueue()


        # session_history = SessionHistory()        
        # session_proc_handler = SessionProcessHandler(graph_dict, data_container,
        #                                              self.commandQ, self.resultQ, mode)
        # core = Core(CodeHq, graph_dict, data_container,
        #             session_history, session_proc_handler, mode=mode)
        # core.run()
        if self.cThread is None:
            try:
                self.cThread=CoreThread(self.core.startNetwork,self.warningQueue,self.errorQueue,self.commandQ,self.resultQ, network)
                self.cThread.start()
            except:
                self.errorQueue.put("Could not boot up the new thread to run the computations on")
            self.status="Running"
            return {"content": "core started"}
        else:
            if self.cThread.isAlive():
                self.Stop()

                while self.cThread.isAlive():
                    time.sleep(0.05)

                try:
                    self.cThread=CoreThread(self.core.startNetwork,self.warningQueue,self.errorQueue,self.commandQ,self.resultQ, network)
                    self.cThread.start()
                    #self.status="Setup"
                except:
                    self.errorQueue.put("Could not boot up the new thread to run the computations on")
            else:
                try:
                    self.cThread=CoreThread(self.core.startNetwork,self.warningQueue,self.errorQueue,self.commandQ,self.resultQ, network)
                    self.cThread.start()
                    #self.status="Setup"
                except:
                    self.errorQueue.put("Could not boot up the new thread to run the computations on")
                    #self.status="SetupFailed"
            self.status="Running"
        return {"content":"core started"}

    def onThread(self, function, *args, **kwargs):
        print(function)
        self.commandQ.put((function, args, kwargs))

    def Pause(self):
        if self.core.testStatus!="nextStep" or self.core.testStatus!="previousStep":
            if self.status=="Paused":
                self.status="Running"
            else:
                self.status="Paused"
        return {"content":self.setCoreStatus(self.status)}

    def Close(self):
        self.status="Stop"
        self.setCoreStatus(self.status)
        if self.core.sess:
            self.core.sess.close()
        if self.cThread is not None:
            while self.cThread.isAlive():
                time.sleep(0.05)
            self.cThread.join()
            print("Core Killed!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return {"content":"closing the core"}

    def headlessOn(self):
        self.onThread(self.core.headlessOn)

    def headlessOff(self):
        self.onThread(self.core.headlessOff)

    def Stop(self):
        self.status="Stop"
        return {"content":self.setCoreStatus(self.status)}

    def checkCore(self):
        return {"content":"Alive"}

    def setCoreStatus(self,status):
        self.onThread(self.core.setStatus,status)
        return {"content":"current status is: " + str(status)}

    def isTrained(self,):
        return {"content":self.core.exporter is not None}

    def exportNetwork(self,value):
        if self.core.exporter is None:
            self.warningQueue.put("Export failed.\nMake sure you have started running the network before you try to Export it.")
            return {"content":"Export Failed.\nNo trained weights to Export."}
        try:
            if value["Type"]=="TFModel":
                path=os.path.abspath(value["Location"]+"/"+str(self.networkName))
                if value["Compressed"]:
                    self.core.exporter.asCompressedTfModel(path)
                else:
                    self.core.exporter.asTfModel(path,self.core.epoch)
                return {"content":"Export success!\nSaved as:\n" + path}
            
        except Exception as e:
            self.warningQueue.put("Export Failed with this error: ")
            self.warningQueue.put(str(e))
            print("Export failed")
            print(traceback.format_exc())
            return {"content":"Export Failed with this error: " + str(e)}

    def saveNetwork(self,value):
        if self.core.exporter is None:
            self.warningQueue.put("Save failed.\nMake sure you have started running the network before you try to Export it.")
            return {"content":"Save Failed.\nNo trained weights to Export."}
        try:
            # path=os.path.abspath(value["Location"]+"/"+str(self.networkName))
            # value["Location"]="C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Networks"
            path=os.path.abspath(value["Location"][0]+"/"+str(self.networkName))
            self.core.saveNetwork(path,value["frontendNetwork"])
            return {"content":"Save succeeded!"}
        except Exception as e:
            self.warningQueue.put("Save Failed with this error: ")
            self.warningQueue.put(str(e))
            print("Save failed")
            print(traceback.format_exc())
            return {"content":"Save Failed with this error: " + str(e)}

        
        # if self.core.sess is None or self.core.graphObj is None or self.core.outputDict is None:
        #     self.warningQueue.put("Export failed.\nMake sure you have started running the network before you try to Export it.")
        #     return {"content":"Export Failed.\nNo trained weights to Export."}
        # try:
        #     #The reason we need to send so many self variables (especially Saver instead of initializing it in the export function) is because we need everything to be initialized
        #     #in the thread. When we run this function it is not run on the thread, but rather run in the main thread with variables taken from the thread. If we want to run
        #     #the function on the thread, we need a queue system to call the function and check for reply, and we need to make sure the thread never is terminated.
        #     self.core.exportNetwork(self.core.sess,self.core.saver,self.core.graphObj,self.core.outputDict,value)
        #     return {"content":"Export success!\nSaved in:\n" + str(value["Location"])}
        # except Exception as e:
        #     self.warningQueue.put("Export Failed with this error: ")
        #     self.warningQueue.put(str(e))
        #     print("Export failed")
        #     print(traceback.format_exc())
        #     return {"content":"Export Failed with this error: " + str(e)}





        # if self.cThread is not None:
        #     self.onThread(self.core.exportNetwork,value)
        #     while True:
        #         if not self.resultQ.empty():
        #             resultMessage=self.resultQ.get()
        #             print(resultMessage)
        #             if type(resultMessage) is str:
        #                 #Can catch warnings or more specific errors here as well if we want.
        #                 if resultMessage=="ExportSuccess":
        #                     return {"content":"Export success! \n Saved in: " + str(value["Location"])}
        #                 if resultMessage=="ExportFailed":
        #                     return {"conent":"Export Failed"}
        #             time.sleep(0.2)

    def skipValidation(self):
        self.onThread(self.core.skip)
        #Check if validation was skipped or not before returning message
        return {"content":"skipped validation"}

    def getTestStatus(self):
        try:
            if self.savedResultsDict["maxTestIter"]!=0:
                if self.status=="Running":
                    return {"Status":self.savedResultsDict["trainingStatus"],"Iterations":self.savedResultsDict["testIter"], "Progress": self.savedResultsDict["testIter"]/(self.savedResultsDict["maxTestIter"]-1)}
                else:
                    return {"Status":self.status,"Iterations":self.savedResultsDict["testIter"], "Progress": self.savedResultsDict["testIter"]/(self.savedResultsDict["maxTestIter"]-1)}
            else:
                print("Max Test Iterations are 0")
                return {"content":"Max Test Iterations are 0"}
        except KeyError:
            return {}
        # if self.core.testIterations!=0:
        #     if self.status=="Running":
        #         return {"Status":self.core.trainingStatus,"Iterations":self.core.testIter, "Progress": self.core.testIter/(self.core.testIterations-1)}
        #     else:
        #         return {"Status":self.status,"Iterations":self.core.testIter, "Progress": self.core.testIter/(self.core.testIterations-1)}
        # else:
        #     print("Test Iterations are 0")

    def getStatus(self):
        try:
            if self.status=="Running":
                return {"Status":self.savedResultsDict["trainingStatus"],"Iterations":self.savedResultsDict["iter"],"Epoch":self.savedResultsDict["epoch"], "Progress": (self.savedResultsDict["epoch"]*self.savedResultsDict["maxIter"]+self.savedResultsDict["iter"])/(max(self.savedResultsDict["maxEpochs"]*self.savedResultsDict["maxIter"],1)), "CPU":psutil.cpu_percent(), "Memory":dict(psutil.virtual_memory()._asdict())["percent"]}
            else:
                return {"Status":self.status,"Iterations":self.savedResultsDict["iter"],"Epoch":self.savedResultsDict["epoch"], "Progress": (self.savedResultsDict["epoch"]*self.savedResultsDict["maxIter"]+self.savedResultsDict["iter"])/(max(self.savedResultsDict["maxEpochs"]*self.savedResultsDict["maxIter"],1)), "CPU":psutil.cpu_percent(), "Memory":dict(psutil.virtual_memory()._asdict())["percent"]}
        except KeyError:
            return {}
        # if self.status=="Running":
        #     return {"Status":self.core.trainingStatus,"Iterations":self.core.iter,"Epoch":self.core.epoch, "Progress": (self.core.epoch*self.core.maxIter+self.core.iter)/(max(self.core.maxEpochs*self.core.maxIter,1))}
        # else:
        #     return {"Status":self.status,"Iterations":self.core.iter,"Epoch":self.core.epoch, "Progress": (self.core.epoch*self.core.maxIter+self.core.iter)/(max(self.core.maxEpochs*self.core.maxIter,1))}

    def startTest(self):
        if self.core.maxTestIter>0:
            self.onThread(self.core.startTest)
            while self.core.testStatus!="Waiting":
                time.sleep(0.05)
            return {"content":"Started Testing"}
        else:
            return {"content":"No test data"}

    def nextStep(self):
        testIter=self.core.testIter
        self.onThread(self.core.nextTestStep)
        while testIter==self.core.testIter:
            time.sleep(0.05)
        return {"content":"Current sample is: "+str(self.core.testIter)}
    
    def previousStep(self):
        testIter=self.core.testIter
        self.onThread(self.core.prevousTestStep)
        while testIter==self.core.testIter and testIter>1:
            time.sleep(0.05)
        return {"content":"Current sample is: "+str(self.core.testIter)}

    def resetTest(self):
        self.onThread(self.core.resetTest)
        while self.core.testIter>1:
            time.sleep(0.05)
        return {"content":"Test is now back to iter 1"}

    def playTest(self):
        self.onThread(self.core.playTest)
        return {"content":"Current sample is: "+str(self.core.testIter)}

    def updateResults(self):
        if not self.resultQ.empty():
            self.savedResultsDict=self.resultQ.get()
            with self.resultQ.mutex:
                self.resultQ.queue.clear()

            import json
            with open('results.json') as f:
                json.dumps(f, self.savedResultsDict)
            

        return {"content":"Results saved"}

    def getTrainingStatistics(self,value):
        try:
            self.iter=self.savedResultsDict["iter"]
            self.epoch=self.savedResultsDict["epoch"]
            self.maxIter=self.savedResultsDict["maxIter"]
            self.maxEpochs=self.savedResultsDict["maxEpochs"]
            self.batch_size=self.savedResultsDict["batch_size"]
            self.graphObj=self.savedResultsDict["graphObj"]
            self.trainingIterations=self.savedResultsDict["trainingIterations"]
            self.resultDict=self.savedResultsDict["trainDict"]
        except KeyError:
            return {}

        return self.getLayerStatistics(value)


    def getTestingStatistics(self,value):
        try:
            self.iter=self.savedResultsDict["testIter"]
            self.maxIter=self.savedResultsDict["maxTestIter"]
            self.batch_size=1
            self.graphObj=self.savedResultsDict["graphObj"]
            self.trainingIterations=self.savedResultsDict["trainingIterations"]
            self.resultDict=self.savedResultsDict["testDict"]
        except KeyError:
            return {}

        return self.getLayerStatistics(value)

    
    def getLayerStatistics(self,value):
        layerId=value["layerId"]
        layerType=value["layerType"]
        view=value["view"]
        log.info("getLayerStatistics for layer {} with type {}. View: {}".format(layerId,
                                                                                 layerType,
                                                                                 view))
        ##########################################
        value["viewId"]="0"
        ##########################################

        if layerType=="DataEnvironment":
            state = self.getStatistics({"layerId":layerId,"variable":"state","innervariable":""})
            dataObj = createDataObject([state])
            return {"Data":dataObj}            
        elif layerType=="DataData":
            D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})
            dataObj = createDataObject([D[-1]])      
            return {"Data":dataObj}
        elif layerType=="DeepLearningFC":
            if view=="Output":
                D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1]
                dataObject = createDataObject([D])                
                output = {"Output": dataObject}
                return output
            if view=="Weights&Bias":
                w=self.getStatistics({"layerId":layerId,"variable":"W","innervariable":""})
                w=np.average(w,axis=0)
                dataObjectWeights = createDataObject([w], typeList=['line'])
                
                b=self.getStatistics({"layerId":layerId,"variable":"b","innervariable":""})
                dataObjectBias = createDataObject([b], typeList=['line'])
                
                output = {"Bias": dataObjectBias, "Weights": dataObjectWeights}
                return output
            if view=="Gradients":
                minD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Min"})
                maxD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Max"})
                avD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Average"})

                dataObj = createDataObject([minD, maxD, avD],
                                           typeList=3*['line'],
                                           nameList=['Min', 'Max', 'Average'],
                                           styleList=[{"color":"#83c1ff"},
                                                      {"color":"#0070d6"},
                                                      {"color":"#6b8ff7"}])
                output = {"Gradients": dataObj}
                return output
        elif layerType=="DeepLearningConv":
            if view=="Weights&Output":
                weights=self.getStatistics({"layerId":layerId,"variable":"W","innervariable":""})                
                Wshapes=weights.shape
                if len(Wshapes)==3:
                    weights=np.expand_dims(np.average(weights[:,:,-1],1),axis=0)
                elif len(Wshapes)==4:
                    weights=np.average(weights[:,:,:,-1],2)
                elif len(Wshapes)==5:
                    weights=np.average(weights[:,:,:,:,-1],3)

                outputs=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1]
                outputs=outputs[:,:,int(value["viewId"])]
                    
                dataObjWeights = createDataObject([weights], typeList=['heatmap'])
                dataObjOutput = createDataObject([outputs])                

                obj = {"Weights":dataObjWeights, "Output": dataObjOutput}
                return obj
            if view=="Bias":
                b=self.getStatistics({"layerId":layerId,"variable":"b","innervariable":""})
                dataObj = createDataObject([b], typeList=['line'])
                output = {"Bias": dataObj}
                return output
            if view=="Gradients":
                minD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Min"})
                maxD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Max"})
                avD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Average"})

                dataObj = createDataObject([minD, maxD, avD],
                                           typeList=3*['line'],
                                           nameList=['Min', 'Max', 'Average'],
                                           styleList=[{"color":"#83c1ff"},
                                                      {"color":"#0070d6"},
                                                      {"color":"#6b8ff7"}])
                output = {"Gradients": dataObj}
                return output
        elif layerType=="DeepLearningDeconv":
            if view=="Weights&Output":
                weights=self.getStatistics({"layerId":layerId,"variable":"W","innervariable":""})                
                Wshapes=weights.shape
                if len(Wshapes)==3:
                    weights=np.expand_dims(np.average(weights[:,:,-1],1),axis=0)
                elif len(Wshapes)==4:
                    weights=np.average(weights[:,:,:,-1],2)
                elif len(Wshapes)==5:
                    weights=np.average(weights[:,:,:,:,-1],3)

                outputs=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1]
                outputs=outputs[:,:,int(value["viewId"])]
                    
                dataObjWeights = createDataObject([weights], typeList=['heatmap'])
                dataObjOutput = createDataObject([outputs])                

                obj = {"Weights":dataObjWeights, "Output": dataObjOutput}
                return obj
            if view=="Bias":
                b=self.getStatistics({"layerId":layerId,"variable":"b","innervariable":""})
                dataObj = createDataObject([b], typeList=['line'])
                output = {"Bias": dataObj}
                return output
            if view=="Gradients":
                minD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Min"})
                maxD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Max"})
                avD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Average"})

                dataObj = createDataObject([minD, maxD, avD],
                                           typeList=3*['line'],
                                           nameList=['Min', 'Max', 'Average'],
                                           styleList=[{"color":"#83c1ff"},
                                                      {"color":"#0070d6"},
                                                      {"color":"#6b8ff7"}])
                output = {"Gradients": dataObj}
                return output
        elif layerType=="DeepLearningRecurrent":
            if view=="Output":
                D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1]
                dataObject = createDataObject([D], typeList=['line'])                
                dataObject = {"Output": dataObject}
                return dataObject

            if view=="Weights&Bias":
                # w=self.getStatistics({"layerId":layerId,"variable":"W","innervariable":""})
                # w=np.average(w,axis=0)
                w=np.array([])
                # b=self.getStatistics({"layerId":layerId,"variable":"b","innervariable":""})
                b=np.array([])
                
                dataObjectWeights = createDataObject([w], typeList=['line'])
                dataObjectBias = createDataObject([b], typeList=['line'])
                
                output = {"Bias": dataObjectBias, "Weights": dataObjectWeights}
                return output
            if view=="Gradients":
                # minD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Min"})
                # maxD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Max"})
                # avD=self.getStatistics({"layerId":layerId,"variable":"Gradient","innervariable":"Average"})
                minD=np.array([])
                maxD=np.array([])
                avD=np.array([])

                dataObj = createDataObject([minD, maxD, avD],
                                           typeList=3*['line'],
                                           nameList=['Min', 'Max', 'Average'],
                                           styleList=[{"color":"#83c1ff"},
                                                      {"color":"#0070d6"},
                                                      {"color":"#6b8ff7"}])
                output = {"Gradients": dataObj}
                return output
        elif layerType in ["MathMerge", "MathSoftmax", "MathArgmax", "ProcessOneHot", "ProcessCrop", "ProcessReshape", "ProcessGrayscale"]:
            D=self.getStatistics({"layerId":layerId,"variable":"Y","innervariable":""})[-1]
            output = createDataObject([D])
            return {"Output":output}
        elif layerType=="TrainNormal":
            if view=="Prediction":
                #Make sure that all the inputs are sent to frontend!!!!!!!!!!!!!!!
                inputs=[self.getStatistics({"layerId":i,"variable":"Y","innervariable":""})[-1] for i in self.graphObj.start_nodes]
                D = [createDataObject([input_]) for input_ in inputs]
                
                X=self.getStatistics({"layerId":layerId,"variable":"X","innervariable":""})
                
                if type(X) is dict:
                    for key,value in X.items():
                        try:
                            int(key)
                            if key==self.graphObj.graphs[layerId]["Info"]["Properties"]["Labels"]:
                                Labels=value
                            else:
                                Network_output=value
                        except:
                            pass
                        
                    cType=self.getPlot(Network_output[-1])

                    if cType=="bar" or cType=="line":
                        PvG = createDataObject([Network_output[-1], Labels[-1]], nameList=['Prediction', 'Ground Truth'])                        

                        # average over samples
                        network_average=np.average(Network_output,axis=0)
                        labels_average = np.average(Labels, axis=0)
                        APvG = createDataObject([network_average, labels_average], nameList=['Prediction', 'Ground Truth'])
                        
                        # PIE
                        acc=self.getStatistics({"layerId":layerId,"variable":"accuracy","innervariable":""})
                        try:
                            lastAcc=acc[-1]
                        except:
                            lastAcc=acc

                        accList = [[('Accuracy', lastAcc*100.0), ('Empty', (1-lastAcc)*100.0)]]
                        Accuracy = createDataObject(accList, typeList=['pie'])
                        returnDict={"Input":D[0],"PvG":PvG,"AveragePvG":APvG,"Accuracy":Accuracy}

                    elif cType=="grayscale" or cType=="RGB" or cType=="heatmap":
                        Network_output=self.subsample(Network_output)
                        Labels=self.subsample(Labels)
                        (height,width)=Network_output.shape[0:2]
                        Mask = createDataObject([Network_output], typeList=['heatmap'])
                        Prediction = createDataObject([Labels], typeList=['heatmap'])
                        
                        # PIE
                        acc=self.getStatistics({"layerId":layerId,"variable":"accuracy","innervariable":""})
                        try:
                            lastAcc=acc[-1]
                        except:
                            lastAcc=acc

                        accList = [[('Accuracy', lastAcc*100.0), ('Empty', (1-lastAcc)*100.0)]]
                        Accuracy = createDataObject(accList, typeList=['pie'])
                        returnDict={"Input":D[0],"PvG":Mask,"AveragePvG":Prediction,"Accuracy":Accuracy}                    
                else:
                    chartType="line"
                    if np.shape(X[-1])[0]<10:
                        chartType="bar"

                    APvGD=np.average(X,axis=0)
                    PvG = createDataObject([X[-1]], typeList=[chartType])
                    APvG = createDataObject([APvGD], typeList=[chartType])
                    returnDict={"Input":D[0],"PvG":PvG,"AveragePvG":APvG}
                return returnDict

            if view=="Accuracy":
                acc=self.getStatistics({"layerId":layerId,"variable":"accuracy","innervariable":""})
                
                currentTraining=acc[:self.trainingIterations]
                currentValidation=acc[:self.maxIter]
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"epochTrainAccuracy","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"epochValAccuracy","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
                
            if view=="Loss":
                loss=self.getStatistics({"layerId":layerId,"variable":"loss","innervariable":""})

                currentTraining=loss[:self.trainingIterations]
                currentValidation=loss[:self.maxIter]
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"epochTrainLoss","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"epochValLoss","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
            if view=="F1":
                f1=self.getStatistics({"layerId":layerId,"variable":"f1","innervariable":""})

                currentTraining=f1[:self.trainingIterations]
                currentValidation=f1[:self.maxIter]
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"epochTrainF1","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"epochValF1","innervariable":""})



                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
            if view=="Precision&Recall":
                pr=self.getStatistics({"layerId":layerId,"variable":"p_and_r","innervariable":""})

                currentTraining=pr[:self.trainingIterations]
                currentValidation=pr[:self.maxIter]
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"epochTrainPandR","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"epochValFPandR","innervariable":""})
                
                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
            if view=="ROC":
                roc=self.getStatistics({"layerId":layerId,"variable":"roc","innervariable":""})

                currentTraining=roc[:self.trainingIterations]
                currentValidation=roc[:self.maxIter]
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"epochTrainROC","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"epochValROC","innervariable":""})
                
                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output            
            if view=="AUC":
                auc=self.getStatistics({"layerId":layerId,"variable":"auc","innervariable":""})
                
                currentTraining=auc[:self.trainingIterations]
                currentValidation=auc[:self.maxIter]
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"epochTrainAUC","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"epochValAUC","innervariable":""})


                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output

        elif layerType=="TrainReinforce":
            if view=="Prediction":
                state = self.getStatistics({"layerId":layerId,"variable":"state","innervariable":""})
                state_ = createDataObject([state])

                prediction = self.getStatistics({"layerId":layerId,"variable":"pred","innervariable":""})
                prediction = createDataObject([prediction[0]], typeList=['line'])
                
                output = {"Input":state_, "Prediction": prediction}
                return output

            if view=="Reward":
                currentReward=self.getStatistics({"layerId":layerId,"variable":"X","innervariable":"Reward"})
                totalReward=self.getStatistics({"layerId":layerId,"variable":"X","innervariable":"epochTotalReward"})


                # doneState=self.getStatistics({"layerId":layerId,"variable":"X","innervariable":"Done"})
                # allDones=np.where(doneState==True)[0]
                # if allDones.size>0:
                #     for i in range(len(allDones)):
                #         if i>0:
                #             r[allDones[i-1]:allDones[i]]=np.cumsum(r[allDones[i-1]:allDones[i]])
                #         else:
                #             r[0:allDones[i]]=np.cumsum(r[0:allDones[i]])
                #     r[allDones[-1]:]=np.cumsum(r[allDones[i]:])
                # else:
                #     r=np.cumsum(r)

                # currentReward=r[int(allDones[-1] if allDones.size>0 else 0):int(doneState.size)]
                # totalReward=np.array([r[int(i-1)] for i in allDones]) if allDones.size>0 else np.array([])
                current_reward = createDataObject([currentReward])
                total_reward = createDataObject([totalReward])
                obj = {"Current": current_reward, "Total": total_reward}
                return obj
            if view=="Loss":
                currentLoss=self.getStatistics({"layerId":layerId,"variable":"loss","innervariable":""})
                totalLoss=self.getStatistics({"layerId":layerId,"variable":"epochTrainLoss","innervariable":""})
                
                current_loss = createDataObject([currentLoss])
                total_loss = createDataObject([totalLoss])
                obj = {"Current": current_loss, "Total": total_loss}
                return obj
            if view=="Steps":
                steps=self.getStatistics({"layerId":layerId,"variable":"X","innervariable":"epochTotalSteps"})
                steps = createDataObject([steps])
                obj = {"Steps": steps}
                return obj
        else:
            return "FieldError: Does not recognize the layerType. " + layerType + " is not in [Train, Fc, Conv, Deconv, Argmax, Softmax, Merge, OneHot, Crop, Reshape, Grayscale]"

    def getPlot(self,D):
        shape=np.squeeze(D).shape
        if len(shape)==0:
            t="scatter"
        elif len(shape)==1:
            if shape[0]<25:
                t="bar"
            else:
                t="line"
        elif len(shape)==2:
            t="grayscale"
        elif len(shape)==3:
            if shape[-1]==1:
                t="grayscale"
            elif shape[-1]==3:
                t="RGB"    #Assume RGB, Replace with a button later on
            # elif np.shape(np.squeeze(self.variables[self.currentView]["input"]))[0]==np.shape(np.squeeze(self.variables[self.currentView]["input"]))[1]==np.shape(np.squeeze(self.variables[self.currentView]["input"]))[2]:
            #     pass
            else:
                t="heatmap"
            #     self.plot1.imshow(self.variables[self.currentView]["input"][:,:,0])
        else:
            t="scatter" #Just something which works for all
        return t

    # def recursive_items(self,dictionary):
    #     for key, value in dictionary.items():
    #         if type(value) is dict:
    #             yield from self.recursive_items(value)
    #         else:
    #             yield (key, value)

    def getStatistics(self,statSpec):
        #print(sess.run([outputVariables["6"]["accuracy"]],feed_dict=dict(zip(keys, values))))

        layerId=statSpec["layerId"]
        variable=statSpec["variable"]
        innervariable=statSpec["innervariable"]
        log.debug("getStatistics for layer {}, variable {}, innervariable {}".format(layerId,
                                                                                     variable,
                                                                                     innervariable))
        
        if self.resultDict is not None:
            # print("All keys available: ",str(list(self.resultDict.keys())))
            if innervariable!="":
                try:
                    result=self.resultDict[layerId][variable][innervariable]
                except:
                    try:
                        print("FieldError, only keys available are: "+str(list(self.resultDict[layerId][variable].keys()))+" |||| Expected: "+str(innervariable))
                        self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict[layerId][variable].keys()))+" |||| Expected: "+str(innervariable))
                    except:
                        try:
                            print("FieldError, only keys available are: "+str(list(self.resultDict[layerId].keys()))+" |||| Expected: " + str(variable))
                            self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict[layerId].keys()))+" |||| Expected: " + str(variable))
                        except:
                            print("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                            self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))

                    result=[]
            elif variable!="":
                try:
                    result=self.resultDict[layerId][variable]
                except:
                    try:
                        print("FieldError, only keys available are: "+str(list(self.resultDict[layerId].keys()))+" |||| Expected: " + str(variable))
                        self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict[layerId].keys()))+" |||| Expected: " + str(variable))
                    except:
                        print("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                        self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                    result=[]
            else:
                try:
                    result=self.resultDict[layerId]
                except:
                    print("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                    self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                    result=[]
        else:
            print("ResultDict is empty :'(")
            self.warningQueue.put("There are no results to fetch")
            result=[]

        if type(result).__name__!='dict':
            result=np.asarray(result)
            # if result.shape:
            #     if result.shape[0]!=self.batch_size and not self.core.stackVariable(self.savedResultsDict["graphObj"].graphs,layerId,variable,innervariable):
            #         # if self.batch_size==1:
            #         #     result=np.reshape(result, [1,*result.shape])
            #         self.warningQueue.put("Dimensionality of the batch size is not correct in layer: "+ str(layerId) + " variable: " + str(variable) + " innervariable: " + str(innervariable) + " , Data size is: " + str(np.shape(result)) + " and Batch size is: " + str(self.batch_size))
            #         print("Dimensionality of the batch size is not correct in layer: "+ str(layerId) + " variable: " + str(variable) + " innervariable: " + str(innervariable) + " , Data size is: " + str(np.shape(result)) + " and Batch size is: " + str(self.batch_size))

        return result

    def subsample(self,sample):
        endSize=500
        if len(sample.shape)==1:
            length=sample.size
            if length>endSize:
                lenRatio=length/endSize
            else:
                lenRatio=1
            result=sample[::int(lenRatio)]

        elif len(sample.shape)>=2:
            height,width=sample.shape[0:2]
            if height>endSize or width>endSize:
                if height>width:
                    heightRatio=widthRatio=height/endSize
                else:
                    heightRatio=widthRatio=width/endSize
            else:
                heightRatio=widthRatio=1
            result=sample[::int(np.ceil(heightRatio)),::int(np.ceil(widthRatio))]
        else:
            result=sample

        return result

    # def rgb2gray(rgb):
    #     return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

    def convertToList(self,npy):
        if len(npy.shape)==0:
            if isinstance(npy, np.integer):
                npy=[int(npy)]
            elif isinstance(npy, np.floating):
                npy=[float(npy)]
        elif len(npy.shape)==1:
            # npy=list(npy)
            npy=npy.tolist()
        elif len(npy.shape)>1:
            npy=npy.tolist()
        return npy

    def grayscale2RGBa(self,data):
        data=np.squeeze(data)
        (w,h)=np.shape(data)
        newData=np.empty((w, h, 4))
        
        if data.max()!=0:
            normalizedData=np.around((data/data.max())*255)
        else:
            normalizedData=data
        newData[:, :, 0] = normalizedData
        newData[:, :, 1] = newData[:, :, 2] = newData[:, :, 0]
        newData[:,:,3]=255
        flatData=np.reshape(newData,-1)

        return flatData

    def RGB2RGBa(self,data):
        data=np.squeeze(data)
        (w,h,d)=np.shape(data)
        newData=np.empty((w, h, 4))
        normalizedData=np.around((data/data.max(0).max(0))*255)
        newData[:, :, 0:3] = normalizedData
        newData[:,:,3]=255
        flatData=np.reshape(newData,-1)
        return flatData
