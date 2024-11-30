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
    
    def __init__ (self,queue_name_origin,data_base,result_query_port, listen_backlog, cant_clients):
        self.queue_name_origin = queue_name_origin
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.data_base =  data_base
        self.running_queue = True
        self.running_socket = False
        self.cant_clients = cant_clients
        self.curr_cant_eofs = 0
        
        self.new_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_socket.bind(('', result_query_port))
        self.new_connection_socket.listen(listen_backlog)
    
    
    def start(self):
        # Procesamos todos los juegos.
        while self.running_queue:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

        # Cuando la bd esta llena, solo atiendo consultas.

        print("termine de guardar juegos, me pongo a aceptar conexion")
        self.running_socket = True
        while self.running_socket:
            client_sock = self.__accept_new_connection()

            print(f"nueva conexion llego")

            protocol = Protocol(client_sock)
            msg = protocol.receive()

            print(f"me llego query: {msg.message_payload}")

            if msg.is_eof():
                self.running_socket = False
                client_sock.close()
                return

            msg_query = MessageQueryGameDatabase.from_message(msg)

            print("voy a buscar el juego")
            game = self.data_base.get_game(msg_query.get_client_id(), msg_query.game_id)
            print("encontre el juego")
            msg_game_info = MessageGameInfo(msg_query.message_id, msg_query.get_client_id(), game)

            print(f"base de datos a punto de enviar: {msg_game_info.message_payload}")
            protocol.send(msg_game_info)
            print(f"envie el juego")

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
            self.curr_cant_eofs += 1
            print(f"me llego un eof, cant de eof actuales: {self.curr_cant_eofs}")
            print(f"cant de clientes: {self.cant_clients}")
            if  self.curr_cant_eofs == self.cant_clients:
                print("pongo en falso el running_queue")
                self.running_queue = False
                self.service_queues.ack(ch, method)
                self.service_queues.close_connection()

            else:
                self.service_queues.ack(ch, method)
        else:
            msg_game_info = MessageGameInfo.from_message(message)
            print(f"voy a guardar el juego {msg_game_info.game.name}")
            self.data_base.store_game(msg_game_info.get_client_id(),msg_game_info.game)
            print(f"guarde el juego {msg_game_info.game.name}")
            self.service_queues.ack(ch, method)