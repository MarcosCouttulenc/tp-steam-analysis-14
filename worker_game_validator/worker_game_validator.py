import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message_serializer import MessageSerializer
from common.message import MessageGameInfo
from common.message import MessageEndOfDataset

CHANNEL_NAME =  "rabbitmq"

class WorkerGameValidator:
    def __init__(self, queue_name_origin: str, queues_name_destiny_str: str, cant_windows, cant_linux, cant_mac, cant_indie):
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queues_name_destiny_str.split(',')
        self.queue_mac = self.queues_name_destiny[0]
        self.queue_windows = self.queues_name_destiny[1]
        self.queue_linux = self.queues_name_destiny[2]
        self.queue_indie = self.queues_name_destiny[3]
        self.queue_bdd = self.queues_name_destiny[4]
        self.running = True
        self.cant_windows = int(cant_windows)
        self.cant_linux = int(cant_linux)
        self.cant_mac = int(cant_mac)
        self.cant_indie = int(cant_indie)


    def start(self):
        #logging.critical(f'action: start | result: success')
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.on_pop_message)

    def on_pop_message(self, ch, method, properties, message):
        #logging.critical(f'action: on_pop_message | result: start | body: {message}')

        #if not message.is_eof():
        #    logging.critical(f"GAME VALIDATOR: JUEGO {MessageGameInfo.from_message(message).game.name}")

        if message.is_eof():
            self.send_eofs(message)
            self.running = False
            self.service_queues.ack(ch, method)
            self.service_queues.close_connection()
        
        else:

            msg_game_info = MessageGameInfo.from_message(message)
            if not msg_game_info.game.is_incomplete():


                for queue_name_destiny in self.queues_name_destiny:
                    self.service_queues.push(queue_name_destiny, message)
                    #logging.critical(f'action: on_pop_message | result: push | queue: {queue_name_destiny}  | body: {message}')

            #logging.critical(f'action: on_pop_message | result: ack')
            self.service_queues.ack(ch, method)

        

         

        #logging.critical(f'action: on_pop_message | result: success')
    
    def send_eofs_to_queue(self, queue_name, queue_cant, message):
        for _ in range(queue_cant-1):
            self.service_queues.push(queue_name, message)
        mes_eof = MessageEndOfDataset.from_message(message)
        mes_eof.set_last_eof()
        print("MENSAJE LAST ENVIANDO:")
        print(mes_eof.message_payload)
        self.service_queues.push(queue_name, mes_eof)
    


    def send_eofs(self, message):

        self.send_eofs_to_queue(self.queue_windows, self.cant_windows, message)
        self.send_eofs_to_queue(self.queue_linux, self.cant_linux, message)
        self.send_eofs_to_queue(self.queue_mac, self.cant_mac, message)
        self.send_eofs_to_queue(self.queue_indie, self.cant_indie, message)
        # La cantidad de workers de bdd es siempre 1
        self.send_eofs_to_queue(self.queue_bdd, 1, message)
