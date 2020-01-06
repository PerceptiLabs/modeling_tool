
coreCalls=["Close", "updateResults", "checkCore", "headless", "getTrainingStatistics", "getTestingStatistics", "Start", "startTest", "resetTest", "getTestStatus",
"nextStep", "previousStep", "playTest", "getIter", "getEpoch", "Stop", "Pause", "SkipToValidation", "Export", "getStatus"]
lwCalls=["getDataPlot", "getDataMeta", "deleteData", "removeReciever", "getNetworkData", "getNetworkInputDim", "getNetworkOutputDim", "getPreviewSample"]
parseCalls=["Parse"]
with configure_scope() as scope:
    scope.set_extra("reciever",reciever)
    scope.set_extra("action",action)
    scope.set_extra("value",self.request.get("value"))
    #Check what the request is for and then get the properties needed for that function
    if action in coreCalls:
        scope.set_extra("Saved Results Dict", core.savedResultsDict)
        scope.set_extra("Network", core.network)
    

    elif action in lwCalls:
        for dataId, dataValue in self.dataDict[reciever].items():
            scope.set_extra("data object for layer: "+str(dataId), dataValue.__dict__)
    elif action in parseCalls:
        pass
    else:
        for dataId, dataValue in self.dataDict[reciever].items():
            scope.set_extra("data object for layer: "+str(dataId), dataValue.__dict__)

#####################################B4End###################################
if action == "getDataMeta":
    value=self.request.get("value")
    Id=value["Id"]
    jsonNetwork=value["Network"]
    if "layerSettings" in value:
        layerSettings = value["layerSettings"]
        jsonNetwork[Id]["Properties"]=layerSettings

    lw_core, _, data_container = self._create_lw_core(jsonNetwork, reciever)
    lw_core.run()

    # import pdb; pdb.set_trace()

    def try_fetch(dict,variable):
        try:
            return dict[variable]
        except:
            return ""

    content={
        "Action_space": try_fetch(data_container[Id],"_action_space"),
        "Dataset_size": try_fetch(data_container[Id], "_data_size"),
        "Columns": try_fetch(data_container[Id], "cols")
    }


elif action == "getPartitionSummary":
    value=self.request.get("value")
    Id=value["Id"]
    jsonNetwork=value["Network"]
    if "layerSettings" in value:
        layerSettings = value["layerSettings"]
        jsonNetwork[Id]["Properties"]=layerSettings

    lw_core, _, data_container = self._create_lw_core(jsonNetwork, reciever)
    lw_core.run()

    def try_fetch(dict,variable):
        try:
            return dict[variable]
        except:
            return ""

    content=try_fetch(data_container[Id],"_partition_summary")
    # for id_ in lw_core.error_handler.to_dict().keys():
    #     errorList.append(lw_core.error_handler[id_].error_message)


elif action == "deleteData":
    value=self.request.get("value")
    if value["Id"] in self.dataDict[reciever]:
        del self.dataDict[reciever][value["Id"]]
        content={"content": "Deleted data on workspace " + str(reciever) + " with Id: " +str(value["Id"])+"."}
    else:
        content={"content": "No such Id had saved data in that workspace"}

elif action == "removeReciever":
    for value in self.dataDict[reciever].values():
        del value
    del self.dataDict[reciever]
    content={"content": "All data on workspace " + str(reciever) + " has been deleted"}

elif action == "getCode":
    value=self.request.get("value")
    jsonNetwork=value['Network']
    Id = value['Id']
    if "layerSettings" in value:
        layerSettings = value["layerSettings"]
        jsonNetwork[Id]["Properties"]=layerSettings
    
    if jsonNetwork[Id]["Type"] == "TrainReinforce":
        graph=Graph(jsonNetwork)
        graph_dict = graph.graphs
        layerInfo=graph_dict[Id]
    else:
        layerInfo={"Info":{"Type":jsonNetwork[Id]["Type"], "Id": Id, "Properties": jsonNetwork[Id]['Properties']}, "Con":jsonNetwork[Id]["backward_connections"]}

    from codehq import CodeHqNew as CodeHq
    
    content = {"Output": CodeHq.get_code_generator(Id,layerInfo).get_code()}

