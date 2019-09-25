from codehq import CodeHQ

import numpy as np
import tensorflow as tf
from tensorflow.python.eager.context import context, EAGER_MODE, GRAPH_MODE

import math
from lw_graph import Graph
from extractVariables import *
from createDataObject import createDataObject

import sys
import traceback
import time
import copy
import queue
import random
import ast

# from sklearn.cluster import KMeans, DBSCAN
# from sklearn.neighbors import KNeighborsClassifier,KNeighborsRegressor
# from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
# from sklearn.svm import OneClassSVM,NuSVC,NuSVR

class lwNetwork():
    def __init__(self,dataDict,variablesDict,jsonNetwork):
        self.outputDim=None
        self.inputDim=None
        self.previewLayer=None
        self.propegateOutputs(dataDict,variablesDict,jsonNetwork)

    def propegateOutputs(self,dataDict,variablesDict,jsonNetwork):
        self.jsonNetwork=jsonNetwork

        def switch_to(mode):
            #Hack to turn eager mode on and off so it does not affect the computational core (since eager mode is global) (can be a problem if running when core already is started?)
            ctx = context()._eager_context
            ctx.mode = mode
            ctx.is_eager = mode == EAGER_MODE
        
        print("Started calculations")
        # try:
        # try:
        graphObj=Graph(jsonNetwork)
        # except Exception as e:
        #     print(traceback.format_exc())
        #     print("The graph did not correctly build, check so that forward and backward connections are correct")
        #     # logQueue.put("The graph did not correctly build, check so that forward and backward connections are correct")
        #     switch_to(GRAPH_MODE)
        #     return ""

        graph=graphObj.graphs            

        tf.reset_default_graph()

        switch_to(EAGER_MODE)
        safe_list = ['math','tf','np','KMeans','DBSCAN','KNeighborsClassifier','KNeighborsRegressor','RandomForestClassifier','RandomForestRegressor','OneClassSVM','NuSVC','NuSVR']
        safe_dict=dict()
        for k in safe_list:
            safe_dict[k]=globals().get(k,None)

        safe_dict['abs'] = abs
        safe_dict['list'] = list
        safe_dict['keep_prob']=1
        # safe_dict['print']=print

        outputDict=dict()
        outputVariables=dict()
        origionalSafeDict=safe_dict.copy()

        ErrorDict=dict()
        ErrorRowDict=dict()

        codeHQ=CodeHQ()
        for Id in list(graph.keys()):
            content=graph[Id]['Info']
            ErrorDict[Id]=""
            ErrorRowDict[Id]=""

            if len(graph[Id]['Con'])>1:
                X=dict()
                for i in graph[Id]['Con']:
                    X.update(dict.fromkeys([i, graph[i]['Info']["Name"]],outputVariables[i]))
                    # Xvariables.update(dict.fromkeys([i, graph[i]['Info']["Name"]],outputVariables[i]))
            elif len(graph[Id]['Con'])==1:
                X=outputVariables[graph[Id]['Con'][0]]
                # Xvariables=outputVariables[graph[Id]['Con'][0]]

            if "X" in locals():
                safe_dict["X"]=X

            # if "Xvariables" in locals():
            #     safe_dict["Xvariables"]=Xvariables

            if content["Type"]=="DataData":
                if Id in dataDict:
                    safe_dict=dataDict[Id].executeCode(globals_=safe_dict)
                    data=dataDict[Id].sample
                    try:
                        if np.shape(data)[0]!=1:
                            data=np.reshape(data, [1,*np.shape(data)])
                    except:
                        pass
                    data=np.array(data,dtype=np.float32)

                    outputDict[Id]=data
                    safe_dict.pop("X", None)
                    outputVariables[Id]={ k : safe_dict[k] for k in set(safe_dict) - set(origionalSafeDict) }
                    outputVariables[Id]["Y"]=data
                    safe_dict=origionalSafeDict.copy()
                    # outputDict[Id]=data
                    # outputVariables[Id]={"Y":data}
                # elif "checkpoint" in content and content["checkpoint"] and content["OutputDim"]!="":
                elif "checkpoint" in content and content["checkpoint"]!=[]:
                    #If the component is loaded from a pre-trained network
                    data=""

                    outDim=ast.literal_eval("["+content["OutputDim"].replace("x",",").replace("None","1")+"]")
                    
                    data=np.zeros(outDim)
                    try:
                        if np.shape(data)[0]!=1:
                            data=np.reshape(data, [1,*np.shape(data)])
                    except:
                        pass
                    data=np.array(data,dtype=np.float32)
                    outputDict[Id]=data
                    outputVariables[Id]={"Y":data}
                else:
                    # :'(
                    outputDict[Id]=""
                    outputVariables[Id]=""
                
                # try:
                #     # if Id not in dataDict:
                #     #     dataH=DataHandlerLW(graph[Id]['Info']["Properties"]["accessProperties"])
                #     #     dataDict[Id]=dataH
                #     data=dataDict[Id].sample
                #     try:
                #         if np.shape(data)[0]!=1:
                #             data=np.reshape(data, [1,*np.shape(data)])
                #     except:
                #         pass
                #     data=np.array(data,dtype=np.float32)
                #     outputDict[Id]=outputVariables[Id]=data
                # except:
                #     outputDict[Id]=""
                #     outputVariables[Id]=""

                # outputDict[Id]=content["Properties"]["Data"]
                # outputVariables[Id]=content["Properties"]["Data"]

            elif content["Type"]=="DataEnvironment":
                try:
                    data=dataDict[Id].sample
                    try:
                        if np.shape(data)[0]!=1:
                            data=np.reshape(data, [1,*np.shape(data)])
                    except:
                        pass
                    data=np.array(data,dtype=np.float32)
                    outputDict[Id]=data
                    outputVariables[Id]={"Y":data}
                except:
                    outputDict[Id]=""
                    outputVariables[Id]=""

            elif content["Type"]=="TrainNormal":
                try:
                    if "" in list(X.values()):
                        outputDict[Id]=""
                    else:
                        outputDict[Id]=""
                except:
                    outputDict[Id]=""
                    
            elif content["Type"]=="TrainReinforce":
                outputDict[Id]=""

            else:
                try:
                    if "checkpoint" in content and content["checkpoint"]:
                        valueDict=variablesDict[content["checkpoint"][-1]]
                        codeString=content["Code"]
                        if type(codeString) is dict:
                            codeString="\n".join(list(codeString.values()))
                        codeRows=re.split(';|\n',codeString)
                        codeRows=list(filter(None,codeRows))
                        print("CodeRows: ", codeRows)
                        safe_dict["valueDict"]=valueDict
                        content["Code"]=""
                        for row in codeRows:
                            if "loc:@" in row:
                                splitRow=row.split("=")
                                new_row=splitRow[0]+"=valueDict['"+ splitRow[1].replace("loc:@","").replace("'","") +"']\n"
                                content["Code"]+=new_row
                            else:
                                content["Code"]+=row+"\n"   
                    try:
                        codeString=content["Code"]
                        if type(codeString) is dict:
                            codeString="\n".join(list(codeString.values()))
                    except:
                        codeString=codeHQ.get_code(content['Type'],content['Properties'],X)

                    try:
                        exec(codeString,safe_dict)    #,{"__builtins__":None},safe_dict

                    except SyntaxError as e:
                        print(traceback.format_exc())
                        error_class = e.__class__.__name__
                        detail = e.args[0]
                        tbObj=traceback.TracebackException(*sys.exc_info())

                        ErrorDict[Id]="".join(tbObj.format_exception_only())
                        ErrorRowDict[Id]=tbObj.lineno or "?"
                    
                        outputDict[Id]=""
                        safe_dict.pop("X", None)
                        outputVariables[Id]={ k : safe_dict[k] for k in set(safe_dict) - set(origionalSafeDict) }
                        safe_dict=origionalSafeDict.copy()    

                    except Exception as e:
                        print(traceback.format_exc())
                        tbObj=traceback.TracebackException(*sys.exc_info())
                        
                        error_class = e.__class__.__name__
                        detail = e
                        cl, exc, tb = sys.exc_info()
                        tb_list=traceback.extract_tb(tb)
                        line_number=""
                        for i in tb_list:
                            if i[2]=="<module>":
                                line_number=i[1]

                        if line_number=="":
                            line_number = tb.tb_lineno
                        
                        ErrorDict[Id]="%s at line %d: %s" % (error_class, line_number, detail)
                        ErrorRowDict[Id]=line_number

                        outputDict[Id]=""
                        safe_dict.pop("X", None)
                        outputVariables[Id]={ k : safe_dict[k] for k in set(safe_dict) - set(origionalSafeDict) }
                        safe_dict=origionalSafeDict.copy()         
       
                    else:
                        outputDict[Id]=safe_dict["Y"]
                        safe_dict.pop("X", None)
                        outputVariables[Id]={ k : safe_dict[k] for k in set(safe_dict) - set(origionalSafeDict) }
                        safe_dict=origionalSafeDict.copy()

                except Exception as e:
                    print(traceback.format_exc())
                    outputDict[Id]=""
                    safe_dict.pop("X", None)
                    outputVariables[Id]={ k : safe_dict[k] for k in set(safe_dict) - set(origionalSafeDict) }
                    safe_dict=origionalSafeDict.copy()
                # else:
                #     safe_dict.pop("Xvariables", None)
                #     outputVariables[Id]={ k : safe_dict[k] for k in set(safe_dict) - set(origionalSafeDict) }
                #     safe_dict=origionalSafeDict.copy()
        
        dimDict=dict()
        returnDict=dict()
        returnDict["InputDim"]=dict()
        returnDict["OutputDim"]=dict()
        returnDict["Preview"]=dict()
        for (Id,value) in outputDict.items():
            OutputDim=[]
            if value is "":
                OutputDim=value
            else:
                if type(value).__name__=="EagerTensor" or type(value).__name__=="Tensor":
                    OutputDim=value.get_shape().as_list()
                    print("EAGER")
                    if not OutputDim:
                        OutputDim=[1]
                elif not np.shape(value):
                    OutputDim=[1]
                # elif  type(value).__name__=="int" or type(value).__name__=="float":
                #     OutputDim=[1]
                else:
                    OutputDim=np.shape(value)
                    print("NP")

                if len(OutputDim)>1:
                    OutputDim=list(OutputDim[1:])
                else:
                    OutputDim=list(OutputDim)
            if len(np.shape(outputDict[Id]))>1:
                returnDict["Preview"][Id]=np.squeeze(outputDict[Id])
            else:
                returnDict["Preview"][Id]=outputDict[Id]

            dimDict[Id]=OutputDim
            #Having returnDict here works as long as dimDict contains all values returnDict needs. Might not work if graph is recursive
            # returnDict[Id]={"InputDim":str(dimDict[graph[Id]['Con'][0]]) if len(graph[Id]['Con'])==1 else str([dimDict[i] for i in graph[Id]['Con']]).replace("'",""),"OutputDim":str(dimDict[Id])}
            # # returnDict[Id]["InputDim"].replace("[","").replace("]","").replace(",","x")
            # returnDict[Id]["OutputDim"]=returnDict[Id]["OutputDim"].replace("[","").replace("]","").replace(", ","x")
            print("ErrorDict: ",ErrorDict)
            print("ErrorRowDict: ",ErrorRowDict)
            returnDict["InputDim"][Id]=str(dimDict[graph[Id]['Con'][0]]) if len(graph[Id]['Con'])==1 else str([dimDict[i] for i in graph[Id]['Con']]).replace("'","")
            # returnDict[Id]["InputDim"].replace("[","").replace("]","").replace(",","x")
            # returnDict["OutputDim"][Id]=str(dimDict[Id]).replace("[","").replace("]","").replace(", ","x")
            returnDict["OutputDim"][Id]={"Dim":str(dimDict[Id]).replace("[","").replace("]","").replace(", ","x"),"Error":{"Message":ErrorDict[Id],"Row":ErrorRowDict[Id]} if ErrorDict[Id]!="" else None}
            

        self.inputDim=returnDict["InputDim"]
        self.outputDim=returnDict["OutputDim"]
        self.previewLayer=returnDict["Preview"]

        print("InputDims: ", returnDict["InputDim"])
        print("OutputDims: ",returnDict["OutputDim"])
        print("predictDict ", returnDict["Preview"])
        print("ErrorDict: ",ErrorDict)
        print("ErrorRowDict: ",ErrorRowDict)
        # for (Id,value) in dimDict.items():
        #     # outputDict[Id]={"InputDim":dimDict[graph[Id]['Con'][0]] if len(graph[Id]['Con'])==1 else str([dimDict[i] for i in graph[Id]['Con']]),"OutputDim":str(dimDict[Id])}
        #     returnDict[Id]={"InputDim":dimDict[graph[Id]['Con'][0]] if len(graph[Id]['Con'])==1 else str([dimDict[i] for i in graph[Id]['Con']]).replace("'",""),"OutputDim":str(dimDict[Id])}
        switch_to(GRAPH_MODE)
        # return returnDict
        # except  Exception as e:
        #     print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        #     print(e)
        #     switch_to(GRAPH_MODE)
        #     emptyKeyList={}
        #     try:
        #         for key in list(jsonNetwork.keys()):
        #             emptyKeyList[key]=""
        #     except  Exception as e:
        #         print(e)
        #     self.inputDim=self.outputDim=emptyKeyList
            # return {"InputDim":emptyKeyList,"OutputDims":emptyKeyList}




            # except SyntaxError as e:
                        #     error_class = e.__class__.__name__
                        #     detail = e.args[0]
                        #     line_number = e.lineno
                        #     print("%s at line %d in layer %s: %s" % (error_class, line_number, str(content["Name"]), detail))
                        # except Exception as e:
                        #     error_class = e.__class__.__name__
                        #     try:
                        #         detail = e.args[0]
                        #     except:
                        #         detail=e
                        #     cl, exc, tb = sys.exc_info()
                        #     line_number = traceback.extract_tb(tb)[-1][1]
                        #     print("%s at line %d in layer %s: %s" % (error_class, line_number, str(content["Name"]), detail))
