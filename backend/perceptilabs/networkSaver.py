import re
import json

from perceptilabs.functionParser import explain
from perceptilabs.codehq import CodeHqNew as CodeHq

def getVariableLibrary(variable):
    try:
        if variable.op.type in ["Variable","VariableV2"]:
            return "tf"
    except:
        return None
    return None

def createReferenceString(variable):
    """
        Creates a reference string from a variable, returns either a reference if possible or the real value of the variable.
    """
    lib=getVariableLibrary(variable)
    
    if lib=="tf":
        return "'loc:@"+str(variable.name).split(":")[0]+"'"

def splitStrings(codeString):
    splitString=re.split(';|\n',codeString)
    splitString=list(filter(None,splitString))
    return splitString

def isAssign(string):
    try:
        parsedCode=explain(string)
        return parsedCode[0]=="Assign"
    except Exception as e:
        print(e)
        return False

def createNewLayerCode(id_,layer,variables):
    # if "Code" not in layer["Info"]:
    #     return ""
    if "Code" in layer["Info"] and layer["Info"]["Code"]:
        tabs=layer["Info"]["Code"]
    else:
        Type=layer["Info"]["Type"]
        Properties=layer["Info"]["Properties"]
        Con=layer['Con']
        backward_connections = layer["Info"]['backward_connections']
        content={"Info":{"Type":Type, "Id": id_, "Properties": Properties, "backward_connections": backward_connections}, "Con":Con}
        tabs=CodeHq.get_code_generator(id_,content).get_code()
        if type(tabs) is not dict:
            tabs={"Output":tabs} 

    newCodeTabs=dict()

    for tab,code in tabs.items():
        newCode=""
        relevantCodeList=splitStrings(code)
        for string in relevantCodeList:
            if isAssign(string):
                if "loc:@" in string:
                    continue
                variableName=string.split("=")[0].replace(" ","")
                if variableName in variables and getVariableLibrary(variables[variableName]) is not None:
                    variable=variables[variableName]
                    newCode+=variableName+"="+createReferenceString(variable)+"\n"
                    newCode+=variableName+"="+"tf.Variable("+variableName+")"+"\n"
                else:
                    newCode+=string+"\n"
            else:
                newCode+=string+"\n"
        newCodeTabs[tab]=newCode  
    return newCodeTabs

def createNetwork(graph_variables,graphObj,frontendNetwork,checkpoint):
    graph=graphObj.graphs
    frontendLayers=frontendNetwork["networkElementList"].copy()
    for Id, layer in graph.items():
        newCode=createNewLayerCode(Id,layer,graph_variables[Id])
        frontendLayers[Id]["layerCode"]=newCode
        frontendLayers[Id]["checkpoint"]=checkpoint

    frontendNetwork["networkElementList"]=frontendLayers

    return frontendNetwork
    

def saveNetwork(path,graph_variables,graphObj,frontendNetwork,checkpoint):
    json_network=createNetwork(graph_variables,graphObj,frontendNetwork,checkpoint)
    print(json_network)
    with open(path, 'w') as json_file:
        json.dump(json_network, json_file)



if __name__ == "__main__":
    import tensorflow as tf
    import numpy as np
    safe_dict=dict()
    safe_list = ['math','tf','np','KMeans','DBSCAN','KNeighborsClassifier','KNeighborsRegressor','RandomForestClassifier','RandomForestRegressor','OneClassSVM','NuSVC','NuSVR']
    for k in safe_list:
        safe_dict[k]=globals().get(k,None)
    codeString="shape = [3,3,1,8];initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(3**2 * 8)));W  = tf.Variable(initial);"
    exec(codeString,safe_dict)
    variables={
        "initial":safe_dict["initial"],
        "W":safe_dict["W"],
        "shape":safe_dict["shape"]
    }
    print(variables)
    layer={"Info":{"Code":{"Output":codeString}}}
    newCode=createNewLayerCode(layer, variables)
    print(newCode)
    print(getVariableLibrary(variables["W"]))

    relevantCodeList=splitStrings(codeString)
    print(relevantCodeList)
    print(isAssign(relevantCodeList[-1]))
