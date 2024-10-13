import logging
logging.basicConfig(level=logging.CRITICAL)
import socket
import errno

from common.message import *
from common.protocol import Protocol
from common.protocol import *
from middleware.queue import ServiceQueues

CHANNEL_NAME =  "rabbitmq"

class Server:
    def __init__(self, listen_new_connection_port, listen_result_query_port, listen_backlog, cant_game_validators, cant_review_validators):
        self.listen_new_connection_port = listen_new_connection_port
        self.listen_result_query_port = listen_result_query_port
        self.cant_game_validators = cant_game_validators
        self.cant_review_validators = cant_review_validators

        self.new_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_socket.bind(('', listen_new_connection_port))
        self.new_connection_socket.listen(listen_backlog)

        self.service_queues = ServiceQueues(CHANNEL_NAME)
    
    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        try:
            c, addr = self.new_connection_socket.accept()
            return c
        except OSError as e:
            if e.errno == errno.EBADF:  # Bad file descriptor, server socket closed
                return None
            else:
                raise
    
    def start(self):
        client_id = "1"
        client_sock = self.__accept_new_connection()

        protocol = Protocol(client_sock)

        msg_welcome_client = MessageWelcomeClient(client_id, self.listen_result_query_port)
        protocol.send(msg_welcome_client)

        self.process_client_messages(protocol)

    def process_client_messages(self, protocol):
        end_of_data = False
        numero_menasje_recibido = 0

        while (not end_of_data):
            receive_batch = protocol.receive_batch()
            numero_menasje_recibido += len(receive_batch)

            if receive_batch == None:
                logging.critical(f'action: server_msg_received | result: invalid_msg | msg: {receive_batch}')
                return

            for message in receive_batch:
                if message.is_game():
                    self.service_queues.push("queue-games", message)
                elif message.is_review():
                    self.service_queues.push("queue-reviews", message)
                elif message.is_eof():
                    msg_end_of_dataset = MessageEndOfDataset.from_message(message)

                    if msg_end_of_dataset.type == "Game":
                        self.send_eofs_to_queue(msg_end_of_dataset, "queue-games", self.cant_game_validators)
                    else:
                        self.send_eofs_to_queue(msg_end_of_dataset, "queue-reviews", self.cant_review_validators)
                        end_of_data = True
    
    def send_eofs_to_queue(self, msg_end_of_dataset, destiny_queue, cant_workers):
        for _ in range(cant_workers - 1):
            self.service_queues.push(destiny_queue, msg_end_of_dataset)
            
        msg_end_of_dataset.set_last_eof()
        self.service_queues.push(destiny_queue, msg_end_of_dataset)