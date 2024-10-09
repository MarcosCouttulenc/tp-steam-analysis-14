import logging
logging.basicConfig(level=logging.CRITICAL)
import socket
import errno

from common.message import *
from common.protocol import *
from common.message_serializer import MessageSerializer
from middleware.queue import ServiceQueues

CHANNEL_NAME =  "rabbitmq"

class Server:
    def __init__(self, listen_new_connection_port, listen_result_query_port, listen_backlog):
        self.listen_new_connection_port = listen_new_connection_port
        self.listen_result_query_port = listen_result_query_port

        self.new_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_socket.bind(('', listen_new_connection_port))
        self.new_connection_socket.listen(listen_backlog)

        #self.emit_result_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.emit_result_socket.bind(('', listen_result_query_port))
        #self.emit_result_socket.listen(listen_backlog)

        self.service_queues = ServiceQueues(CHANNEL_NAME)
    
    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        try:
            c, addr = self.new_connection_socket.accept()
            #logging.critical(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError as e:
            if e.errno == errno.EBADF:  # Bad file descriptor, server socket closed
                #logging.critical('SOCKET CERRADO - ACCEPT_NEW_CONNECTIONS')
                return None
            else:
                raise
    
    def start(self):
        client_id = "1"
        client_sock = self.__accept_new_connection()

        protocol = Protocol(client_sock)

        msg_welcome_client = MessageWelcomeClient(client_id, self.listen_result_query_port)
        protocol.send(msg_welcome_client)
        #logging.critical(f'action: server_msg_sent | result: success | msg: {msg_welcome_client}')

        self.process_client_messages(protocol)

        

    def process_client_messages(self, protocol):
        #logging.critical(f'action: process_client_messages | result: start | msg: success')

        end_of_data = False

        numero_menasje_recibido = 0

        while (not end_of_data):
            receive_batch = protocol.receive_batch()
            numero_menasje_recibido += len(receive_batch)
            print(f"mensajes recibidos hasta ahora: {numero_menasje_recibido}")
            if receive_batch == None:
                logging.critical(f'action: server_msg_received | result: invalid_msg | msg: {receive_batch}')
                return

            for message in receive_batch:
                if message.is_game():
                    msg_game = MessageGameInfo.from_message(message)
                    self.service_queues.push("queue-games", message)
                    #logging.critical(f'action: server_msg_received | result: success | msg: {msg_game}')
                elif message.is_review():
                    msg_review = MessageReviewInfo.from_message(message)
                    #logging.critical(f'action: server_msg_received | result: success | msg: {msg_review}')
                else:
                    print("\n\nME LLEGO UN END OF DATA\n\n")
                    print(message)
                    msg_end_of_dataset = MessageEndOfDataset.from_message(message)
                    #logging.critical(f'action: server_msg_received | result: success | msg: {msg_end_of_dataset}')
                    end_of_data = True

        #logging.critical(f'action: process_client_messages | result: success | msg: success')