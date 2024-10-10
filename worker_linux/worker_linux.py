import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import MessageGameInfo
from common.message import MessageEndOfDataset
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
            msg_eof = MessageEndOfDataset.from_message(message)
            
            if msg_eof.is_last_eof():
                #print("RECIBI LAST EOF")
                self.service_queues.push(self.queue_name_destiny, message)
            
            #print("RECIBI EOF PERO NO LAST")
            self.service_queues.ack(ch, method)
            self.service_queues.close_connection()
            self.running = False
            return


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






    
