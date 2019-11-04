class webInterface():
    def __init__():
        pass

class desktopInterface(Interface):
    def __init__():
        pass

    reciever=self.request.get("reciever")
    action = self.request.get("action")
    startTime=time.time()

    if not reciever in self.dataDict:
        self.dataDict[reciever]=dict()

    if reciever not in self.cores:
        core=coreLogic(reciever)
        self.cores[reciever]=core
    else:
        core=self.cores[reciever]

    warnings=core.warningQueue
    warningList=[]

    errors=core.errorQueue
    errorList=[]

    content=""

    
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
            # scope.set_extra("Core properties", core.core.__dict__)
            # coreProperties=dict()
            # for key, value in core.core.__dict__.items():
            #     if type(value).__name__!="dict":
            #         coreProperties[key]=value
            # scope.set_extra("Core properties", coreProperties)
            scope.set_extra("Saved Results Dict", core.savedResultsDict)
            scope.set_extra("Network", core.network)
        

        elif action in lwCalls:
            for dataId, dataValue in self.dataDict[reciever].items():
                scope.set_extra("data object for layer: "+str(dataId), dataValue.__dict__)
        elif action in parseCalls:
            pass
        else:
            # scope.set_extra("Core properties", core.core.__dict__)
            for dataId, dataValue in self.dataDict[reciever].items():
                scope.set_extra("data object for layer: "+str(dataId), dataValue.__dict__)

    #####################################B4End###################################
    

queue_function_translation=[("stop-request","stop-response", "Stop"),
    ("start-request","start-response", "Start"),  #Might have to be a frontend call to cloud, where core then starts as soon as the VM is on
    ("cloud-close-vm-request","cloud-close-vm-response", "empty"),
    ("model-save-request","model-save-response", "saveTrained"),
    ("update-results-request","update-results-response", "updateResults"),
    ("get-status-request", "get-status-response", "getStatus"),    #TODO: Not yet exists as an endpoint!!!!
    ("headless-request","headless-response", "headless"),
    ("get-training-statistics-request","get-training-statistics-response", "getTrainingStatistics"),
    ("get-testing-statistics-request","get-testing-statistics-response", "getTestingStatistics"),
    ("start-test-request","start-test-response", "startTest"),
    ("reset-test-request","reset-test-response", "resetTest"),
    ("get-test-status-request","get-test-status-response", "getTestStatus"),
    ("next-step-request","next-step-response", "nextStep"),
    ("previous-step-request","previous-step-response", "previousStep"),
    ("play-test-request","play-test-response", "playTest"),
    ("pause-request","pause-response", "Pause"),
    ("skip-validation-request","skip-validation-response", "SkipToValidation"),
    ("check-core-request","check-core-response", "checkAlive"),
    ("export-request","export-response", "Export")    #Might have to be moved to LW Core and let that one store all internal variables for open tabs
]

class azureInterface():
    def __init__():
        pass

