from azure.storage.queue import QueueService
from azure.storage.queue.models import QueueMessageFormat
import json
from coreLogic import coreLogic


def start(core,value):
    return core.startCore(value)

def stop(core,value):
    return core.Stop()

def empty(core,value):
    return "Not yet implemented"

def checkAlive(core,value):
    return "Alive"

def saveTrained(core,value):
    return core.saveNetwork(value)

def updateResults(core,value):
    return core.updateResults()

def getStatus(core,value):
    return core.getStatus()

def headless(core,value):
    if value:
        return core.headlessOn()
    else:
        return core.headlessOff()

def getTrainingStatistics(core,value):
    return core.getTrainingStatistics(value)

def getTestingStatistics(core,value):
    return core.getTestingStatistics(value)

def startTest(core,value):
    return core.startTest()

def resetTest(core,value):
    return core.resetTest()

def getTestStatus(core,value):
    return core.resetTest()

def nextStep(core,value):
    return core.nextStep()

def previousStep(core,value):
    return core.previousStep()

def playTest(core,value):
    return core.playTest()

def Pause(core,value):
    return core.Pause()

def SkipToValidation(core,value):
    return core.SkipToValidation()

def Export(core,value):
    return core.Export(value)

#Core
queueNames=[
    ("stop-request","stop-response", stop),
    ("start-request","start-response", start),  #Might have to be a frontend call to cloud, where core then starts as soon as the VM is on
    ("cloud-close-vm-request","cloud-close-vm-response", empty),
    ("model-save-request","model-save-response", saveTrained),
    ("update-results-request","update-results-response", updateResults),
    ("get-status-request", "get-status-response", getStatus),    #TODO: Not yet exists as an endpoint!!!!
    ("headless-request","headless-response", headless),
    ("get-training-statistics-request","get-training-statistics-response", getTrainingStatistics),
    ("get-testing-statistics-request","get-testing-statistics-response", getTestingStatistics),
    ("start-test-request","start-test-response", startTest),
    ("reset-test-request","reset-test-response", resetTest),
    ("get-test-status-request","get-test-status-response", getTestStatus),
    ("next-step-request","next-step-response", nextStep),
    ("previous-step-request","previous-step-response", previousStep),
    ("play-test-request","play-test-response", playTest),
    ("pause-request","pause-response", Pause),
    ("skip-validation-request","skip-validation-response", SkipToValidation),
    ("check-core-request","check-core-response", checkAlive),
    ("export-request","export-response", Export)    #Might have to be moved to LW Core and let that one store all internal variables for open tabs
    ]

def coreQueueProcessor():
    core=coreLogic("VMNetwork", None) #Only need one core since every VM only will have one core running on them.
    queue_service = QueueService(account_name='uantumetdisks', account_key='65rzvvM8RGmELHhQy3PrJdIQH1fQFH0J9CIdJd5U0zNMwz2V7ifhbJNtub/jLaN0P+3lsYWQQg4wjVsXi/1RWQ==')

    config = json.load(open("config.json"))
    subscripitionId=config["SubscriptionId"]
    print("SubscriptionId: ",subscripitionId)
    print("Server Queue up and running!")
    while True:
        # if not core:
        #     core=coreCommunicator("VMNetwork")  #Only need one core since every VM only will have one core running on them.

        for queueTouple in queueNames:
            request=queueTouple[0]
            responseQueue=queueTouple[1]
            function=queueTouple[2]

            messages = queue_service.get_messages(request,visibility_timeout=1)
            for message in messages:
                messageSubId=json.loads(QueueMessageFormat.binary_base64decode(message.content))["SubscriptionId"]
                if messageSubId!=subscripitionId:
                    break
                value=json.loads(QueueMessageFormat.binary_base64decode(message.content))

                warnings=core.warningQueue
                warningList=[]

                errors=core.errorQueue
                errorList=[]

                response={"content": function(core,value)}

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


                answer={"UserId":value["UserId"],"SubscriptionId":value["SubscriptionId"],"result":response}
                queue_service.put_message(responseQueue,QueueMessageFormat.binary_base64encode(bytes(json.dumps(answer),"utf-8")))
                queue_service.delete_message(request, message.id, message.pop_receipt)

if __name__ == "__main__":
    print(queueNames[0])