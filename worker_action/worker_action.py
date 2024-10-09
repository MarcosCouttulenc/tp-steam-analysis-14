import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import MessageGameInfo
from common.message import Message
from common.message import MessageQueryOneUpdate

CHANNEL_NAME =  "rabbitmq"
MESSAGE_TYPE_QUERY_ONE_UPDATE = "query-one-update"
PAYLOAD = "mac"

class ACTIONWorker:
    def __init__(self, queue_name_origin, queue_name_destiny):
        self.queue_name_origin = queue_name_origin
        self.queue_name_destiny = queue_name_destiny
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)

    
    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    
    def process_message(self, ch, method, properties, message: Message):
        msg_game_info = MessageGameInfo.from_message(message)
        
        if msg_game_info.game.is_shooter():
            self.service_queues.push(self.queue_name_destiny, message)

        self.service_queues.ack(ch, method)




    
