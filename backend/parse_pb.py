import tensorflow as tf
import numpy as np
import random
# import copy
import re
import os
import copy
from tensorflow.python.platform import gfile
from google.protobuf import text_format
# from tensorflow.python.tools import inspect_checkpoint as chkp
# from tensorflow.python import pywrap_tensorflow
# from tensorflow.python.framework import importer
# from tensorflow.core.protobuf import saver_pb2
# from tensorflow.python.training import saver as saver_lib
from tensorflow.python.saved_model import tag_constants
from extractVariables import *
from functionParser import explain
from lw_graph import Graph
from functools import reduce
import operator
import collections
import funclib


def parseAttribute(attr):
   """Takes a protobuf attribute and returns it in a format usable by Python.
   Arguments: 
      attr: A protobuf attribute.
   Returns:
      A Python variable or tf format.
   """
   if type(attr).__name__ in ["bytes","int64","float","bool","DataType","str","int"]:
      try:
         attr=attr.decode()
      except:
         pass
      return attr

   elif type(attr).__name__=="list" or "Repeated" in type(attr).__name__:
      attrList=[]
      for a in attr:
         attrList.append(parseAttribute(a))
      return attrList

   elif type(attr).__name__=="AttrValue":
      for value in [attr.s, attr.i, attr.f]:
         if value:
            return parseAttribute(value)
      for value in [attr.shape, attr.tensor, attr.func]:
         if value.ByteSize()!=0:
            return parseAttribute(value)
      if attr.type:
         if "DT_FLOAT" in str(attr):
            return tf.float32
         if "DT_INT32" in str(attr):
            return tf.int32
         if "DT_DOUBLE" in str(attr):
            return tf.float64

      if attr.list.ByteSize()!=0:
         return parseAttribute(attr.list)
      #If it's nothing else, then assume it is boolean   
      return parseAttribute(attr.b) 

   elif type(attr).__name__=="ListValue":
      for value in [attr.s, attr.i, attr.f, attr.b, attr.type]:
         if value:
            return parseAttribute(value)
      for value in [attr.shape, attr.tensor, attr.func]:
         if value.ByteSize()!=0:
            return parseAttribute(value)

   elif type(attr).__name__=="TensorShapeProto":
      return parseAttribute(attr.dim)

   elif type(attr).__name__=="TensorProto":
      print(attr)
      raise Exception("Found a TensorProto, logic not yet implemented")

   elif "Dim" in type(attr).__name__:
      for value in [attr.size, attr.name]:
         if not value:
            pass
         else:
            return parseAttribute(value)

def cleanTensorName(name):
   return name.split(":")[0]

def getPreviousOperation(currentLayer,name_graph_def,operations):
   if currentLayer.name in operations:
      return currentLayer
   else:
      for i in currentLayer.input:
         if "^" not in i:
            return getPreviousOperation(name_graph_def[cleanTensorName(i)],name_graph_def,operations)

def getConstants(currentLayer,name_graph_def,operations):
   if isValidConstant(operation.op):
      return currentLayer
   else:
      for i in currentLayer.input:
         if "^" not in i:
            return getConstants(name_graph_def[cleanTensorName(i)],name_graph_def,operations)

def opHasMultipleOutputs(operationName):
   if operationName=="FusedBatchNorm":
      return True
   if operationName=="Switch":
      return True
   if operationName=="Merge":
      return True
   
   return False

def getPreviousComponent(currentLayerName,name_graph_def):
   """Returns the previous constant or operation with a tag specifying it's type.
   Return: (protobuf Layer, string Identifier, string OutputTag)
   The Identifier can either be "Operation", "Constant" or "NotFound".
   The OutputTag returns a string to fetch the correct output from the operation (ex: "[1]").
   """
   currentLayer=name_graph_def[cleanTensorName(currentLayerName)]
   splitName=currentLayerName.split(":")
   if len(splitName)>1:
      OutputTag="["+splitName[1]+"]"
   else:
      if opHasMultipleOutputs(currentLayer.op):
         OutputTag="[0]"
      else:
         OutputTag=""

   if isValidOperation(currentLayer.op):
      return (currentLayer,"Operation",OutputTag)
   elif isValidConstant(currentLayer.op):
      return (currentLayer,"Constant",OutputTag)
   else:
      for i in currentLayer.input:
         if "^" not in i:
            return getPreviousComponent(i,name_graph_def)
   return (None, "NotFound","")


nonValidOp=[]
def isValidOperation(operation):
   accepted_operations=list(funclib.OpNameDict.keys())
   # accepted_operations=["BatchNorm","Conv","reshape","dropout","pool","placeholder","relu","add","sub","mul","softmax","biasadd","squeeze","shape"] #, "Identity"
   # accepted_operations=["BatchNorm","Logistic","Relu","Relu6","ReluN1To1","Tanh","Add","Maximum","Minimum","Mul","Sub","AveragePool2d","Concatenation","Conv2d","DepthwiseConv2d","FullyConnected","L2Normalization","MaxPool2d","Mean",
   #               "Pad","Reshape","ResizeBilinear","ResizeNearestNeighbor","Slice","Softmax","SpaceToDepth","Split","Squeeze","StridedSlice","Placeholder"]
   if any(op.lower() == operation.lower() for op in accepted_operations):
      return True
   else:
      if operation not in nonValidOp:
         nonValidOp.append(operation)  #Just for debugging
      return False

