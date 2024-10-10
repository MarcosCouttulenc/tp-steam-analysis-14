import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import MessageReviewInfo
from common.message import Message

CHANNEL_NAME =  "rabbitmq"

class PositiveWorker:
    def __init__(self, queue_name_origin, queue_name_destiny):
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queue_name_destiny.split(',')
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)

    
    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    
    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():
            for queue_name_destiny in self.queues_name_destiny:
                self.service_queues.push(queue_name_destiny, message)
        else:
            msg_review_info = MessageReviewInfo.from_message(message)

            #print(message)
            
            if msg_review_info.review.is_negative():
                for queue_name_destiny in self.queues_name_destiny:
                    self.service_queues.push(queue_name_destiny, message)

        self.service_queues.ack(ch, method)




    
