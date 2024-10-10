import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message_serializer import MessageSerializer
from common.message import MessageGameInfo

CHANNEL_NAME =  "rabbitmq"

class WorkerGameValidator:
    def __init__(self, queue_name_origin: str, queues_name_destiny_str: str):
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queues_name_destiny_str.split(',')
        self.running = True 

    def start(self):
        #logging.critical(f'action: start | result: success')
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.on_pop_message)

    def on_pop_message(self, ch, method, properties, message):
        #logging.critical(f'action: on_pop_message | result: start | body: {message}')

        #if not message.is_eof():
        #    logging.critical(f"GAME VALIDATOR: JUEGO {MessageGameInfo.from_message(message).game.name}")

        for queue_name_destiny in self.queues_name_destiny:
            self.service_queues.push(queue_name_destiny, message)
            #logging.critical(f'action: on_pop_message | result: push | queue: {queue_name_destiny}  | body: {message}')

        #logging.critical(f'action: on_pop_message | result: ack')

        self.service_queues.ack(ch, method)

        if message.is_eof():
            self.running = False   

        #logging.critical(f'action: on_pop_message | result: success')