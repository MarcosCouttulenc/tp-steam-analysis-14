import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageReviewInfo
from common.message import MessageQueryFourFileUpdate
from common.message import MessageEndOfDataset

CHANNEL_NAME =  "rabbitmq"
BUFFER_MAX_SIZE = 50


class QueryFourReducer:
    def __init__(self, queue_name_origin, queues_name_destiny_str):
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queues_name_destiny_str.split(",")
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.buffer = {} # Se van a guardar par de (nombre, cant_reseñas)
        self.curr_cant = 0
    
    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    
    def process_message(self, ch, method, properties, message: Message):

        if message.is_eof():
            msg_eof = MessageEndOfDataset.from_message(message)
            if  msg_eof.is_last_eof():
                print("push eof")
            
            if len(self.buffer) > 0:
                self.save_buffer_in_file_and_clean_it()

            self.running = False
            self.service_queues.ack(ch, method)
            self.service_queues.close_connection()
            return
            
        msg_review_info = MessageReviewInfo.from_message(message)


        self.curr_cant += 1            
        #guardo en el buffer dict o actualizo si ya estaba la clave: (name, cant_reseñas_positivas)
        if not msg_review_info.review.game_name in self.buffer:
            self.buffer[msg_review_info.review.game_name] = 0
        self.buffer[msg_review_info.review.game_name] += 1

        if self.curr_cant >= BUFFER_MAX_SIZE:
            self.save_buffer_in_file_and_clean_it()

        self.service_queues.ack(ch, method)
    
    def buffer_to_list_of_tuples(self):
        rta = []
        for name, cant_reviews in self.buffer.items():
            rta.append((name, cant_reviews))
        return rta

    def save_buffer_in_file_and_clean_it(self):
        # toma lo que hay en el buffer, lo guarda en el archivo y lo mantiene ordenado de mayor a menor segun
        # tiempo de juego.
        for queue_name in self.queues_name_destiny:
            list_of_tuples = self.buffer_to_list_of_tuples()
            msg = MessageQueryFourFileUpdate(list_of_tuples)

            print(f"Save buffer Q4 - {msg}")

            self.service_queues.push(queue_name, msg)
        
        self.curr_cant = 0
        self.buffer = {}