elif action == "getNetworkInputDim":
    jsonNetwork=self.request.get("value")

    lw_core, extras_reader, _ = self._create_lw_core(jsonNetwork, reciever)            
    lw_core.run()
    
    content={}

    extras_dict=extras_reader.to_dict()
    for Id, value in jsonNetwork.items():
        extras_value={}
        content[Id]={}

        if Id in extras_dict:
            extras_value=extras_dict[Id]

        con=value['backward_connections']

        if len(con)==1 and con[0] in extras_dict:
            content[Id].update({"inShape":str(extras_dict[con[0]]["outShape"])})
        else:
            tmp=[]
            for i in con:
                if i in extras_dict:
                    tmp.append(extras_dict[i]["outShape"])
            tmp=np.squeeze(tmp).tolist()

            content[Id].update({"inShape":str(tmp).replace("'","")})

        # content[Id]={"inShape":str(extras_dict[jsonNetwork[Id]['backward_connections'][0]]) if len(jsonNetwork[Id]['backward_connections'])==1 else str([extras_dict[i] for i in jsonNetwork[Id]['backward_connections']]).replace("'","")}
        # content[Id].update({"inShape":value["inShape"]})

        if Id in lw_core.error_handler:
            log.info("ErrorMessage: " + str(lw_core.error_handler[Id]))

            content[Id]['Error'] = {
                'Message': lw_core.error_handler[Id].error_message,
                'Row': lw_core.error_handler[Id].error_line
            }
        else:
            content[Id]['Error'] = None
    
elif action == "getNetworkOutputDim":
    jsonNetwork=self.request.get("value")

    lw_core, extras_reader, _ = self._create_lw_core(jsonNetwork, reciever)                        
    lw_core.run()
    
    extrasDict=extras_reader.to_dict()

    content={}

    for Id, value in extrasDict.items():
        content[Id]={}
        content[Id].update({"Dim": str(value["outShape"]).replace("[","").replace("]","").replace(", ","x")})

        if Id in lw_core.error_handler:
            log.info("ErrorMessage: " + str(lw_core.error_handler[Id]))

            content[Id]['Error'] = {
                'Message': lw_core.error_handler[Id].error_message,
                'Row': lw_core.error_handler[Id].error_line
            }
        else:
            content[Id]['Error'] = None                

elif action == "getPreviewSample":
    value=self.request.get("value")
    jsonNetwork=value["Network"]
    LayerId=value["Id"]

    try:
        Variable=value["Variable"]
    except:
        Variable=None

    lw_core, extras_reader, data_container = self._create_lw_core(jsonNetwork, reciever)                                    
    lw_core.run()
    
    sample=""
    if Variable:
        dataContainerDict=data_container.to_dict()
        if LayerId in dataContainerDict:
            sample = dataContainerDict[LayerId][Variable]
    else:
        extrasDict=extras_reader.to_dict()
        if LayerId in extrasDict:
            sample = extrasDict[LayerId]["Sample"]

    if isinstance(sample,tf.Variable):
        sample=sample.numpy()

    if len(np.shape(sample))>1:
        sample=np.squeeze(sample)

    def reduceTo2d(data):
        data_shape=np.shape(np.squeeze(data))
        if len(data_shape)<=2 or (len(data_shape)==3 and (data_shape[-1]==3 or data_shape[-1]==1)):
            return data
        else:
            return reduceTo2d(data[...,-1])

    dataObject=createDataObject([reduceTo2d(np.asarray(sample))])
    
    if self._is_jsonable(dataObject):
        content = dataObject
    else:
        content = createDataObject([""])


elif action == "getPreviewVariableList":
    value=self.request.get("value")
    jsonNetwork=value["Network"]
    LayerId=value["Id"]

    lw_core, extras_reader, _ = self._create_lw_core(jsonNetwork, reciever)                                                
    lw_core.run()
    
    extrasDict=extras_reader.to_dict()
    if LayerId in extrasDict:
        content = {
            "VariableList": extrasDict[LayerId]["Variables"],
            "VariableName": extrasDict[LayerId]["Default_var"],
        }

        if LayerId in lw_core.error_handler:
            log.info("ErrorMessage: " + str(lw_core.error_handler[LayerId]))
            
            content['Error'] = {
                'Message': lw_core.error_handler[LayerId].error_message,
                'Row': lw_core.error_handler[LayerId].error_line
            }
    else:
        content = ""