def isValidConstant(operation):
   accepted_operations=list(funclib.ConstantNameDict.keys())
   if any(op.lower() == operation.lower() for op in accepted_operations):
      return True
   else:
      return False

def getNameSpace(operation,name_spaces):
   names=cleanTensorName(operation.name).split("/")
   current_name_space=names[0]
   current_path=name_spaces
   if type(current_path) is dict and names[0] in current_path and type(current_path[names[0]]) is dict:
      current_path=current_path[names[0]]
   for name in names[1:]:
      if type(current_path) is dict and name in current_path and type(current_path[name]) is dict:
         current_path=current_path[name]
         current_name_space=current_name_space+"/"+name
      else:
         break   
   return current_name_space

def getSameNamespace(operation1,operation2,name_spaces):
   pass

def inSameNameSpace(operation1,operation2,name_spaces):
   if type(operation1).__name__!="NodeDef" or type(operation2).__name__!="NodeDef":
      return False
   if getNameSpace(operation1,name_spaces)==getNameSpace(operation2,name_spaces):
      return True
   else:
      return False

def _has_no_variables(sess):
   for op in sess.graph.get_operations():
      if op.type.startswith("Variable") or op.type.endswith("VariableOp"):
         return False
   return True

def parsedAttrHandler(parsed):
   if type(parsed).__name__=="str":
      return "'"+str(parsed)+"'"
   elif type(parsed).__name__=="DType":
      return "tf."+parsed.name
   else:
      return str(parsed)

def augmentParsedAttr(operation, argument, parsed):
   if operation == "Placeholder" and argument == "shape":
      for i in range(len(parsed)):
         if parsed[i]==-1:
            parsed[i]=None
   return parsed

def findComponentName(layer):
   # ProcessOneHot,ProcessCrop,ProcessReshape,,ProcessEmbed,ProcessGrayscale,DeepLearningFC,DeepLearningConv,DeepLearningDeconv,DeepLearningRecurrent,MathArgmax,
   # MathSoftmax,MathSplit,MathMerge,PointWise,TrainNormal,TrainReinforce,ClassicMLKMeans,ClassicMLDbscans,ClassicMLKNN,ClassicMLRandomForest,ClassicMLSVM

   #Check first for high Prio types and then for Low prio types and lastly custom. Search backwards
   highPrio={
      "DeepLearningConv":["conv"],
      "DeepLearningDeconv":["deconv"],
      "DeepLearningFC":["fully_connected"],  #Need a better way to find fully connected layers since they can be manually built or with function
      "DataData":["placeholder"],
   }
   lowPrio={
      "MathSoftmax":["softmax"],
      "ProcessReshape":["reshape"],
      "MathMerge":["add", "subtract", "multiply", "concat"],
   }
   for highPrioName, searchPhrases in highPrio.items():
      if any([searchPhrase in layer.lower() for searchPhrase in searchPhrases]):
         return highPrioName
   for lowPrioName, searchPhrases in lowPrio.items():
      if any([searchPhrase in layer.lower() for searchPhrase in searchPhrases]):
         return lowPrioName
   return "ProcessEmbed"

def getGraphDef(graph_def_path):
   print(graph_def_path)
   type_pb=graph_def_path.split(".")[-1]=="pb"
   graph_def = tf.GraphDef()
   mode = "rb" if type_pb else "r"
   with gfile.GFile(graph_def_path, mode) as f:
      if type_pb:
         graph_def.ParseFromString(f.read())
      else:
         text_format.Merge(f.read(), graph_def)
   return graph_def

   # with open(graph_def_path) as f:
   #    txt = f.read()

   # graph_def = text_format.Parse(txt, tf.GraphDef())
   # return graph_def


   # graph2 = tf.Graph()
   # with graph2.as_default():
   #    with tf.Session(graph=graph2) as sess:
   #          # Restore saved values
   #          tf.saved_model.loader.load(
   #             sess,
   #             [tag_constants.SERVING],
   #             graph_def_path
   #          )
   # return graph2.as_graph_def()
   

def getLayerType(componentName):
   #Can be Data, Other, Train or Сontainer
   if componentName=="LayerContainer":
      return "Container"
   elif componentName in ["DataData","DataEnvironment"]:
      return "Data"
   elif componentName in ["TrainNormal","TrainReinforce"]:
      return "Train"
   else:
      return "Other"

def getFromDict(dataDict, mapList):
      return reduce(operator.getitem, mapList, dataDict)
   
