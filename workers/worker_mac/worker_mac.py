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
            message: MessageGameInfo = self.service_queues.pop(POP_QUEUE_NAME)
            self.process_message(message)

    
    def process_message(self, message: MessageGameInfo):
        print(f"Processing message: {message}")
        if (message.game.mac):
            print(f"Game {message.game.name} is available for MACOS")
            #enviar a la query1
            self.service_queues.push(PUSH_QUEUE_NAME, " ")
        else: pass





    
