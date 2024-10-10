import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message_serializer import MessageSerializer
from common.message import MessageGameInfo

CHANNEL_NAME =  "rabbitmq"

class WorkerGameValidator:
    def __init__(self, queue_name_origin: str, queues_name_destiny_str: str, cant_windows, cant_linux, cant_mac, cant_indie):
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queues_name_destiny_str.split(',')
        self.running = True
        self.cant_windows = cant_windows
        self.cant_linux = cant_linux
        self.cant_mac = cant_mac
        self.cant_indie = cant_indie

        self.bigger_cant_containers = max(self.cant_windows, self.cant_linux, self.cant_mac, self.cant_indie)

    def start(self):
        #logging.critical(f'action: start | result: success')
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.on_pop_message)

    def on_pop_message(self, ch, method, properties, message):
        #logging.critical(f'action: on_pop_message | result: start | body: {message}')

        #if not message.is_eof():
        #    logging.critical(f"GAME VALIDATOR: JUEGO {MessageGameInfo.from_message(message).game.name}")

        if message.is_eof():
            for queue_name_destiny in self.queues_name_destiny:
                self.service_queues.push(queue_name_destiny, message)
            self.running = False  
        
        else:

            msg_game_info = MessageGameInfo.from_message(message)
            if not msg_game_info.game.is_incomplete():


                for queue_name_destiny in self.queues_name_destiny:
                    self.service_queues.push(queue_name_destiny, message)
                    #logging.critical(f'action: on_pop_message | result: push | queue: {queue_name_destiny}  | body: {message}')

        #logging.critical(f'action: on_pop_message | result: ack')

        self.service_queues.ack(ch, method)

         

        #logging.critical(f'action: on_pop_message | result: success')