def forceInDict(dataDict, mapList, value):
   #Creates new branches where needed to be able to put all values into the dictionary
   try:
      path=getFromDict(dataDict, mapList[:-1])
   except:
      forceInDict(dataDict,mapList[:-1],dict())
      path=getFromDict(dataDict, mapList[:-1])
   #Check if something already exists at that spot and in that case make it a dict so both items can be there
   if mapList[-1] in path:
      if type(path[mapList[-1]]) is dict:
         path[mapList[-1]][str(value)]=value
      else:
         path[mapList[-1]]={[mapList[-1]]:[mapList[-1]],str(value):value}
   else:
      path[mapList[-1]]=value

def setInDict(dataDict, mapList, value):
   #Only puts into the dictionary as deep as it can go
   try:
      path=getFromDict(dataDict, mapList[:-1])
      path[mapList[-1]]=value
   except:
      if len(mapList)>1:
         setInDict(dataDict,mapList[:-1],value)
   


def flatten(d, parent_key='', sep='_'):
   items = []
   for k, v in d.items():
      new_key = parent_key + sep + k if parent_key else k
      if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
      else:
            items.append((new_key, v))
   return dict(items)

def prune_tree(root):
   #Removes all depth where it can
   priority_operations=["Conv"]
   
   flatten_root=False
   #Flatten all branches which have a priority operation inside them
   for branch in root.values():
      if type(branch) == str and any(priority_op in branch for priority_op in priority_operations):
         flatten_root=True
   if flatten_root:
      return flatten(root)
   else:
      for name, branch in root.items():
         #Remove pointless depth
         if len(root)==1:
            if  type(branch) == dict:
               return prune_tree(branch)
            else:
               return branch
         #Go deeper into the tree
         if type(branch) == dict:
            root[name]=prune_tree(branch)
      return root

def grow_tree(root):
   #Adds depth where needed but tries to merge where it can instead
   operation_dependency_dict={"AvgPool":["Conv", "Deconv"]}
   nonDicts=[]
   dicts=[]
   #Check what the branches contain
   for name, branch in root.items():
      if type(branch) == dict:
         dicts.append(name)
      else:
         nonDicts.append(name)

   #Take action depending on what they have
   if len(nonDicts)==0:
      for name, branch in root.items():
         newbranch=grow_tree(branch)
         root[name]=newbranch
   if len(nonDicts)>0 and len(dicts)>0:
      if any(nD in operation_dependency_dict for nD in nonDicts):
         #either flatten or merge. For now we do easy which is flatten
         return flatten(root)
      else:
         for name in nonDicts:
            root[name]={name:root[name]}
         for name in dicts:
            root[name]=grow_tree(root[name])
   return root


def wrapWithCast(string,operation):
      parsed=""
      for attrkey,attrvalue in operation.attr.items():
         if attrkey=="T" or attrkey=="dtype":
            parsed=parsedAttrHandler(parseAttribute(attrvalue))
      if parsed:
         string="tf.dtypes.cast("+string+","+parsed+")"
      return string

# def getIndexedOutput(operation):
#    if operation=="FusedBatchNorm":
#       return "[0]"
#    elif operation=="Switch":
#       return "[0]"
#    else:
#       return ""

def createOperationString(operation,previousOperation,name_spaces,name2idDict,layer,layers):
   if inSameNameSpace(operation, previousOperation, name_spaces):
      return "_".join(cleanTensorName(previousOperation.name).split("/")[-2:])
   else:
      #Need to also check if it is connected to the output variable of that layer, otherwise use X[Id]['Variable']
      previousLayer=layers[getNameSpace(previousOperation,name_spaces)]
      if previousLayer["Operations"].index(previousOperation)==len(previousLayer["Operations"])-1:
         if len(layer["backward_connections"])>1:
            return "X['"+ name2idDict[getNameSpace(previousOperation,name_spaces)] +"']['Y']"
         else:
            return "X['Y']"
      else:
         if len(layer["backward_connections"])>1:
            return "X['"+ name2idDict[getNameSpace(previousOperation,name_spaces)] +"']['"+"_".join(cleanTensorName(previousOperation.name).split("/")[-2:])+"']"
         else:
            return "X['"+str("_".join(cleanTensorName(previousOperation.name).split("/")[-2:]))+"']"

