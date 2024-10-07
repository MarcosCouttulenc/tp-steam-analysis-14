from middleware.queue import ServiceQueues
from common.message import MessageGameInfo

POP_QUEUE_NAME = "queue-mac"
PUSH_QUEUE_NAME = "queue-query1-mac"
CHANNEL_NAME =  "rabbitmq"

class MACOSWorker:
    def __init__(self):
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)

    
    def start(self):
        while self.running:
            self.service_queues.pop(POP_QUEUE_NAME, self.process_message)

    
    def process_message(self, ch, method, properties, message):
        print(f"Processing message: {message}")
        self.service_queues.ack(ch, method)
        return





    
