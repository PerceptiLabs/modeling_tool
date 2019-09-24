from azure.storage.queue import QueueService
from azure.storage.queue.models import QueueMessageFormat
import json
from coreCommunicator import coreCommunicator

core=coreCommunicator("VMNetwork") #Only need one core since every VM only will have one core running on them.
queue_service = QueueService(account_name='uantumetdisks', account_key='65rzvvM8RGmELHhQy3PrJdIQH1fQFH0J9CIdJd5U0zNMwz2V7ifhbJNtub/jLaN0P+3lsYWQQg4wjVsXi/1RWQ==')

config = json.load(open("config.json"))
subscripitionId=config["SubscriptionId"]
print("SubscriptionId: ",subscripitionId)
print("Server Queue up and running!")

def stop(value):
    return core.Stop()

def empty(value):
    return "Not yet implemented"


queueNames=[("stop-request","stop-response", stop),
    ("start-request","start-response"),
    ("cloud-close-vm-request","cloud-close-vm-response", empty),
    ("model-save-request","model-save-response"),
    ("cloud-load-data-request","cloud-load-data-response"),
    ("get-data-plot-request","get-data-plot-response"),
    ("get-data-meta-request","get-data-meta-response"),
    ("delete-data-request","delete-data-response"),
    ("remove-reciever-request","remove-reciever-response"),
    ("get-network-data-request","get-network-data-response"),
    ("get-network-input-dim-request","get-network-input-dim-response"),
    ("get-network-output-dim-request","get-network-output-dim-response"),
    ("close-request","close-response"),
    ("update-results-request","update-results-response"),
    ("check-core-request","check-core-response"),
    ("headless-request","headless-response"),
    ("get-training-statistics-request","get-training-statistics-response"),
    ("get-testing-statistics-request","get-testing-statistics-response"),
    ("start-test-request","start-test-response"),
    ("reset-test-request","reset-test-response"),
    ("get-test-status-request","get-test-status-response"),
    ("next-step-request","next-step-response"),
    ("previous-step-request","previous-step-response"),
    ("play-test-request","play-test-response"),
    ("pause-request","pause-response"),
    ("skip-validation-request","skip-validation-response"),
    ("export-request","export-response")]


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

            response={"content": function(value)}

            answer={"UserId":value["UserId"],"SubscriptionId":value["SubscriptionId"],"result":response}
            queue_service.put_message(responseQueue,QueueMessageFormat.binary_base64encode(bytes(json.dumps(answer),"utf-8")))
            queue_service.delete_message(request, message.id, message.pop_receipt)


# if request == "stop-request":
            #     response=core.Stop()

            # elif request == "start-request":
            #     response=core.startCore(value["Graph"])

            # elif request == "cloud-close-vm-request":
            #     #Shouldnt have to do anything here, but might as well stop the core
            #     response=core.Stop()

            # elif request == "model-save-request":

            # elif request == "cloud-load-data-request":

            # elif request == "get-data-plot-request":

            # elif request == "get-data-meta-request":

            # elif request == "delete-data-request":

            # elif request == "remove-reciever-request":

            # elif request == "get-network-data-request":

            # elif request == "get-network-input-dim-request":

            # elif request == "get-network-output-dim-request":

            # elif request == "close-request":

            # elif request == "update-results-request":

            # elif request == "check-core-request":

            # elif request == "headless-request":

            # elif request == "get-training-statistics-request":

            # elif request == "get-testing-statistics-request":

            # elif request == "start-test-request":

            # elif request == "reset-test-request":

            # elif request == "get-test-status-request":

            # elif request == "next-step-request":

            # elif request == "previous-step-request":

            # elif request == "play-test-request":

            # elif request == "pause-request":

            # elif request == "skip-validation-request":

            # elif request == "export-request":

    # messages = queue_service.get_messages('start',visibility_timeout=1)
    # for message in messages:
    #     messageSubId=json.loads(QueueMessageFormat.binary_base64decode(message.content))["SubscriptionId"]
    #     if messageSubId==subscripitionId:
    #         value=json.loads(QueueMessageFormat.binary_base64decode(message.content))
    #         response=core.startCore(value["Graph"])
    #         answer={"UserId":value["UserId"],"SubscriptionId":value["SubscriptionId"],"result":response}
    #         queue_service.put_message("start-complete",QueueMessageFormat.binary_base64encode(bytes(json.dumps(answer),"utf-8")))
    #         queue_service.delete_message('start', message.id, message.pop_receipt)

    # messages = queue_service.get_messages('status',visibility_timeout=1)
    # for message in messages:
    #     messageSubId=json.loads(QueueMessageFormat.binary_base64decode(message.content))["SubscriptionId"]
    #     if messageSubId==subscripitionId:
    #         value=json.loads(QueueMessageFormat.binary_base64decode(message.content))
    #         response=core.getStatus()
    #         answer={"UserId":value["UserId"],"SubscriptionId":value["SubscriptionId"],"result":response}
    #         queue_service.put_message("status-complete",QueueMessageFormat.binary_base64encode(bytes(json.dumps(answer),"utf-8")))
    #         queue_service.delete_message('status', message.id, message.pop_receipt)

    # messages = queue_service.get_messages('stop',visibility_timeout=1)
    # for message in messages:
    #     messageSubId=json.loads(QueueMessageFormat.binary_base64decode(message.content))["SubscriptionId"]
    #     if messageSubId==subscripitionId:
    #         response=core.Stop()
    #         # answer={"result":response}
    #         # queue_service.put_message("stop-complete",QueueMessageFormat.binary_base64encode(bytes(json.dumps(answer),"utf-8")))
    #         queue_service.delete_message('stop', message.id, message.pop_receipt)

    # messages = queue_service.get_messages('pause',visibility_timeout=1)
    # for message in messages:
    #     messageSubId=json.loads(QueueMessageFormat.binary_base64decode(message.content))["SubscriptionId"]
    #     if messageSubId==subscripitionId:
    #         response=core.Pause()
    #         # answer={"result":response}
    #         # queue_service.put_message("stop-complete",QueueMessageFormat.binary_base64encode(bytes(json.dumps(answer),"utf-8")))
    #         queue_service.delete_message('pause', message.id, message.pop_receipt)
    
    # messages = queue_service.get_messages('statistic',visibility_timeout=1)
    # for message in messages:
    #     messageSubId=json.loads(QueueMessageFormat.binary_base64decode(message.content))["SubscriptionId"]
    #     if messageSubId==subscripitionId:
    #         value=json.loads(QueueMessageFormat.binary_base64decode(message.content))
    #         response=core.getLayerStatistics({"layerId":value["layerId"],"view":value["view"],"layerType":value["layerType"]})
    #         answer={"UserId":value["UserId"],"SubscriptionId":value["SubscriptionId"],"result":response}
    #         queue_service.put_message("statistic-complete",QueueMessageFormat.binary_base64encode(bytes(json.dumps(answer),"utf-8")))
    #         queue_service.delete_message('statistic', message.id, message.pop_receipt)