def createConstantString(constant,generatedNameDict,layer,trainableFlag):
   new_c_parameters=[]
   constantName=cleanTensorName(constant.name)

   #Check for Weight variables (Trainable variables) to display in frontend
   #TODO: Improve this logic. Look not only in name but also which attribute it represents in the function.
   if "weight" in constantName.lower().split("/")[-1] or (len(constantName.lower().split("/"))>1 and "weight" in constantName.lower().split("/")[-2] and constantName.lower().split("/")[-1]=="read"):
      generatedName="W"
   else:
      generatedName=constantName.split("/")[-1]

   if generatedName in generatedNameDict and generatedNameDict[generatedName]!=constantName:
      name_counter=1
      while True:
         if generatedName+"_"+str(name_counter) not in generatedNameDict or generatedNameDict[generatedName+"_"+str(name_counter)]==constantName:
            generatedName=generatedName+"_"+str(name_counter)
            break
         name_counter+=1

   if generatedName not in generatedNameDict:      
      generatedNameDict[generatedName]=constantName                     
      layer["Code"]+=str(generatedName)+"='loc:@"+str(constantName)+"';\n"

      parsedConstant=explain(funclib.ConstantNameDict[constant.op])
      c_function=parsedConstant[0].func
      c_keywords=list(parsedConstant[0].keywords.keys())
      new_c_parameters.append(generatedName)   #We want the Input to be the reference to the variable which we will fetch in core

      for keyword in c_keywords:
         if keyword=="name":
            new_c_parameters.append(str(keyword)+"='"+constantName+"'")
         elif keyword=="trainable":
            if trainableFlag=="All":
               new_c_parameters.append(str(keyword)+"=True")
            elif trainableFlag=="None":
               new_c_parameters.append(str(keyword)+"=False")
            elif trainableFlag=="Some":
               new_c_parameters.append(str(keyword)+"=True")
            else:
               new_c_parameters.append(str(keyword)+"=True")
         else:
            for attrkey,attrvalue in constant.attr.items():
               if attrkey==keyword:
                  if attrkey=="use_cudnn_on_gpu" or attrkey=="shape":
                     continue
                  parsed=parseAttribute(attrvalue)
                  augmented=augmentParsedAttr(constant.op, keyword, parsed)
                  attrString=parsedAttrHandler(augmented)

                  new_c_parameters.append(str(attrkey)+"="+attrString)
                  break
         
      layer["Code"]+=generatedName+"="+c_function+"("+", ".join(new_c_parameters)+");\n"
   return generatedName

def createGraph(graph_def):
   ###################################Create NameSpaces################################# 
   name_tree={}
   name_graph_def=dict()
   filtered_operations=[]
   non_prio_oprations=[]
   prio_oprations=["Conv"]
   low_prio_ops=[]
   #First we put in the priority operations
   for n in graph_def.node:
      name_graph_def[n.name]=n
      if isValidOperation(n.op):
         filtered_operations.append(cleanTensorName(n.name))
         if any(prio_op.lower() in n.op.lower() for prio_op in prio_oprations):
            namelist=n.name.split("/")
            forceInDict(name_tree,namelist,n.op)
         else:
            low_prio_ops.append(n)
   #Then we put in the other operations but stop if we reach a priority one
   for n in low_prio_ops:
      namelist=n.name.split("/")
      setInDict(name_tree,namelist,n.op)

   grown_tree=grow_tree(name_tree)   #Grows and merges the tree where necessary
   name_spaces=copy.deepcopy(grown_tree)
   # import json
   # print(json.dumps(grown_tree,indent=2,sort_keys=True))
   # print(nonValidOp)
   # error



   # name_tree={}
   # name_graph_def=dict()
   # filtered_operations=[]  
   # for n in graph_def.node:
   #    name_graph_def[n.name]=n
   #    if isValidOperation(n.op):
   #       opName=cleanTensorName(n.name)
   #       filtered_operations.append(opName)
   #       namelist=opName.split("/")
   #       forceInDict(name_tree,namelist,n.op)
         
   # pruned_tree=prune_tree(name_tree)   #Prunes the tree as much as it can, has a problem, it currently removes important middle nodes which only contain 1 dict. Make it
                                         #recursively remove depth where only 1 node exists instead.
   # grown_tree=grow_tree(pruned_tree)   #Grows and merges the tree where necessary
   # name_spaces=copy.deepcopy(grown_tree)

   # import json
   # print(json.dumps(grown_tree,indent=2,sort_keys=True))
   # error
   # return name_spaces

   ######################################Create and Group Layers#######################################
   layers=dict()
   for op_name in filtered_operations:
      op=name_graph_def[op_name]
      name=getNameSpace(op,name_spaces)   #Has issues incase a "middle-node" has been removed. It then stopps in the middle of the branch. Not something that needs to be fixed, just fyi
      if name=="":
         raise Exception("No name space was found in operation " +op.name)
      try:
         layers[name]["Operations"].append(op)
      except:
         layers[name]={"Operations":[op], "StartNodes":[], "Code":"", "backward_connections":[], "forward_connections": []}


   ###########################################Create Id's#######################################################
   nrLayers=len(list(layers.keys()))
   idList=random.sample(range(1, nrLayers+1), nrLayers)
   name2idDict={}
   id2nameDict={}
   for layerName in layers.keys():
      Id=str(idList.pop())
      name2idDict[layerName]=Id
      id2nameDict[Id]=layerName

   #######################################Create Containers#############################################
   #Temporary, as soon as we can have multiple layer containers inside each other we can have more depth than 1 and use the 1-liner where we create the network
   layerContainers={}
   deleteList=[]
   for layerName, layer in layers.items():
      containerNames=["/".join(layerName.split("/")[0:i]) for i in range(1,len(layerName.split("/")))]
      for container in containerNames[:-1]:
         if container not in deleteList:
            deleteList.append(container)
      layerContainers[layerName]=containerNames
   for layerName, containerList in layerContainers.items():
      for d in deleteList:
         if d in layerContainers[layerName]:
            layerContainers[layerName].remove(d)

   ########################################Create an inner and outer graph###############################################
   for layer in layers.values():
      start_nodes=[]
      
      for op in layer["Operations"]:
         inputs=[]

         for inp in op.input:
            if "^" not in inp:
               previousOp=getPreviousOperation(name_graph_def[cleanTensorName(inp)],name_graph_def,filtered_operations)
               if previousOp:
                  inputs.append(previousOp)

         nameSpaceCheck=[inSameNameSpace(op,inp,name_spaces) for inp in inputs]

         if inputs==[] or not any(nameSpaceCheck):
            start_nodes.append(op)
            layer["StartNodes"].append(op)

         for index in np.where(np.array(nameSpaceCheck)==False)[0]:
            connectionNamespace=getNameSpace(inputs[index],name_spaces)
            if name2idDict[connectionNamespace] not in layer["backward_connections"]:
               layer["backward_connections"].append(name2idDict[connectionNamespace])
            if name2idDict[getNameSpace(op, name_spaces)] not in layers[connectionNamespace]["forward_connections"]:
               layers[connectionNamespace]["forward_connections"].append(name2idDict[getNameSpace(op, name_spaces)])

      #Find the nodes connected to the previous nodes:
      new_operations=start_nodes[:]

      cyclicCheck={}
      queue=layer["Operations"][:]
      while queue:
         inputsFromNameSpace=[]
         op=queue.pop(0)

         if op in new_operations:
            continue
         for inp in op.input:
            if "^" not in inp:
               previousOp=getPreviousOperation(name_graph_def[cleanTensorName(inp)],name_graph_def,filtered_operations)
               if previousOp and inSameNameSpace(op,previousOp,name_spaces):
                  inputsFromNameSpace.append(previousOp)

         if set([cleanTensorName(inp.name) for inp in inputsFromNameSpace]).issubset([cleanTensorName(new_op.name) for new_op in new_operations]):
         # if lambda inputsFromNameSpace, new_operations: any(i in inputsFromNameSpace for i in new_operations):
         #    if not set([cleanTensorName(inp.name) for inp in inputsFromNameSpace]).issubset([cleanTensorName(new_op.name) for new_op in new_operations]):
         #       print(op.name)
            new_operations.append(op)
         else:
            queue.append(op)

      layer["Operations"]=new_operations[:]

   # error
   return layers, name_graph_def, filtered_operations, name_spaces, name2idDict, id2nameDict, layerContainers