class Interface():
    def __init__(self, core):
        self._cores={}
        self._core=None

    def _addCore(self, reciever):
        from coreLogic import coreLogic
        core=coreLogic(reciever)
        self._cores[reciever] = core

    def setCore(self, reciever):
        if reciever not in self._cores:
            self._addCore(reciever)
        self._core = self._cores[reciever]

    def globalErrors(self):
        errorList = []
        errors = self._core.errorQueue
        while not errors.empty():
            message = errors.get(timeout=0.05)
            errorList.append(message)
        if errorList:
            self._core.Close()
        return errorList

    def globalWarnings(self):
        warningList = []
        warnings = self._core.warningQueue
        while not warnings.empty():
            message = warnings.get(timeout=0.05)
            warningList.append(message)
        return warningList

    def add_to_checkpointDict(self, content):
        if content["checkpoint"][-1] not in self.checkpointDict:
            from extractVariables import extractCheckpointInfo
            ckptObj=extractCheckpointInfo(content["endPoints"], *content["checkpoint"])
            self.checkpointDict[content["checkpoint"][-1]]=ckptObj.getVariablesAndConstants()
            ckptObj.close()

    def _create_lw_core(self, jsonNetwork):
        graph = Graph(jsonNetwork)
        
        graph_dict = graph.graphs

        for value in graph_dict.values():
            if "checkpoint" in value["Info"] and value["Info"]["checkpoint"]:
                self.add_to_checkpointDict(value["Info"])

        data_container = DataContainer()
        
        session_history_lw = SessionHistory()
        extras_reader = LayerExtrasReader()

        from codehq import CodeHqNew as CodeHq

        module_provider = ModuleProvider()
        module_provider.load('tensorflow', as_name='tf')
        module_provider.load('numpy', as_name='np')
        module_provider.load('pandas', as_name='pd')             
        module_provider.load('gym')
        module_provider.load('json')  
        module_provider.load('os')   
        module_provider.load('skimage')         

        
        for hook_target, hook_func in LW_ACTIVE_HOOKS.items():
            module_provider.install_hook(hook_target, hook_func)

        error_handler = LightweightErrorHandler()
            
        lw_core = LightweightCore(CodeHq, graph_dict,
                                  data_container, session_history_lw,
                                  module_provider, error_handler,
                                  extras_reader, checkpointValues=self.checkpointDict.copy())
        
        return lw_core, extras_reader, data_container

    def get_action(self, action, value):
        if action == "getDataMeta":
            getDataMeta(value)
        elif action == "getPartitionSummary":
            getPartitionSummary()
        elif action == "getCode":
            getCode()
        elif action == "getNetworkInputDim":
            getNetworkInputDim()
        elif action == "getNetworkOutputDim":
            getNetworkOutputDim()
        elif action == "getPreviewSample":
            getPreviewSample()
        elif action == "getPreviewVariableList":
            getPreviewVariableList()
        elif action == "Parse":
            Parse()
        elif action == "Close":
            Close()
        elif action == "updateResults":
            self._core.updateResults()
        elif action == "checkCore":
            self._core.checkCore()
        elif action == "headless":
            On=value
            self._core.headless(On)
        elif action == "getTrainingStatistics":
            self._core.getTrainingStatistics()
        elif action == "getTestingStatistics":
            self._core.getTestingStatistics()
        elif action == "getS3Keys":
            self._core.getS3Keys()
        elif action == "Start":
            self._core.Start()
        elif action == "startTest":
            self._core.startTest()
        elif action == "resetTest":
            self._core.resetTest()
        elif action =="getTestStatus":
            self._core.getTestStatus()
        elif action == "nextStep":
            self._core.nextStep()
        elif action == "previousStep":
            self._core.previousStep()
        elif action == "playTest":
            self._core.playTest()
        elif action == "getIter":
            self._core.getIter()
        elif action == "getEpoch":
            self._core.getEpoch()
        elif action == "Stop":
            self._core.Stop()
        elif action == "Pause":
            self._core.Pause()
        elif action == "Unpause":
            self._core.Unpause()
        elif action == "SkipToValidation":
            self._core.SkipToValidation()
        elif action == "Export":
            self._core.Export()
        elif action == "isTrained":
            self._core.isTrained()
        elif action == "SaveTrained":
            self._core.SaveTrained()
        elif action == "getEndResults":
            self._core.getEndResults()
        elif action == "getStatus":
            self._core.getStatus()
        else:
            raise LookupError("The requested action does not exist")

        
        
    if action == "getDataMeta":
        value=self.request.get("value")
        Id=value["Id"]
        jsonNetwork=value["Network"]

        lw_core, _, data_container = self._create_lw_core(jsonNetwork)
        lw_core.run()


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

        lw_core, _, data_container = self._create_lw_core(jsonNetwork)
        lw_core.run()

        def try_fetch(dict,variable):
            try:
                return dict[variable]
            except:
                return ""

        content=try_fetch(data_container[Id],"_partition_summary")

    elif action == "deleteData":
        value=self.request.get("value")
        if value["Id"] in self.dataDict[reciever]:
            del self.dataDict[reciever][value["Id"]]
            content={"content": "Deleted data on workspace " + str(reciever) + " with Id: " +str(value["Id"])+"."}
        else:
            content={"content": "No such Id had saved data in that workspace"}
        # print(self.dataDict)

    elif action == "removeReciever":
        for value in self.dataDict[reciever].values():
            del value
        del self.dataDict[reciever]
        # print(self.dataDict)
        content={"content": "All data on workspace " + str(reciever) + " has been deleted"}

    elif action == "getCode":
        value=self.request.get("value")
        Id=value["Id"]
        Type=value["Type"]
        Properties=value["Properties"]
        Con=value["backward_connections"]
        layerInfo={"Info":{"Type":Type, "Id": Id, "Properties": Properties}, "Con":Con}
        # jsonNetwork=value['jsonNetwork']
        # Id = value['Id']
        # graph=Graph(jsonNetwork)
        # graph_dict = graph.graphs

        # layerInfo=graph_dict[Id]

        from codehq import CodeHqNew as CodeHq
        
        content = {"Output": CodeHq.get_code_generator(Id,layerInfo).get_code()}

    elif action == "getNetworkInputDim":
        jsonNetwork=self.request.get("value")

        lw_core, extras_reader, _ = self._create_lw_core(jsonNetwork)            
        lw_core.run()
        
        content={}
        # for Id, value in extras_reader.to_dict().items():
        #     inShape[Id]=value["inShape"]

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

        lw_core, extras_reader, _ = self._create_lw_core(jsonNetwork)                        
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

        lw_core, extras_reader, data_container = self._create_lw_core(jsonNetwork)                                    
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
            content = ""



    elif action == "getPreviewVariableList":
        value=self.request.get("value")
        jsonNetwork=value["Network"]
        LayerId=value["Id"]

        lw_core, extras_reader, _ = self._create_lw_core(jsonNetwork)                                                
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
        Paths=value["Paths"]
        trainableFlag=value["Trainable"]
        end_points=value["EndPoints"]
        try:
            containers=value["Containers"]
        except:
            pass
        # Paths=value
        # trainableFlag="All"
        # end_points=""
        correct_file_list=self.getParsingFiles(Paths)
        # if correct_file_list[-1] not in self.checkpointDict:
        #     self.checkpointDict[correct_file_list[-1]]=extractCheckpointInfo(*correct_file_list)
        # try:
        print("Files: " , correct_file_list)
        filteredValueDict=None
        try:
            content, filteredValueDict=parse(trainableFlag, end_points, *correct_file_list)
        except Exception as e:
            print(traceback.format_exc())
            content="Could not parse the file.\n"+str(e)
        if type(filteredValueDict) is dict:
            self.checkpointDict[correct_file_list[-1]]=filteredValueDict
        else:
            warningList.append("Could not load the variables, try changing the End Points.\n"+str(filteredValueDict))
        

        # except Exception as e:
        #     print("Error: ", e)
        #     content={"content":"Parser crashed"}
        #     errors.put("Parser crashed")

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

    

    while not errors.empty():
        message=errors.get(timeout=0.05)
        errorList.append(message)

    while not warnings.empty():
        message=warnings.get(timeout=0.05)
        warningList.append(message)


    if errorList:
        core.Close()
        if not content:
            content={"content":"Core crashed without any error message, closing core"}
        try:
            content["errorMessage"]=errorList
        except:
            content={"content":content, "errorMessage":errorList}
    if warningList:
        try:
            content["warningMessage"]=warningList
        except:
            content={"content":content, "warningMessage":warningList}

    if type(content) is not dict:
        content={"content":content}
    elif type(content) is dict and "content" not in content:
        content={"content":content}

    endTime=time.time()

    response = {
        "content": content
    }
    # print("Requst: %s\nResponse: %s" % (str(action), str(response)))
    # log.debug("Response: " + pprint.pformat(response, depth=6))        
    return response