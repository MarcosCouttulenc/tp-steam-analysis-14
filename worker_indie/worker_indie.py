import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import MessageGameInfo
from common.message import MessageEndOfDataset
from common.message import Message

CHANNEL_NAME = "rabbitmq"

class WorkerIndie:
    def __init__(self, queue_name_origin, queue_name_destiny, cant_2010):
        self.queue_name_origin = queue_name_origin
        self.queue_name_destiny = queue_name_destiny
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.cant_2010 = cant_2010

    
    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    
    def process_message(self, ch, method, properties, message: Message):

        if message.is_eof():
            #print("ME LLEGO EOF")
            msg_eof = MessageEndOfDataset.from_message(message)
            
            if msg_eof.is_last_eof():
                #print("EL MIO ES EL LAST")
                #self.service_queues.push(self.queue_name_destiny, message)
                self.send_eofs_to_queue(self.queue_name_destiny, self.cant_2010, msg_eof)
                
            self.service_queues.ack(ch, method)
            self.service_queues.close_connection()
            self.running = False
            return

        msg_game_info = MessageGameInfo.from_message(message)
        
        if msg_game_info.game.is_indie():
            #logging.critical(f"JUEGO Indie FILTRADO: {msg_game_info.game.name}\n")
            #logging.critical(f"Juego: {msg_game_info.game.name} | Pusheando a {self.queue_name_destiny} | Msg: {message.message_payload}")
            self.service_queues.push(self.queue_name_destiny, message)

        self.service_queues.ack(ch, method)
        
    def send_eofs_to_queue(self, queue_name, queue_cant, msg_eof):
        msg_eof.set_not_last_eof()
        
        for _ in range(queue_cant-1):
            self.service_queues.push(queue_name, msg_eof)
            
        msg_eof.set_last_eof()
        print("MENSAJE LAST ENVIANDO:")
        print(msg_eof.message_payload)
        self.service_queues.push(queue_name, msg_eof)
        
        


