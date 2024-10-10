import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import MessageReviewInfo
from common.message import Message

CHANNEL_NAME =  "rabbitmq"


class EnglishWorker:
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
            self.service_queues.push(self.queue_name_destiny, message)
        else:


            msg_review_info = MessageReviewInfo.from_message(message)
            
            if self.is_in_english(msg_review_info.review.review_text):
                self.service_queues.push(self.queue_name_destiny, message)

        self.service_queues.ack(ch, method)
    
    def is_in_english(self, text):
        return True




    