def parse(trainableFlag, end_points, graph_def_path, checkpoint=None):
   graph_def=getGraphDef(graph_def_path)

   for node in graph_def.node:
      node.device = ""

   # opList=[]
   # for node in graph_def.node:
   #    if node.op not in opList:
   #       opList.append(node.op)
   
   # print(opList)
   # error

   # graph_def = tf.compat.v1.graph_util.extract_sub_graph(graph_def, ["MobilenetV1/Predictions/Reshape_1"])
   # graph_def = tf.compat.v1.graph_util.extract_sub_graph(graph_def, ["MobilenetV2/Predictions/Reshape_1"])
   # graph_def = tf.compat.v1.graph_util.extract_sub_graph(graph_def, ["MobilenetV2/Logits/Squeeze"])

   
   ###################################Incase we want to automatically find the endpoints, we need to run our graph twice -.- ###################################
   if not end_points:
      end_points=[]
      layers, name_graph_def, filtered_operations, name_spaces, name2idDict, id2nameDict, layerContainers=createGraph(graph_def)
      for layer in layers.values():
         #Removes all Assign operations which only Assign weights and are not connected to actual Operations
         if layer["forward_connections"]==[] and layer["backward_connections"]==[] and len(layers)>1:
            continue
         if layer["forward_connections"]==[]:
            not_endpoints=[]
            for op in layer["Operations"][:]:
               for inp in op.input:
                  previousOp=getPreviousOperation(name_graph_def[cleanTensorName(inp)],name_graph_def,filtered_operations)
                  not_endpoints.append(previousOp)
            layer_end_operations=[]
            for op in layer["Operations"][:]:
               if op not in not_endpoints:
                  layer_end_operations.append(cleanTensorName(op.name))
            end_points.extend(layer_end_operations)

      print("Found end operations: ", end_points)

      graph_def = tf.compat.v1.graph_util.extract_sub_graph(graph_def, end_points)
   else:
      end_points=end_points.replace(" ", "").split(",")
      graph_def = tf.compat.v1.graph_util.extract_sub_graph(graph_def, end_points)
   
   layers, name_graph_def, filtered_operations, name_spaces, name2idDict, id2nameDict, layerContainers=createGraph(graph_def)

   # error
   print("Extracting info")
   info=extractCheckpointInfo(end_points,graph_def_path,checkpoint)
   
   print("Got Info")
   valueDict=info.getVariablesAndConstants()
   # valueDict=info.getVariablesFromSess()
   print("Got Values")
   filteredValueDict={}


   # try:
   #    valueDict=info.getAllVariables()
   #    filteredValueDict={}
   # except Exception as e:
   #    valueDict=None
   #    filteredValueDict=str(e)
   
   ###############################################Convert operations into strings######################################
   for layer in layers.values():
      generatedNameDict={} #Map between the generated names and the actual names of variables and constants. Want it to reset for every layer
      for operation in layer["Operations"]:            
         if operation.op in funclib.OpNameDict:
            parsedFunction=explain(funclib.OpNameDict[operation.op])
            function=parsedFunction[0].func
            arguments=parsedFunction[0].args
            keywords=list(parsedFunction[0].keywords.keys())
            parameters=arguments+keywords
            listLooper=0
            # inputCounter=-1
            inputCounter=0

            newParameters=[]
            for parameter in parameters:
               attrString=None

               #Check if the attribute exists as an attr in the pb
               for attrkey,attrvalue in operation.attr.items():
                  if attrkey=="use_cudnn_on_gpu":
                     continue
                  if attrkey==parameter:
                     parsed=parseAttribute(attrvalue)
                     augmented=augmentParsedAttr(operation.op, parameter, parsed)
                     attrString=parsedAttrHandler(augmented)
                  if attrkey=="N" and listLooper==0:
                     listLooper=parseAttribute(attrvalue)

               if attrString==None:
                  #Check if it is an Input
                  while inputCounter<len(operation.input) and "^" in operation.input[inputCounter]:
                     inputCounter+=1
                  if inputCounter<len(operation.input):
                     #If N exists as an attribute it means that one of the arguments is a list. We assume that it is always the first one.
                     if inputCounter==0 and listLooper>0:
                        listParameters=[]
                        for i in range(listLooper):
                           # previousOperation,Identifier,OutputTag=getPreviousComponent(name_graph_def[cleanTensorName(operation.input[inputCounter])],name_graph_def)
                           previousOperation,Identifier,OutputTag=getPreviousComponent(operation.input[inputCounter],name_graph_def)
                           if Identifier=="Operation":
                              listParameters.append(createOperationString(operation,previousOperation,name_spaces,name2idDict,layer,layers)+OutputTag)
                           elif Identifier=="Constant":
                              filteredValueDict[previousOperation.name]=valueDict[previousOperation.name]
                              listParameters.append(createConstantString(previousOperation,generatedNameDict,layer,trainableFlag)+OutputTag)
                           else:
                              pass

                           # previousOperation=getPreviousOperation(name_graph_def[cleanTensorName(operation.input[inputCounter])],name_graph_def,filtered_operations)
                           # if previousOperation!=None:
                           #    listParameters.append(createOperationString(operation,previousOperation,name_spaces,name2idDict,layer,layers))
                           # else:
                           #    constant=getConstants(name_graph_def[cleanTensorName(operation.input[inputCounter])],name_graph_def,filtered_operations)
                           #    if constant!=None:
                           #       #Add constant to the filtered value dict
                           #       filteredValueDict[constant.name]=valueDict[constant.name]

                           #       listParameters.append(createConstantString(constant,generatedNameDict,layer,trainableFlag))
                           #    else:
                           #       # listParameters.append("None")
                           #       pass #Don't want to append None, can cause more damage than leaving it out of the list

                           inputCounter+=1
                        inputCounter-=1 #To compensate for getting one more at the bottom of the function again

                        attrString="["+",".join(listParameters)+"]"
                     #If it is just a normal input
                     else:
                        # previousOperation,Identifier,OutputTag=getPreviousComponent(name_graph_def[cleanTensorName(operation.input[inputCounter])],name_graph_def)
                        previousOperation,Identifier,OutputTag=getPreviousComponent(operation.input[inputCounter],name_graph_def)
                        if Identifier=="Operation":
                           attrString=createOperationString(operation,previousOperation,name_spaces,name2idDict,layer,layers)+OutputTag
                        elif Identifier=="Constant":
                           filteredValueDict[previousOperation.name]=valueDict[previousOperation.name]
                           attrString=createConstantString(previousOperation,generatedNameDict,layer,trainableFlag)+OutputTag
                        else:
                           attrString="None"
                        # previousOperation=getPreviousOperation(name_graph_def[cleanTensorName(operation.input[inputCounter])],name_graph_def,filtered_operations)
                        # if previousOperation!=None:
                        #    attrString=createOperationString(operation,previousOperation,name_spaces,name2idDict,layer,layers)

                        # else:
                        #    constant=getConstants(name_graph_def[cleanTensorName(operation.input[inputCounter])],name_graph_def,filtered_operations)
                           
                        #    if constant!=None:
                        #       #Add constant to the filtered value dict
                        #       filteredValueDict[constant.name]=valueDict[constant.name]

                        #       attrString=createConstantString(constant,generatedNameDict,layer,trainableFlag)

                        #    else:
                        #       attrString="None"

                     inputCounter+=1

                  elif inputCounter>=len(operation.input) and parameter in arguments:
                     #Incase there are no more inputs to take from and we still have to fill in arguments we will assume that we can leave it empty 
                     #(It's either that or setting None, where None can crash easier)
                     attrString=""
                     pass

                  else:
                     attrString="None"

               if parameter in arguments and attrString!="":
                  newParameters.append(attrString)
               elif parameter in keywords and attrString!="None" and attrString!="": #No need to include standard keywords
                  newParameters.append(parameter+"="+attrString)

            #After finding all relevant arguments and keyword, put them together to create the function.
            if layer["Operations"].index(operation)==len(layer["Operations"])-1:
               layer["Code"]+="Y="+function+"("+", ".join(newParameters)+")"
            else:
               layer["Code"]+="_".join(cleanTensorName(operation.name).split("/")[-2:])+"="+function+"("+", ".join(newParameters)+")"
            # layer["Code"]+=getIndexedOutput(operation.op)   #Unforently, some operations returns more than just one value. Since this is not descriped in the protobuff 
                                                            #we just have to assume and hardcode.
            layer["Code"]+=";\n"

   for layername, layer in layers.items():
      print(layername)
      print(layer["Code"])
  
