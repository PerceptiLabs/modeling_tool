from codehq import CodeHQ
from data import Data
from extractVariables import *

import numpy as np
import tensorflow as tf
import GPUtil

import pprint
import logging
log = logging.getLogger(__name__)

class NetworkBuilder():
    def buildNetwork(self,graphObj,jsonNetwork,randomSeed,keep_prob,checkpointDict,batch_size,warningQueue,errorQueue):
        FLAG_DISTRIBUTED=False
        version="CPU" # The version of Modelling Platform the user has
        # Check if multiple GPUs and use MirroredStrategy if that is the case
        GPUs = GPUtil.getGPUs()
        num_gpus=len(GPUs)
        if num_gpus>1 and version=="GPU":
            return self._buildNetworkDistributed(graphObj,jsonNetwork,randomSeed,keep_prob,checkpointDict,batch_size,warningQueue,errorQueue,FLAG_DISTRIBUTED,num_gpus)
        elif version=="MultipleMachines":
            # Set up TF_CONFIG and create MultiWorkerMirroredStrategy
            pass
        else:
            return self._buildNetwork(graphObj,jsonNetwork,randomSeed,keep_prob,checkpointDict,batch_size,warningQueue,errorQueue,FLAG_DISTRIBUTED)

    def _buildNetworkDistributed(self,graphObj,jsonNetwork,randomSeed,keep_prob,checkpointDict,batch_size,warningQueue,errorQueue,FLAG_DISTRIBUTED,num_gpus):
        # cross_device_ops = tf.contrib.distribute.AllReduceCrossDeviceOps('hierarchical_copy', num_packs=num_gpus)
        # strategy = tf.distribute.MirroredStrategy(cross_device_ops=cross_device_ops)
        strategy = tf.distribute.MirroredStrategy()
        global_batch_size = batch_size * strategy.num_replicas_in_sync
        with strategy.scope():
            # Either send in FLAG to _buildNetwork or copy paste in here and edit
            return self._buildNetwork(graphObj,jsonNetwork,randomSeed,keep_prob,batch_size,warningQueue,errorQueue,FLAG_DISTRIBUTED)

    def _buildNetwork(self,graphObj,jsonNetwork,randomSeed,keep_prob,checkpointDict,batch_size,warningQueue,errorQueue,FLAG_DISTRIBUTED):
        FLAG_REINFORCE = False
        graph=graphObj.graphs   #graph has structure [id]->[id for id in backward_connections]
        end_points=graphObj.end_points

        #Incase we have loaded a network
        # checkpointDict={}
        # for Id in list(graph.keys()):
        #     content=graph[Id]['Info']
        #     if "checkpoint" in content and content["checkpoint"]!=[] and content["checkpoint"][-1] not in list(checkpointDict.keys()):
        #         # checkpointDict[content["checkpoint"][-1]]=extractCheckpointInfo(*content["checkpoint"])
        #         checkpointDict[content["checkpoint"][-1]]=extractCheckpointInfo(*content["checkpoint"]).getAllVariables()
        # if checkpointDict:
        #     tf.reset_default_graph()

        safe_list = ['math','tf','np','KMeans','DBSCAN','KNeighborsClassifier','KNeighborsRegressor','RandomForestClassifier','RandomForestRegressor','OneClassSVM','NuSVC','NuSVR']
        safe_dict=dict()
        for k in safe_list:
            safe_dict[k]=globals().get(k,None)

        safe_dict['abs'] = abs
        safe_dict['list']=list
        # safe_dict['print']=print
        safe_dict['keep_prob']=keep_prob

        ###########################################################################################################
        #Accessable to the users through layer code:
        #X contains the output (Y) of the previous layer, if there is more than 1 output then X becomes a dict
        #  where the output of each layer can be accessed by either the layer's name or their id (X["FC_1"] for example). 
        #Xvariables contains all the variables in the previous layers, use if you want to access their weights or bias etc.
        #  As with X, if there are more than 1 previous layer's, Xvariables represent them in a dict format.
        #  Xvariables is a dict, so to access any of the variables just write ex. Xvariables["W"].

        #Accessable to the backend:
        #outputDict and outputVariables mirrors X and Xvariables where one contains the output only and the other contains
        #  every variable in the layer. You access the layer through id, ex. outputVariables[5] will give you all variables which exists
        #  in layer with id 5.
        ###########################################################################################################

        outputDict=dict()
        outputVariables=dict()
        origionalSafeDict=safe_dict.copy()
        # print(safe_dict)
        # exec("print(keep_prob)",{"__builtins__":None},safe_dict)
        # error
        codeHQ=CodeHQ()
        for Id in list(graph.keys()):
            content=graph[Id]['Info']
            log.info("Building network component of type {} with id {}".format(content["Type"], Id))

            #Check how many inputs the layer has and take input values from previous layers
            if len(graph[Id]['Con'])>1:
                X=dict()
                for i in graph[Id]['Con']:
                    X.update(dict.fromkeys([i, graph[i]['Info']["Name"]],outputVariables[i]))
                    # Xvariables.update(dict.fromkeys([i, graph[i]['Info']["Name"]],outputVariables[i]))
            elif len(graph[Id]['Con'])==1:
                X=outputVariables[graph[Id]['Con'][0]]
                # Xvariables=outputVariables[graph[Id]['Con'][0]]

            #Check so it has previous layers (X exists)
            if "X" in locals():
                safe_dict["X"]=X

            # if "Xvariables" in locals():
            #     safe_dict["Xvariables"]=Xvariables

            if content["Type"]=="DataData":
                #Create a data object and put as a refence into content["code"]["data"]?
                #We can then easily call .getData and have a reference to the placeholder from the object for the session.
                # try:
                content['Properties']['accessProperties']['Seed']=randomSeed
                content["Data"]=Data(content["Properties"],jsonNetwork["Hyperparameters"])
                # except:
                #     errorQueue.put("The data was not read correctly, did you enter the correct data path?")
                #     print("The data was not read correctly, did you enter the correct data path?")
                #     return
                placeholder=content["Data"].placeholder 
                outputDict[Id]=placeholder
                outputVariables[Id]={"Y":placeholder}
                
            elif content["Type"]=="DataEnvironment":
                if "Batch_size" not in content["Properties"]["accessProperties"]:
                    content["Properties"]["accessProperties"]["Batch_size"]=10 #TODO: REMOVE
                dataObj=Data(content["Properties"],jsonNetwork["Hyperparameters"])
                content["Data"]=dataObj
                placeholder=content["Data"].placeholder 
                outputDict[Id]=placeholder
                outputVariables[Id]={"Y":placeholder}

            elif content["Type"]=="TrainNormal":
                try:
                    try:
                        if type(content["Code"]) is str:
                            codeString=content["Code"]
                        else:
                            lossString=content["Code"]["Loss"]
                            optString=content["Code"]["Optimizer"]
                            accString=content["Code"]["Accuracy"]
                            codeString=lossString+"\n"+optString+"\n"+accString
                    except:
                        codeString=codeHQ.get_code(content['Type'],content['Properties'],X)

                    self._exec(codeString, safe_dict)
                    #exec(codeString,{"__builtins__":None},safe_dict)
                    # print(safe_dict["Y"])
                    outputDict[Id]=safe_dict["Y"]       #The variables run in exec are not added to local() but to the safe_dict
                    safe_dict.pop("X", None)

                    if len(graph[Id]['Con'])>1:
                        X=dict()
                        for i in graph[Id]['Con']:
                            X.update(dict.fromkeys([i, graph[i]['Info']["Name"]],outputDict[i]))
                    elif len(graph[Id]['Con'])==1:
                        X=outputDict[graph[Id]['Con'][0]]
                    safe_dict["X"]=X

                    outputVariables[Id]={ k : safe_dict[k] for k in set(safe_dict) - set(origionalSafeDict) }
                    safe_dict=origionalSafeDict.copy()
                    
                except Exception as e:
                    errorQueue.put("Got a crash in component \"" + graph[Id]["Info"]["Name"] + "\" when trying to build the Network.")
                    raise Exception(str(e))

            elif content["Type"]=="TrainReinforce":
                FLAG_REINFORCE=True
                # Make sure that we can reach input, worker_output and original_output in the agent Class
                workerDict={"Input":[],"Output":[],"Output_id":[],"Output_org":[],"Copy_id":graphObj.copykeys}
                for con in graph[Id]['Con']:
                    if graph[con]['Copy']:
                        workerDict["Input"].append(outputDict[graph[con]['Input_ref'][0]])
                        workerDict["Output"].append(outputDict[con])
                        workerDict["Output_id"].append(con)
                        workerDict["Output_org"].append(outputDict[graph[con]['CopyOf']])
                # Create input placeholders and other necessary placeholder(s), e.g. for actions, target, advatanges, rewards
                content["Data"]=dataObj
                content["Data"].source_obj.setAgent(content['Properties']['ReinforceType'], content['Properties'], safe_dict, workerDict, outputVariables, graph) #replace content['Properties'] with actionString
                placeholders=content["Data"].reinforcePlaceholders()
                outputDict[Id]=placeholders




                # If we only have 1 layer, it's not a dictionary. In that case, create a dictionary to add placeholders in it
                if type(X)!=dict:
                    X={str(con):X,str(graph[con]['Info']['Name']):X}
                    safe_dict["X"]=X
                for key,value in placeholders.items():
                    X[key]=value
                content['Properties']['Placeholders']=placeholders
                content['Properties']['Worker_outputs']=workerDict["Output_id"]
                codeString,actionString=codeHQ.get_code(content['Type'],content['Properties'],X)
                actionString=actionString.lower()
                self._exec(codeString, safe_dict)
                

                
                #exec(codeString,{"__builtins__":None},safe_dict)
                """
                safe_dict.pop("X", None)

                if len(graph[Id]['Con'])>1:
                    X=dict()
                    for i in graph[Id]['Con']:
                        X.update(dict.fromkeys([i, graph[i]['Info']["Name"]],outputDict[i]))
                elif len(graph[Id]['Con'])==1:
                    X=outputDict[graph[Id]['Con'][0]]
                """

                for i in graph[Id]['Con']:
                    X.update(dict.fromkeys([i, graph[i]['Info']["Name"]],outputDict[i]))
                
                safe_dict["X"]=X
                outputVariables[Id]={ k : safe_dict[k] for k in set(safe_dict) - set(origionalSafeDict) }

                
                safe_dict=origionalSafeDict.copy()
            else:
                # try:
                if "checkpoint" in content and content["checkpoint"]:
                    valueDict=checkpointDict[content["checkpoint"][-1]]
                    codeString=content["Code"]["Output"]
                    codeRows=re.split(';|\n',codeString)
                    codeRows=list(filter(None,codeRows))
                    safe_dict["valueDict"]=valueDict
                    content["Code"]["Output"]=""
                    for row in codeRows:
                        if "loc:@" in row:
                            splitRow=row.split("=")
                            new_row=splitRow[0]+"=valueDict['"+ splitRow[1].replace("loc:@","").replace("'","") +"']\n"
                            content["Code"]["Output"]+=new_row
                        else:
                            content["Code"]["Output"]+=row+"\n" 

                if content["Code"]["Output"]!="":
                    codeString=content["Code"]["Output"]
                else:
                    codeString=codeHQ.get_code(content['Type'],content['Properties'],X)

                self._exec(codeString, safe_dict)
                #exec(codeString,{"__builtins__":None},safe_dict)
                
                outputDict[Id]=safe_dict["Y"]       #The variables run in exec are not added to local() but to the safe_dict
                safe_dict.pop("X", None)
                safe_dict.pop("valueDict", None)

                if len(graph[Id]['Con'])>1:
                    X=dict()
                    for i in graph[Id]['Con']:
                        X.update(dict.fromkeys([i, graph[i]['Info']["Name"]],outputDict[i]))
                elif len(graph[Id]['Con'])==1:
                    X=outputDict[graph[Id]['Con'][0]]
                safe_dict["X"]=X

                outputVariables[Id]={ k : safe_dict[k] for k in set(safe_dict) - set(origionalSafeDict) }
                safe_dict=origionalSafeDict.copy()


        if log.isEnabledFor(logging.DEBUG):                
            log.debug("_buildNetwork outputDict: " + pprint.pformat(outputDict))
            log.debug("_buildNetwork outputVariables: " + pprint.pformat(outputVariables))        
        
        return outputDict, outputVariables, FLAG_REINFORCE


    def _exec(self, code_string, safe_dict):

        debug_string = "Executing code:\n" + \
                       "===============\n" + \
                       "{}\n" \
                       "===============".format(code_string)
        log.debug(debug_string)


        try:
            exec(code_string, {"__builtins__":None}, safe_dict)
        except:
            log.exception("Error when calling exec in NetworkBuilder")
            raise
