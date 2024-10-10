import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageGameInfo
from common.message import MessageQueryTwoFileUpdate
from common.message import MessageEndOfDataset

CHANNEL_NAME =  "rabbitmq"
BUFFER_MAX_SIZE = 0

class QueryTwoReducer:
    def __init__(self, queue_name_origin, queues_name_destiny_str):
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queues_name_destiny_str.split(",")
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.buffer = [] # Se van a guardar tupla de (nombre, playtime)
    
    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    
    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():
            msg_eof = MessageEndOfDataset.from_message(message)
            print(f"ME LLEGO EOF")
            if  msg_eof.is_last_eof():
                print("push eof")
            
            if len(self.buffer) > 0:
                self.save_buffer_in_file_and_clean_it()

            self.running = False
            self.service_queues.ack(ch, method)
            self.service_queues.close_connection()
            return
    
        msg_game_info = MessageGameInfo.from_message(message)

        #print(f"LLEGO AL REDUCER EL JUEGO:\n{msg_game_info.game.name}")
        
        #logging.critical(msg_game_info.pretty_str())

        self.buffer.append((msg_game_info.game.name, msg_game_info.game.playTime))
        # print("\n\n buffer actual\n\n")
        # print(self.buffer)
        # print("\n\n")
        self.buffer.sort(key=lambda game_data: game_data[1], reverse=True) #game_data: (name, playtime)

        #logging.critical("----QUERY 2 HASTA AHORA----")
        #for game_in_buffer in self.buffer:
        #    logging.critical(game_in_buffer.pretty_str())

        

        if len(self.buffer) >= BUFFER_MAX_SIZE:
            self.save_buffer_in_file_and_clean_it()

        self.service_queues.ack(ch, method)

    def save_buffer_in_file_and_clean_it(self):
        # toma lo que hay en el buffer, lo guarda en el archivo y lo mantiene ordenado de mayor a menor segun
        # tiempo de juego.
        for queue_name in self.queues_name_destiny:
            msg = MessageQueryTwoFileUpdate(self.buffer)

            #print(f"VOY A ENVIAR EL MSG:\n{msg.message_payload}")

            self.service_queues.push(queue_name, msg)
        
        self.buffer = []