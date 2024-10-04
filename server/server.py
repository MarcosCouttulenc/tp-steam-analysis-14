import logging
import socket
import errno

from common.message import *
from common.protocol import *
# import pika

class Server:
    def __init__(self, listen_new_connection_port, listen_result_query_port, listen_backlog):
        self.listen_new_connection_port = listen_new_connection_port
        self.listen_result_query_port = listen_result_query_port

        self.new_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_socket.bind(('', listen_new_connection_port))
        self.new_connection_socket.listen(listen_backlog)

        self.emit_result_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.emit_result_socket.bind(('', listen_result_query_port))
        self.emit_result_socket.listen(listen_backlog)
    
    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

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
    
    #def receive_message(self, skt):
    #    data = skt.recv(1024)
    #    return data.decode('utf-8')
    
    #def send_message(self, skt, msg):
    #    msg = "{}\n".format(msg).encode('utf-8')
    #    skt.send(msg)
    
    def start(self):
        client_id = "1"
        client_sock = self.__accept_new_connection()

        protocol = Protocol(client_sock)

        msg_welcome_client = MessageWelcomeClient(client_id, self.listen_result_query_port)
        protocol.send(msg_welcome_client)
        logging.info(f'action: server_msg_sent | result: success | msg: {msg_welcome_client}')

        end_of_data = False
        while (not end_of_data):
            receive_batch = protocol.receive_batch()
            if receive_batch == None:
                logging.info(f'action: server_msg_received | result: invalid_msg | msg: {receive_batch}')
                return

            for message in receive_batch:
                msg_game = MessageGameInfo.from_message(message)
                logging.info(f'action: server_msg_received | result: success | msg: {msg_game}')
    
    #def start(self):
        # logging.basicConfig(level=logging.DEBUG)
        # logging.info('action: server_start | result: success')

        # # Conectar a RabbitMQ
        # connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        # channel = connection.channel()

        # channel.queue_declare(queue='task_queue', durable=True)
        
        # channel.basic_consume(queue='task_queue', on_message_callback=callback, auto_ack=True)
        
        # logging.info('Waiting for messages...')
        # channel.start_consuming()