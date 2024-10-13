import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import MessageGameInfo
from common.message import Message
from common.message import MessageEndOfDataset

CHANNEL_NAME =  "rabbitmq"
MESSAGE_TYPE_QUERY_ONE_UPDATE = "query-one-update"
PAYLOAD = "mac"

class MACOSWorker:
    def __init__(self, queue_name_origin, queue_name_destiny):
        self.queue_name_origin = queue_name_origin
        self.queue_name_destiny = queue_name_destiny
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)

    
    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    
    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():
            msg_eof = MessageEndOfDataset.from_message(message)
            
            if msg_eof.is_last_eof():
                self.service_queues.push(self.queue_name_destiny, message)
            
            self.service_queues.ack(ch, method)
            self.service_queues.close_connection()
            self.running = False
            return
        
        mes = MessageGameInfo.from_message(message)
        
        if mes.game.mac:
            update_message = Message(MESSAGE_TYPE_QUERY_ONE_UPDATE, PAYLOAD)
            self.service_queues.push(self.queue_name_destiny, update_message)
        self.service_queues.ack(ch, method)


    