################################ Pygraphviz Code ##############################################
   # import pygraphviz as pgv
   # AG=pgv.AGraph(directed=True)
   

   # class subgraphHolder():
   #    """A way to store nested pygraphviz subgraphs. It can only have zero or one parent.
   #    """
   #    def __init__(self,parent,name,graph=None):
   #       self.parent=parent
   #       self.name=name
   #       self.children={}
   #       if graph is not None:
   #          self.graph=graph
   #       else:
   #          if self.parent!=None:
   #             self.addGraph(None)

   #    def addChild(self,name):
   #       if name not in self.children:
   #          child=subgraphHolder(self,name)
   #          self.children[name]=child
   #          return child
   #       else:
   #          return self.children[name]
      
   #    def addGraph(self,graph=None):
   #       if graph!=None:
   #          self.graph=graph
   #       else:
   #          self.graph=self.parent.graph.add_subgraph(name="cluster"+self.name)

   #    def addNode(self,node):
   #       self.graph.add_node(node,name=self.name)


   # root=subgraphHolder(None,"root",graph=AG)
   # for layerName, layer in layers.items():
   #    currentRoot=root
   #    nameSpaces=layerName.split("/")[:-1]
   #    for nS in nameSpaces:
   #       currentRoot=currentRoot.addChild(nS)
   #    currentRoot.addNode(name2idDict[layerName])

   
   # for layerName, layer in layers.items():
   #    for con in layer["forward_connections"]:
   #       AG.add_edge(name2idDict[layerName],con)

   # import networkx as nx
   # G=nx.drawing.nx_agraph.from_agraph(AG)
   # positions=nx.nx_agraph.graphviz_layout(G,prog='dot')

   # AG.layout(prog='dot')
   # AG.draw('img.png')
