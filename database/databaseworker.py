from middleware.queue import ServiceQueues
from common.message import MessageGameInfo
from common.message import Message

CHANNEL_NAME =  "rabbitmq"  

class BaseDateWorker():
    
    def __init__ (self,queue_name_origin,data_base):
        self.queue_name_origin = queue_name_origin
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.data_base =  data_base
        self.data_base.start()
    
    
    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)


    def process_message(self, ch, method, properties, message: Message):
        mes = MessageGameInfo.from_message(message)
        self.data_base.store_game(mes.game)
        self.service_queues.ack(ch, method)
        return