import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import MessageGameInfo
from common.message import Message

CHANNEL_NAME =  "rabbitmq"
MESSAGE_TYPE_QUERY_ONE_UPDATE = "query-one-update"
PAYLOAD = "linux"

class LinuxWorker:
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

            mes = MessageGameInfo.from_message(message)

            #logging.critical(f"LINUX: JUEGO {mes.game.name}")

            #logging.critical(f"Processing message: {mes.pretty_str()}")
            #logging.critical(f"\nVALOR BOOLEANO DE MAC: {mes.game.mac}\n")
            if mes.game.linux:
                #logging.critical(f"JUEGO Linux FILTRADO: {mes.game.name}")
                update_message = Message(MESSAGE_TYPE_QUERY_ONE_UPDATE, PAYLOAD)

                #logging.info(f"Juego: {mes.game.name} | Pusheando a {self.queue_name_destiny} | Msg: {update_message.message_payload}")

                self.service_queues.push(self.queue_name_destiny, update_message)
                #logging.info(f"JUEGO MAC FILTRADO: {message.game.name}")
        self.service_queues.ack(ch, method)
        return





    