####################################################################################################

################################# NetworkX Only Code ###############################################
   import networkx as nx

   G=nx.Graph()
   maxWeight=1
   for layerName, layer in layers.items():
      if len(layerName.split("/"))>maxWeight:
         maxWeight=len(layerName.split("/"))

   for layerName, layer in layers.items():
      for con in layer["forward_connections"]:
         layer2Name=id2nameDict[con]
         layerNamespaces=layerName.split("/")
         layer2Namespaces=layer2Name.split("/")
         weight=1

         if len(layerNamespaces)>len(layer2Namespaces):
            for i in layer2Namespaces:
               if i not in layerNamespaces:
                  weight=maxWeight-layer2Namespaces.index(i)
                  break
         else:
            for i in layerNamespaces:
               if i not in layer2Namespaces:
                  weight=maxWeight-layerNamespaces.index(i)
                  break
         # print(weight)
         G.add_edge(name2idDict[layerName],con,weight=weight)

   
   positions=nx.kamada_kawai_layout(G,scale=1500,dim=2,weight='weight') #,dist=df.to_dict()

################################################################################################


   flipped_positions={node: (x,-y) for (node, (x,y)) in positions.items()}

   xScale=yScale=1.3
   minX=50
   minY=50
   for Id,pos in flipped_positions.items():
      if pos[0]*xScale<minX:
         minX=pos[0]*xScale
      if pos[1]*yScale<minY:
         minY=pos[1]*yScale
   
   # print(positions)
   # error
   
   adjX=50-minX
   adjY=50-minY
   positionsCopy={}
   for Id,pos in flipped_positions.items():
      positionsCopy[Id]=[pos[0]*xScale+adjX,pos[1]*yScale+adjY]
      # pos[0]+=adjX
      # pos[1]+=adjY

   positions=positionsCopy
   


   # print(positions)
   # error

   #######################################Create layers in correct foramt#######################################
   layerDict=dict()
   for layerName,layer in layers.items():
      # print(layerName.split("/")[-1])
      # print(layerContainers[layerName])
      componentName=findComponentName(layer["Code"])
      layerType=getLayerType(componentName)
      try:
         dim=info.getDimensions([layer["Operations"][-1].name])[0]
         # dim=[]
         # dim=[x for x in dim if x is not None]
         if not dim:
            dim=[1]
         elif dim[0]==None and len(dim)>1:
            dim=dim[1:]
         elif dim[0]==None and len(dim)==0:
            dim="None"

         OutputDim=str(dim).replace("[","").replace("]","").replace(", ","x").replace("None","?")
      except Exception as e:
         print("Error: ", e)
         print("In operation: ", [layer["Operations"][-1].name])
         # print("With dim: ", dim)
         OutputDim=""

      layerDict[name2idDict[layerName]]={
         "layerId": name2idDict[layerName],
         "checkpoint": [graph_def_path,checkpoint],
         "endPoints": end_points,
         # "layerName": layerName.split("/")[-1],
         "layerName": layerName,
         "layerType": layerType,
         "layerSettings": "",
         "layerCode":{"Output":layer["Code"]},
         "layerNone": False,
         "layerMeta": {
            # "layerContainerName": ["/".join(layerName.split("/")[0:i]) for i in range(1,len(layerName.split("/")))],
            "layerBgColor": '',
            "layerContainerName": layerContainers[layerName],
            "isInvisible": False,
            "isLock": False,
            "isSelected": False,
            "position": {
               # "top": None,
               # "left": None
               # "top": random.randint(10,700),
               # "left": random.randint(10,700)
               "top":positions[name2idDict[layerName]][0],
               "left":positions[name2idDict[layerName]][1]
            },
            "OutputDim": OutputDim,
            "InputDim": "",
            "containerDiff": {
               "top": 0,
               "left": 0
            }
         },
         "layerCodeError": None,
         "componentName": componentName,
         "connectionOut":layer["forward_connections"],
         "connectionIn":layer["backward_connections"],
         "connectionArrow": layer["forward_connections"]
      }

   ########################################Create Network#####################################################
   Network={
      "network":{
         "networkName":graph_def_path.split("/")[-1].split(".")[-2],
         "networkID":"",
         "networkSettings":None,
         "networkMeta": {},
         "networkElementList": layerDict,
      }
   }
   # import json
   # print(json.dumps(Network,indent=2,sort_keys=True))
   info.close()

   return Network, filteredValueDict

