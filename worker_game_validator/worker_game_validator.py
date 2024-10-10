import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message_serializer import MessageSerializer

CHANNEL_NAME =  "rabbitmq"

class WorkerGameValidator:
    def __init__(self, queue_name_origin: str, queues_name_destiny_str: str):
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queues_name_destiny_str.split(',')
        self.running = True 

    def start(self):
        logging.info(f'action: start | result: success')
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.on_pop_message)

    def on_pop_message(self, ch, method, properties, message):
        logging.info(f'action: on_pop_message | result: start | body: {message}')

        for queue_name_destiny in self.queues_name_destiny:
            self.service_queues.push(queue_name_destiny, message)
            logging.info(f'action: on_pop_message | result: push | queue: {queue_name_destiny}  | body: {message}')

        logging.info(f'action: on_pop_message | result: ack')

        self.service_queues.ack(ch, method)

        if message.is_eof():
            self.running = False   

        logging.info(f'action: on_pop_message | result: success')