from azure.storage.queue import QueueService
from azure.storage.queue.models import QueueMessageFormat
import json
from coreCommunicator import coreCommunicator

core=None
queue_service = QueueService(account_name='uantumetdisks', account_key='65rzvvM8RGmELHhQy3PrJdIQH1fQFH0J9CIdJd5U0zNMwz2V7ifhbJNtub/jLaN0P+3lsYWQQg4wjVsXi/1RWQ==')

config = json.load(open("config.json"))
subscripitionId=config["SubscriptionId"]
print("SubscriptionId: ",subscripitionId)
print("Server Queue up and running!")


while True:
    if not core:
        core=coreCommunicator("VMNetwork")

    messages = queue_service.get_messages('start',visibility_timeout=1)
    for message in messages:
        messageSubId=json.loads(QueueMessageFormat.binary_base64decode(message.content))["SubscriptionId"]
        if messageSubId==subscripitionId:
            value=json.loads(QueueMessageFormat.binary_base64decode(message.content))
            response=core.startCore(value["Graph"])
            answer={"UserId":value["UserId"],"SubscriptionId":value["SubscriptionId"],"result":response}
            queue_service.put_message("start-complete",QueueMessageFormat.binary_base64encode(bytes(json.dumps(answer),"utf-8")))
            queue_service.delete_message('start', message.id, message.pop_receipt)

    messages = queue_service.get_messages('status',visibility_timeout=1)
    for message in messages:
        messageSubId=json.loads(QueueMessageFormat.binary_base64decode(message.content))["SubscriptionId"]
        if messageSubId==subscripitionId:
            value=json.loads(QueueMessageFormat.binary_base64decode(message.content))
            response=core.getStatus()
            answer={"UserId":value["UserId"],"SubscriptionId":value["SubscriptionId"],"result":response}
            queue_service.put_message("status-complete",QueueMessageFormat.binary_base64encode(bytes(json.dumps(answer),"utf-8")))
            queue_service.delete_message('status', message.id, message.pop_receipt)

    messages = queue_service.get_messages('stop',visibility_timeout=1)
    for message in messages:
        messageSubId=json.loads(QueueMessageFormat.binary_base64decode(message.content))["SubscriptionId"]
        if messageSubId==subscripitionId:
            response=core.Stop()
            # answer={"result":response}
            # queue_service.put_message("stop-complete",QueueMessageFormat.binary_base64encode(bytes(json.dumps(answer),"utf-8")))
            queue_service.delete_message('stop', message.id, message.pop_receipt)

    messages = queue_service.get_messages('pause',visibility_timeout=1)
    for message in messages:
        messageSubId=json.loads(QueueMessageFormat.binary_base64decode(message.content))["SubscriptionId"]
        if messageSubId==subscripitionId:
            response=core.Pause()
            # answer={"result":response}
            # queue_service.put_message("stop-complete",QueueMessageFormat.binary_base64encode(bytes(json.dumps(answer),"utf-8")))
            queue_service.delete_message('pause', message.id, message.pop_receipt)
    
    messages = queue_service.get_messages('statistic',visibility_timeout=1)
    for message in messages:
        messageSubId=json.loads(QueueMessageFormat.binary_base64decode(message.content))["SubscriptionId"]
        if messageSubId==subscripitionId:
            value=json.loads(QueueMessageFormat.binary_base64decode(message.content))
            response=core.getLayerStatistics({"layerId":value["layerId"],"view":value["view"],"layerType":value["layerType"]})
            answer={"UserId":value["UserId"],"SubscriptionId":value["SubscriptionId"],"result":response}
            queue_service.put_message("statistic-complete",QueueMessageFormat.binary_base64encode(bytes(json.dumps(answer),"utf-8")))
            queue_service.delete_message('statistic', message.id, message.pop_receipt)