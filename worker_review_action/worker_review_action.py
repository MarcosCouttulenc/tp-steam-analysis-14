import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import MessageReviewInfo
from common.message import MessageEndOfDataset
from common.message import Message

CHANNEL_NAME =  "rabbitmq"


class ActionWorker:
    def __init__(self, queue_name_origin, queue_name_destiny, cant_query5_reducer, cant_positivas):
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queue_name_destiny.split(',')
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.cant_query5_reducer = cant_query5_reducer
        self.cant_postivas = cant_positivas


    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    
    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():
            msg_eof = MessageEndOfDataset.from_message(message)
            
            if msg_eof.is_last_eof():
                self.send_eofs(msg_eof)
            
            self.service_queues.ack(ch, method)
            self.service_queues.close_connection()
            self.running = False
            return
        
        msg_review_info = MessageReviewInfo.from_message(message)
        
        if msg_review_info.review.is_action():
            for queue_name_destiny in self.queues_name_destiny:
                self.service_queues.push(queue_name_destiny, message)

        self.service_queues.ack(ch, method)


    def send_eofs(self, msg_eof):
        queue_review_positive = self.queues_name_destiny[0]
        queue_query5_reducer = self.queues_name_destiny[1]

        self.send_eofs_to_queue(queue_review_positive, self.cant_postivas, msg_eof)
        self.send_eofs_to_queue(queue_query5_reducer, self.cant_query5_reducer, msg_eof)

    def send_eofs_to_queue(self, queue_name, queue_cant, msg_eof):
        msg_eof.set_not_last_eof()

        for _ in range(queue_cant-1):
            self.service_queues.push(queue_name, msg_eof)
            
        msg_eof.set_last_eof()
        self.service_queues.push(queue_name, msg_eof)



    
