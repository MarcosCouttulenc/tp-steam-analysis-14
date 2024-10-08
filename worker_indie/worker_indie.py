import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import MessageGameInfo
from common.message import Message

CHANNEL_NAME = "rabbitmq"

class WorkerIndie:
    def __init__(self, queue_name_origin, queue_name_destiny):
        self.queue_name_origin = queue_name_origin
        self.queue_name_destiny = queue_name_destiny
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)

    
    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    
    def process_message(self, ch, method, properties, message: Message):
        msg_game_info = MessageGameInfo.from_message(message)
        
        if msg_game_info.game.is_indie():
            #logging.critical(f"JUEGO Indie FILTRADO: {msg_game_info.game.name}\n")
            #logging.critical(f"Juego: {msg_game_info.game.name} | Pusheando a {self.queue_name_destiny} | Msg: {message.message_payload}")
            self.service_queues.push(self.queue_name_destiny, message)

        self.service_queues.ack(ch, method)




