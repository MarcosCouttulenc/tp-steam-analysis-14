import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageGameInfo
from common.message import MessageQueryTwoFileUpdate
from common.message import MessageEndOfDataset

CHANNEL_NAME =  "rabbitmq"

class ReducerWorker:
    def __init__ (self,queue_name_origin, queues_name_destiny_str):
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queues_name_destiny_str.split(",")
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        
        self.buffer = self.init_buffer()


    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    def update_buffer(self, message: Message):
        return 0

    def send_buffer_to_file(self, client_id):
        return 0
    
    def init_buffer(self):
        return 0
    
    def buffer_contains_items(self):
        return True

    def buffer_is_full(self):
        return True

    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():
            self.handle_eof(ch, method, properties, message)
            return
    
        self.update_buffer(message)

        if self.buffer_is_full():
            self.send_buffer_to_file(message.get_client_id())

        self.service_queues.ack(ch, method)

    def handle_eof(self, ch, method, properties, message: Message):
        msg_eof = MessageEndOfDataset.from_message(message)
        
        if  msg_eof.is_last_eof():
            print("push eof")
        
        if self.buffer_contains_items():
            self.send_buffer_to_file(message.get_client_id())

        self.running = False
        self.service_queues.ack(ch, method)
        self.service_queues.close_connection()
    
    
    