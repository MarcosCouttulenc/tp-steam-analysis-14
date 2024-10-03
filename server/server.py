import logging
import socket
import errno
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


        # logging.info('action: accept_connections | result: in_progress')
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
    
    def receive_message(self, skt):
        data = skt.recv(1024)
        return data.decode('utf-8')
    
    def send_message(self, skt, msg):
        msg = "{}\n".format(msg).encode('utf-8')
        skt.send(msg)
    
    def start(self):
        client_sock = self.__accept_new_connection()

        msg_to_send = 'Te pusiste nerviosa? :J'
        self.send_message(client_sock, msg_to_send)
        logging.info(f'action: server_msg_sent | result: success | msg: {msg_to_send}')

        rta = self.receive_message(client_sock)
        logging.info(f'action: server_msg_received | result: success | msg: {rta}')
    
    
    
    
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