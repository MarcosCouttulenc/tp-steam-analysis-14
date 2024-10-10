from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageGameInfo
from common.message import MessageQueryGameDatabase
from common.protocol import *

import socket
import errno
import logging
logging.basicConfig(level=logging.CRITICAL)


CHANNEL_NAME =  "rabbitmq"  

class DataBaseWorker():
    
    def __init__ (self,queue_name_origin,data_base,result_query_port, listen_backlog):
        self.queue_name_origin = queue_name_origin
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.data_base =  data_base
        self.running_queue = True
        self.running_socket = False
        
        self.new_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_socket.bind(('', result_query_port))
        self.new_connection_socket.listen(listen_backlog)
    
    
    def start(self):
        # Procesamos todos los juegos.
        while self.running_queue:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

        # Cuando la bd esta llena, solo atiendo consultas.
        self.running_socket = True
        while self.running_socket:
            client_sock = self.__accept_new_connection()
            protocol = Protocol(client_sock)
            msg = protocol.receive()
            msg_query = MessageQueryGameDatabase.from_message(msg)
            game = self.data_base.get_game(msg_query.game_id)
            logging.critical(f"Voy a responser game info de id: {msg_query.game_id}")
            msg_game_info = MessageGameInfo(game)
            protocol.send(msg_game_info)

    def __accept_new_connection(self):
        try:
            c, addr = self.new_connection_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError as e:
            if e.errno == errno.EBADF:  # Bad file descriptor, server socket closed
                logging.info('SOCKET CERRADO - ACCEPT_NEW_CONNECTIONS')
                return None
            else:
                raise
        
    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():
            self.running_queue = False
            self.service_queues.close_connection()
            return

        msg_game_info = MessageGameInfo.from_message(message)
        self.data_base.store_game(msg_game_info.game)
        self.service_queues.ack(ch, method)
        #self.data_base.get_game(msg_game_info.game.id)