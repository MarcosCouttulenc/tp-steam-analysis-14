from middleware.queue import ServiceQueues
from common.message import MessageGameInfo
from common.message import Message
import socket
import logging
from common.protocol import *

logging.basicConfig(level=logging.CRITICAL)

CHANNEL_NAME =  "rabbitmq"  

class DataBaseWorker():
    
    def __init__ (self,queue_name_origin,data_base,result_query_port, listen_backlog):
        self.queue_name_origin = queue_name_origin
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.data_base =  data_base
        self.running = True
        self.new_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_socket.bind(('', result_query_port))
        self.new_connection_socket.listen(listen_backlog)
    
    
    def start(self):
        ## Primera parte donde recibe los juegos.
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

        ##Empiezo a recibir reviews



        
    def process_message(self, ch, method, properties, message: Message):
        mes = MessageGameInfo.from_message(message)
        self.data_base.store_game(mes.game)
        self.service_queues.ack(ch, method)
        self.data_base.load_games()
        return