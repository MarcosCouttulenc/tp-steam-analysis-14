import langid
import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import MessageReviewInfo
from common.message import Message
from common.message import MessageEndOfDataset

CHANNEL_NAME =  "rabbitmq"

class EnglishWorker:
    def __init__(self, queue_name_origin, queue_name_destiny, cant_query4_reducer):
        self.queue_name_origin = queue_name_origin
        self.queue_name_destiny = queue_name_destiny
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.cant_query4_reducer = cant_query4_reducer


    
    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    
    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():
            msg_eof = MessageEndOfDataset.from_message(message)
            
            if msg_eof.is_last_eof():
                self.send_eofs_to_queue(self.queue_name_destiny, self.cant_query4_reducer, msg_eof)
                
            self.service_queues.ack(ch, method)
            self.service_queues.close_connection()
            self.running = False
            return

        msg_review_info = MessageReviewInfo.from_message(message)
        
        if self.is_in_english(msg_review_info.review.review_text):
            self.service_queues.push(self.queue_name_destiny, message)

        self.service_queues.ack(ch, method)
    
    def is_in_english(self, text):
        idioma, confianza = langid.classify(text)

        return (idioma == 'en')

    def send_eofs_to_queue(self, queue_name, queue_cant, msg_eof):
        msg_eof.set_not_last_eof()

        for _ in range(queue_cant-1):
            self.service_queues.push(queue_name, msg_eof)
            
        msg_eof.set_last_eof()
        self.service_queues.push(queue_name, msg_eof)

    
