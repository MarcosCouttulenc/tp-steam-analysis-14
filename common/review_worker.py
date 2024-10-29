import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import MessageReviewInfo
from common.message import MessageEndOfDataset
from common.message import Message

CHANNEL_NAME =  "rabbitmq"


class ReviewWorker:
    #cant_next= "cant_positivas,cant_query5_reducers"
    def __init__(self, queue_name_origin, queues_name_destiny, cant_next):
        self.queue_name_origin = queue_name_origin
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.queues_destiny = self.init_queues_destiny(queues_name_destiny, cant_next)
    
    def init_queues_destiny(self, queues_name_destiny, cant_next):
        queues_name_destiny_list = queues_name_destiny.split(',')
        cant_next_list = cant_next.split(',')
        rta = {}
        for i in range(len(queues_name_destiny_list)):
            rta[queues_name_destiny_list[i]] = int(cant_next_list[i])
        return rta


    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    
    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():
            self.handle_eof(message, ch, method)
            return
        
        msg_review_info = MessageReviewInfo.from_message(message)

        #logging.critical(f"me llego msj: {message.message_payload}")
        
        if self.validate_review(msg_review_info.review):
            self.forward_message(message)

        self.service_queues.ack(ch, method)
    
    def handle_eof(self, message, ch, method):
        msg_eof = MessageEndOfDataset.from_message(message)
            
        if msg_eof.is_last_eof():
            self.send_eofs(msg_eof)
        
        self.service_queues.ack(ch, method)
        #self.service_queues.close_connection()
        #self.running = False

    def send_eofs(self, msg_eof):
        for queue_name, cant_next in self.queues_destiny.items():
            self.send_eofs_to_queue(queue_name, cant_next, msg_eof)



    def send_eofs_to_queue(self, queue_name, queue_cant, msg_eof):
        msg_eof.set_not_last_eof()

        for _ in range(queue_cant-1):
            self.service_queues.push(queue_name, msg_eof)
            
        msg_eof.set_last_eof()
        self.service_queues.push(queue_name, msg_eof)

    def validate_review(self, review):
        return False

    def forward_message(self, message):
        for queue_name_destiny in self.queues_destiny.keys():
            self.service_queues.push(queue_name_destiny, message)


    
