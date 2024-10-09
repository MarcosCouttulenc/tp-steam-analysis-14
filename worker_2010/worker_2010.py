import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import MessageGameInfo
from common.message import Message

CHANNEL_NAME =  "rabbitmq"


class DecadeWorker:
    def __init__(self, queue_name_origin, queue_name_destiny):
        self.queue_name_origin = queue_name_origin
        self.queue_name_destiny = queue_name_destiny
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)

    
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
            self.service_queues.push(self.queue_name_destiny, message)
        else:
            mes = MessageGameInfo.from_message(message)
            #logging.critical(f"Processing message: {mes.pretty_str()}")
            #logging.critical(f"\nVALOR BOOLEANO DE MAC: {mes.game.mac}\n")
            if self.is_from_2010_decade(mes.game.release_date):
                #logging.critical(f"JUEGO DECADA 2010 FILTRADO: {mes.game.name}")

                #logging.info(f"Juego: {mes.game.name} | Pusheando a {self.queue_name_destiny} | Msg: {message.message_payload}")

                self.service_queues.push(self.queue_name_destiny, message)
        self.service_queues.ack(ch, method)
        return





    