####################################Parser###################################
elif action == "Parse":
    value=self.request.get("value")
    # Paths=value["Paths"]
    if value["Pb"]:
        pb=value["Pb"][0]
    else:
        pb=value["Pb"]

    if value["Checkpoint"]:
        ckpt=value["Checkpoint"][0]
    else:
        ckpt=value["Checkpoint"]

    Paths = [pb, ckpt]
    trainableFlag=value["Trainable"]
    end_points=value["EndPoints"]
    containers=value["Containers"]
    try:
        correct_file_list=self.getParsingFiles(Paths)
    except Exception as e:
        content=e
        print(e)

    filteredValueDict=None
    try:
        content, filteredValueDict=parse(trainableFlag, end_points, *correct_file_list)
    except Exception as e:
        print(traceback.format_exc())
        content="Could not parse the file.\n"+str(e)
        errorList.append("Could not parse the file")
    if type(filteredValueDict) is dict:
        self.checkpointDict[correct_file_list[-1]]=filteredValueDict
    else:
        warningList.append("Could not load the variables, try changing the End Points.\n"+str(filteredValueDict))
    
####################################Computing server#########################
elif action == "Close":
    content="Shutting down app"
    self.shutDown()
    
    # for c in self.cores.values():
    #     content=c.Close()
    #     del c
    # sys.exit(1)

elif action == "updateResults":
    content=core.updateResults()

elif action == "setLogLevel":
    logLevel = self.request.get("value")
    log.setLevel(logLevel)
    content = "Logging has been set to " + logLevel

elif action == "setUser":
    userInfo = self.request.get("value")
    with configure_scope() as scope:
        scope.user = userInfo

elif action == "checkCore":
    content=core.checkCore()

elif action == "headless":
    value=self.request.get("value")
    if value:
        content=core.headlessOn()
    else:
        content=core.headlessOff()

elif action == "getTrainingStatistics":
    value=self.request.get("value")
    content=core.getTrainingStatistics(value)

elif action == "getTestingStatistics":
    value=self.request.get("value")
    content=core.getTestingStatistics(value)
################## Other ######################
elif action == "getS3Keys":
    value = self.request.get("value")
    adapter = S3BucketAdapter(value['bucket'],
                                value['aws_access_key_id'], value['aws_secret_access_key'])
    content = adapter.get_keys(value['delimiter'], value['prefix'])                    
################## Deprecated ######################
elif action == "getLayerStatistics":
    value=self.request.get("value")
    result=core.getLayerStatistics(value)
    content=result

elif action == "Start":
    network=self.request.get("value")
    for value in network['Layers'].values():
        if "checkpoint" in value and value["checkpoint"]:
            self.add_to_checkpointDict(value)
    content=core.startCore(network, self.checkpointDict.copy())

elif action=="startTest":
    content=core.startTest()

elif action=="resetTest":
    content=core.resetTest()

elif action =="getTestStatus":
    content=core.getTestStatus()

elif action == "nextStep":
    content=core.nextStep()

elif action == "previousStep":
    content=core.previousStep()

elif action == "playTest":
    content=core.playTest()

################## OutDated ######################
elif action == "getStatistics":
    value=self.request.get("value")
    content=core.getStatistics(value)

elif action == "getIter":
    content=core.getIter()

elif action == "getEpoch":
    content=core.getEpoch()

elif action == "Stop":
    content=core.Stop()

elif action == "Pause":
    content=core.Pause()

elif action == "Unpause":
    content=core.Unpause()

elif action == "SkipToValidation":
    content=core.skipToValidation()

elif action == "Export":
    value=self.request.get("value")
    content=core.exportNetwork(value)

elif action == "isTrained":
    content=core.isTrained()

elif action == "SaveTrained":
    value=self.request.get("value")
    content=core.saveNetwork(value)

elif action == "getEndResults":
    content=core.getEndResults()

elif action == "getStatus":
    content=core.getStatus()

else:
    warningList.append("Invalid action " + str(action))