if __name__ == "__main__":
  

   # graph_def_path = './mobilenetv1/mobilenet_v1_1.0_224_quant_frozen.pb' #path to your .pb file
   # graph_def_path = './1559636463459/1/saved_model.pb' #path to your .pb file
   graph_def_path = 'C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/mobilenetv1/mobilenet_v1_1.0_224_quant_eval.pbtxt' #path to your .pbtxt file
   checkpoint='C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/mobilenetv1/mobilenet_v1_1.0_224_quant.ckpt'
   
   # graph_def_path = 'C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/mobilenetV2/mobilenet_v2_1.0_192_eval.pbtxt' #path to your .pbtxt file
   # checkpoint='C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/mobilenetV2/mobilenet_v2_1.0_192.ckpt'

   # graph_def_path = 'C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/mobilenetV2_coral/mobilenet_v2_1.0_224_quant_frozen.pb'
   # graph_def_path = 'C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/mobilenetV2_coral/mobilenet_v2_1.0_224_quant_eval.pbtxt' #path to your .pbtxt file
   # checkpoint='C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/mobilenetV2_coral/mobilenet_v2_1.0_224_quant.ckpt'

   # graph_def_path = 'C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/faster_rcnn/graph.pbtxt' #path to your .pbtxt file
   # # graph_def_path = 'C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/faster_rcnn/frozen_inference_graph.pb'
   # checkpoint='C:/Users/Robert/Documents/PerceptiLabs/PereptiLabsPlatform/Parser/faster_rcnn/model.ckpt-51249'
   # checkpoint=None


   # from extractVariables import extractCheckpointInfo
   # test=extractCheckpointInfo(getGraphDef(graph_def_path),checkpoint)

   # constants=test.getDimensions(["MobilenetV1/Conv2d_1_depthwise/depthwise_weights"])
   # print(constants)

   # parsed=parse("All","all_refined_box_encodings,all_class_predictions_with_background",*[graph_def_path,checkpoint])
   parsed=parse("All","",*[graph_def_path,checkpoint])