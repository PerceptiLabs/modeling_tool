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
import threading
import pprint
import logging

from networkExporter import exportNetwork
from networkSaver import saveNetwork

from modules import ModuleProvider
from core_new.core import *
from core_new.data import DataContainer
from core_new.errors import CoreErrorHandler
from core_new.history import SessionHistory
from analytics.scraper import get_scraper

log = logging.getLogger(__name__)
scraper = get_scraper()

class coreLogic():
    def __init__(self,networkName):
        self.networkName=networkName

        self.warningQueue=queue.Queue()
        self.errorQueue=queue.Queue()
        self.commandQ=queue.Queue()
        # self.resultQ=queue.LifoQueue()
        self.resultQ=queue.Queue()
        self.cThread=None

        self.trainResults=None
        self.testResults=None
        self.paused=False

        self.status="Created"

        self.testIter=0
        self.maxTestIter=0
        self.testList=[]
        self.playCounter=None
        self.playing=False
        
        self.saver=None

        #self.core=core(self.networkName)

        self.savedResultsDict={}

        self.network=None

    def startCore(self,network, checkpointValues):
        #Start the backendthread and give it the network
        self.network=network

        # import json
        # with open('net.json', 'w') as f:
        #     json.dump(network, f) 

        data_container = DataContainer()

        self.graphObj = Graph(network['Layers'])
        graph_dict=self.graphObj.graphs

        from codehq import CodeHqNew as CodeHq

        error_handler = CoreErrorHandler(self.errorQueue)
        

        module_provider = ModuleProvider()
        module_provider.load('tensorflow', as_name='tf')
        module_provider.load('numpy', as_name='np')
        module_provider.load('pandas', as_name='pd')
        module_provider.load('gym')
        module_provider.load('json')           

        session_history = SessionHistory()
        session_proc_handler = SessionProcessHandler(graph_dict, data_container, self.commandQ, self.resultQ)
        self.core = Core(CodeHq, graph_dict, data_container, session_history, module_provider,
                         error_handler, session_proc_handler, checkpointValues) 

        if self.cThread is not None and self.cThread.isAlive():
            self.Stop()

            while self.cThread.isAlive():
                time.sleep(0.05)

            try:
                # self.cThread=CoreThread(self.core.startNetwork,self.warningQueue,self.errorQueue,self.commandQ,self.resultQ, network)
                self.cThread=CoreThread(self.core.run,self.errorQueue)
                self.cThread.start()
            except Exception as e:
                self.errorQueue.put("Could not boot up the new thread to run the computations on because of: ", str(e))
        else:
            try:
                self.cThread=CoreThread(self.core.run,self.errorQueue)
                self.cThread.start()
            except Exception as e:
                self.errorQueue.put("Could not boot up the new thread to run the computations on because of: ", str(e))
        self.status="Running"
            
        return {"content":"core started"}


    def Pause(self):
        self.commandQ.put('pause')
        self.paused=True
        return {"content": "Paused"}
        
    def Unpause(self):
        self.commandQ.put('unpause')
        self.paused=False
        return {"content":"Unpaused"}

    def Close(self):
        return {"content":"closing the core"}

    def headlessOn(self):
        self.commandQ.put("headlessOn")

    def headlessOff(self):
        self.commandQ.put("headlessOff")

    def Stop(self):
        self.status="Stop"
        self.commandQ.put("stop")
        return {"content":"Stopping"}

    def checkCore(self):
        return {"content":"Alive"}

    def isTrained(self,):
        if self.saver:
            return {"content":True}
        else:
            return {"content":False}

    def exportNetwork(self,value):
        if self.saver is None:
            self.warningQueue.put("Export failed.\nMake sure you have started running the network before you try to Export it.")
            return {"content":"Export Failed.\nNo trained weights to Export."}
        try:
            exporter = exportNetwork(self.saver)
            if value["Type"]=="TFModel":
                path=os.path.abspath(value["Location"]+"/"+str(self.networkName))
                if value["Compressed"]:
                    exporter.asCompressedTfModel(path)
                else:
                    exporter.asTfModel(path,self.epoch)
                return {"content":"Export success!\nSaved as:\n" + path}
            
        except Exception as e:
            self.warningQueue.put("Export Failed with this error: ")
            self.warningQueue.put(str(e))
            print("Export failed")
            print(traceback.format_exc())
            return {"content":"Export Failed with this error: " + str(e)}

    def saveNetwork(self,value):
        if self.saver is None:
            self.warningQueue.put("Save failed.\nMake sure you have started running the network before you try to Export it.")
            return {"content":"Save Failed.\nNo trained weights to Export."}
        try:
            if "all_tensors" not in self.saver:
                raise Exception("'all_tensors' was not found so the Saver could not create any references to the expored checkpoints.\nTry adding 'api.data.store(all_tensors=api.data.get_tensors())' to your Training Layer.")
            elif self.saver["all_tensors"]==[]:
                raise Exception("'all_tensors' was found but contained no variables.")

            exporter = exportNetwork(self.saver)
            path=os.path.abspath(value["Location"][0])
            frontendNetwork=value["frontendNetwork"]
            if not os.path.exists(path):   
                os.mkdir(path)
            checkpoint=[None, os.path.relpath(exporter.asTfModel(path,self.epoch),path)]

            newPath=os.path.abspath(path+"/"+"model.json")
            saveNetwork(newPath, self.saver["all_tensors"], self.graphObj, frontendNetwork, checkpoint)

            return {"content":"Save succeeded!"}
        except Exception as e:
            self.errorQueue.put("Save Failed with this error: ")
            self.errorQueue.put(str(e))
            print("Save failed")
            print(traceback.format_exc())
            return {"content":"Save Failed with this error: " + str(e)}

    def skipValidation(self):
        self.commandQ.put("skip")
        #Check if validation was skipped or not before returning message
        return {"content":"skipped validation"}

    def getTestStatus(self):
        try:
            if self.savedResultsDict["maxTestIter"]!=0:
                if self.status=="Running":
                    return {"Status":self.savedResultsDict["trainingStatus"],"Iterations":self.testIter, "Progress": self.testIter/(self.savedResultsDict["maxTestIter"]-1)}
                else:
                    return {"Status":self.status,"Iterations":self.testIter, "Progress": self.testIter/(self.savedResultsDict["maxTestIter"]-1)}
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

    def get_cpu_and_mem(self):
        cpu = psutil.cpu_percent()
        mem = dict(psutil.virtual_memory()._asdict())["percent"]
        scraper.submit('cpu_and_mem', {'cpu': cpu, 'mem': mem})
        return cpu, mem
        
    def getStatus(self):
        try:
            cpu, mem = self.get_cpu_and_mem()
            if self.status=="Running":
                progress = (self.savedResultsDict["epoch"]*self.savedResultsDict["maxIter"]+self.savedResultsDict["iter"])/(max(self.savedResultsDict["maxEpochs"]*self.savedResultsDict["maxIter"],1))
                result = {
                    "Status":"Paused" if self.paused else self.savedResultsDict["trainingStatus"],
                    "Iterations": self.savedResultsDict["iter"],
                    "Epoch": self.savedResultsDict["epoch"],
                    "Progress": progress,
                    "CPU": cpu,
                    "Memory": mem
                }
                return result
            else:
                progress = (self.savedResultsDict["epoch"]*self.savedResultsDict["maxIter"]+self.savedResultsDict["iter"])/(max(self.savedResultsDict["maxEpochs"]*self.savedResultsDict["maxIter"],1))
                return {
                    "Status":"Paused" if self.paused else self.status,
                    "Iterations":self.savedResultsDict["iter"],
                    "Epoch":self.savedResultsDict["epoch"],
                    "Progress": progress,
                    "CPU":cpu,
                    "Memory":mem
                }
        except KeyError:
            return {}
        # if self.status=="Running":
        #     return {"Status":self.core.trainingStatus,"Iterations":self.core.iter,"Epoch":self.core.epoch, "Progress": (self.core.epoch*self.core.maxIter+self.core.iter)/(max(self.core.maxEpochs*self.core.maxIter,1))}
        # else:
        #     return {"Status":self.status,"Iterations":self.core.iter,"Epoch":self.core.epoch, "Progress": (self.core.epoch*self.core.maxIter+self.core.iter)/(max(self.core.maxEpochs*self.core.maxIter,1))}

    def startTest(self):
        #TODO: Remove this function
        if self.savedResultsDict["trainingStatus"]=='Testing' or self.savedResultsDict["trainingStatus"]=='Finished':
            return {"content":"Started Testing"}
        else:
            return {"content":"No test data"}

    def nextStep(self):
        if self.testIter<self.maxTestIter-1:
            self.testIter+=1
        else:
            self.resetTest()
        return {"content":"Current sample is: "+str(self.testIter)}
    
    def previousStep(self):
        if self.testIter>0:
            self.testIter-=1
        return {"content":"Current sample is: "+str(self.testIter)}

    def resetTest(self):
        self.testIter=0
        return {"content":"Test is now back to iter 1"}

    def increaseStep(self):
        while self.testIter<self.maxTestIter:
            if not self.playing:
                return
            self.testIter+=1
            time.sleep(0.5)
        self.playing=False
        return

    def playTest(self):
        if self.playCounter:
            self.playing=False
            self.playCounter.join()
            self.playCounter=None
        else:
            self.playing=True
            self.playCounter=threading.Thread(target=self.increaseStep)
            self.playCounter.start()

        return {"content": "Play started"}

    def updateResults(self):
        # if not self.resultQ.empty():
        #     self.savedResultsDict.update(self.resultQ.get())
        #     with self.resultQ.mutex:
        #         self.resultQ.queue.clear()

        #TODO: Look from the back and go forward if we find a test instead of going through all of them
        tmp=None

        while not self.resultQ.empty():
            tmp=self.resultQ.get()

            if "saver" in tmp:
                self.saver=tmp.pop("saver")
                # self.exporter = exportNetwork(saver)

            if "testDict" in tmp:
                self.testList.append(tmp["testDict"])
                if not self.maxTestIter:
                    self.maxTestIter = tmp['maxTestIter']
        if tmp:
            self.savedResultsDict.update(tmp)

        return {"content":"Results saved"}

    def getTrainingStatistics(self,value):
        try:
            self.iter=self.savedResultsDict["iter"]
            self.epoch=self.savedResultsDict["epoch"]
            self.maxIter=self.savedResultsDict["maxIter"]
            self.maxEpochs=self.savedResultsDict["maxEpochs"]
            self.batch_size=self.savedResultsDict["batch_size"]
            self.trainingIterations=self.savedResultsDict["trainingIterations"]
            self.resultDict=self.savedResultsDict["trainDict"]
        except KeyError:
            log.exception("Error in getTrainingStatistics")                        
            return {}


        try:
            layer_statistics = self.getLayerStatistics(value)
            return layer_statistics
        except:
            message = "Error in getTrainingStatistics."
            if log.isEnabledFor(logging.DEBUG):
                message += " savedResultsDict: " + pprint.pformat(self.savedResultsDict)
            log.exception(message)


    def getTestingStatistics(self,value):
        try:
            # self.maxTestIter=self.maxTestIter
            self.batch_size=1
            self.resultDict=self.testList[self.testIter]
        except KeyError as e:
            print(e)
            log.exception("Error in getTestingStatistics")            
            return {}

        try:
            layer_statistics = self.getLayerStatistics(value)
            return layer_statistics
        except Exception as e:
            print(e)
            message = "Error in getTestingStatistics."
            if log.isEnabledFor(logging.DEBUG):
                message += " savedResultsDict: " + pprint.pformat(self.savedResultsDict)
            log.exception(message)


    
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
                                Labels=value['Y']
                            else:
                                Network_output=value['Y']
                        except:
                            pass
                        
                    cType=self.getPlot(Network_output[-1])
                    if cType=="bar" or cType=="line" or cType=='scatter':
                        PvG = createDataObject([Network_output[-1], Labels[-1]], nameList=['Prediction', 'Ground Truth'])                        

                        # average over samples
                        network_average=np.average(Network_output,axis=0)
                        labels_average = np.average(Labels, axis=0)
                        APvG = createDataObject([network_average, labels_average], nameList=['Prediction', 'Ground Truth'])
                        
                        # PIE
                        acc_train=self.getStatistics({"layerId":layerId,"variable":"acc_train_iter","innervariable":""})
                        acc_val=self.getStatistics({"layerId":layerId,"variable":"acc_val_iter","innervariable":""})

                        if acc_val!=[]:
                            acc=acc_val
                        else:
                            acc=acc_train

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
                acc_train=self.getStatistics({"layerId":layerId,"variable":"acc_train_iter","innervariable":""})
                acc_val=self.getStatistics({"layerId":layerId,"variable":"acc_val_iter","innervariable":""})

                currentTraining=acc_train
                if isinstance(acc_train,np.ndarray):
                    currentValidation=np.concatenate((acc_train,np.asarray(acc_val)))
                elif isinstance(acc_train,list):
                    if isinstance(acc_val,list):
                        currentValidation=acc_train+acc_val
                    else:
                        currentValidation=acc_train+list(acc_val)
                
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"acc_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"acc_validation_epoch","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
                
            if view=="Loss":
                loss_train=self.getStatistics({"layerId":layerId,"variable":"loss_train_iter","innervariable":""})
                loss_val=self.getStatistics({"layerId":layerId,"variable":"loss_val_iter","innervariable":""})

                currentTraining=loss_train
                if isinstance(loss_train,np.ndarray):
                    currentValidation=np.concatenate((loss_train,np.asarray(loss_val)))
                elif isinstance(loss_train,list):
                    if isinstance(loss_val,list):
                        currentValidation=loss_train+loss_val
                    else:
                        currentValidation=loss_train+list(loss_val)

                totalTraining=self.getStatistics({"layerId":layerId,"variable":"loss_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"loss_validation_epoch","innervariable":""})

                dataObjectCurrent = createDataObject([currentValidation, currentTraining],
                                                     typeList=['line', 'line'],
                                                     nameList=['Validation', 'Training'])
            
                dataObjectTotal = createDataObject([totalValidation, totalTraining],
                                                   typeList=['line', 'line'],
                                                   nameList=['Validation', 'Training'])
                output = {"Current": dataObjectCurrent, "Total": dataObjectTotal}
                return output
            if view=="F1":
                f1_train=self.getStatistics({"layerId":layerId,"variable":"f1_train_iter","innervariable":""})
                f1_val=self.getStatistics({"layerId":layerId,"variable":"f1_val_iter","innervariable":""})

                currentTraining=f1_train
                if isinstance(f1_train,np.ndarray):
                    currentValidation=np.concatenate((f1_train,np.asarray(f1_val)))
                elif isinstance(f1_train,list):
                    if isinstance(f1_val,list):
                        currentValidation=f1_train+f1_val
                    else:
                        currentValidation=f1_train+list(f1_val)
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"f1_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"f1_validation_epoch","innervariable":""})



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
                auc_train=self.getStatistics({"layerId":layerId,"variable":"auc_train_iter","innervariable":""})
                auc_val=self.getStatistics({"layerId":layerId,"variable":"auc_val_iter","innervariable":""})

                currentTraining=auc_train
                if isinstance(auc_train,np.ndarray):
                    currentValidation=np.concatenate((auc_train,np.asarray(auc_val)))
                elif isinstance(auc_train,list):
                    if isinstance(auc_val,list):
                        currentValidation=auc_train+auc_val
                    else:
                        currentValidation=auc_train+list(auc_val)
                totalTraining=self.getStatistics({"layerId":layerId,"variable":"auc_training_epoch","innervariable":""})
                totalValidation=self.getStatistics({"layerId":layerId,"variable":"auc_validation_epoch","innervariable":""})


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
                
                prediction = createDataObject([prediction], typeList=['line'])
                
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
                current_reward = createDataObject([currentReward],
                                                typeList=['line'])
                total_reward = createDataObject([totalReward],
                                                typeList=['line'])
                obj = {"Current": current_reward, "Total": total_reward}
                return obj
            if view=="Loss":
                currentLoss=self.getStatistics({"layerId":layerId,"variable":"loss","innervariable":""})
                totalLoss=self.getStatistics({"layerId":layerId,"variable":"epochTrainLoss","innervariable":""})
                
                current_loss = createDataObject([currentLoss],
                                                typeList=['line'])
                total_loss = createDataObject([totalLoss],
                                               typeList=['line'])
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
                        log.debug("FieldError, only keys available are: "+str(list(self.resultDict[layerId][variable].keys()))+" |||| Expected: "+str(innervariable))
                        self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict[layerId][variable].keys()))+" |||| Expected: "+str(innervariable))
                    except:
                        try:
                            log.debug("FieldError, only keys available are: "+str(list(self.resultDict[layerId].keys()))+" |||| Expected: " + str(variable))
                            self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict[layerId].keys()))+" |||| Expected: " + str(variable))
                        except:
                            log.debug("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                            self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))

                    result=[]
            elif variable!="":
                try:
                    result=self.resultDict[layerId][variable]
                except:
                    try:
                        log.debug("FieldError, only keys available are: "+str(list(self.resultDict[layerId].keys()))+" |||| Expected: " + str(variable))
                        self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict[layerId].keys()))+" |||| Expected: " + str(variable))
                    except:
                        log.debug("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                        self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                    result=[]
            else:
                try:
                    result=self.resultDict[layerId]
                except:
                    log.debug("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                    self.warningQueue.put("FieldError, only keys available are: "+str(list(self.resultDict.keys()))+" |||| Expected: " + str(layerId))
                    result=[]
        else:
            log.debug("ResultDict is empty :'(")
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
