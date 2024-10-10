import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import MessageGameInfo
from common.message import MessageEndOfDataset
from common.message import Message

CHANNEL_NAME =  "rabbitmq"


class DecadeWorker:
    def __init__(self, queue_name_origin, queue_name_destiny, cant_query2_reducer):
        self.queue_name_origin = queue_name_origin
        self.queue_name_destiny = queue_name_destiny
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.cant_query2_reducer = cant_query2_reducer

    
    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)
    
    def is_from_2010_decade(self, date):
        # date format: "oct 21, 2008". Decade: last two bytes
        decade_release = int(date[-2:])
        if decade_release in range(10, 20):
            return True
        return False


    
    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():
            msg_eof = MessageEndOfDataset.from_message(message)
            
            if msg_eof.is_last_eof():
                self.send_eofs_to_queue(self.queue_name_destiny, self.cant_query2_reducer, msg_eof)
                
            self.service_queues.ack(ch, method)
            self.service_queues.close_connection()
            self.running = False
            return
        
        mes = MessageGameInfo.from_message(message)

        if self.is_from_2010_decade(mes.game.release_date):
            self.service_queues.push(self.queue_name_destiny, message)

        self.service_queues.ack(ch, method)

    def send_eofs_to_queue(self, queue_name, queue_cant, msg_eof):
        msg_eof.set_not_last_eof()
        
        for _ in range(queue_cant-1):
            self.service_queues.push(queue_name, msg_eof)
            
        msg_eof.set_last_eof()
        self.service_queues.push(queue_name, msg_eof)




    
