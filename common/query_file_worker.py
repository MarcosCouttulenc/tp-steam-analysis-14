import csv
import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageQueryOneFileUpdate
from common.message import MessageQueryOneResult
from common.message import MessageResultStatus
from common.message import ResultStatus
from common.protocol import *
from common.protocol_healthchecker import ProtocolHealthChecker, get_container_name
import multiprocessing
import socket
import errno
import time

CHANNEL_NAME = "rabbitmq"

# File format:
# <client_id>,<cant_linux>,<cant_mac>,<cant_windows>

class QueryFile:
    def __init__(self, queue_name_origin, file_path, result_query_port, listen_backlog,ip_healthchecker, port_healthchecker):
        self.queue_name_origin = queue_name_origin
        self.file_path = file_path
        self.new_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_socket.bind(('', result_query_port))
        self.new_connection_socket.listen(listen_backlog)
        self.file_lock = multiprocessing.Lock()
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        manager = multiprocessing.Manager()
        self.totals = manager.dict()
        self.eof_dict = manager.dict()
        self.ip_healthchecker = ip_healthchecker
        self.port_healthchecker = int(port_healthchecker)
    
    def start(self):
        # Lanzamos proceso para conectarnos al health checker
        connect_health_checker = multiprocessing.Process(
            target = self.process_connect_health_checker 
        )

        process_updates = multiprocessing.Process(target=self.process_handle_result_updates, args=())
        process_queries = multiprocessing.Process(target=self.process_handle_result_queries, args=())

        process_updates.start()
        process_queries.start()
        connect_health_checker.start()

        process_updates.join()
        process_queries.join()
        connect_health_checker.join()


    ## Proceso de conexion con health checker
    ## --------------------------------------------------------------------------------      
    def process_connect_health_checker(self):
        time.sleep(10)

        while self.running:
            skt_next_healthchecker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            skt_next_healthchecker.connect((self.ip_healthchecker, self.port_healthchecker))
            
            # comienza la comunicacion
            healthchecker_protocol = ProtocolHealthChecker(skt_next_healthchecker)

            # le envio el nombre de mi container
            if (not healthchecker_protocol.send_container_name(get_container_name())):
                continue

            # ciclo de checkeo de health
            while healthchecker_protocol.wait_for_health_check():
                healthchecker_protocol.health_check_ack()
    

    ## Proceso para devolver informacion de la query
    ## --------------------------------------------------------------------------------
    def process_handle_result_queries(self):
        while self.running:
            client_sock = self.__accept_new_connection()
            protocol = Protocol(client_sock)

            message = protocol.receive()
            client_id = int(message.get_client_id())

            message_result_status = MessageResultStatus(str(client_id), ResultStatus.PENDING)
            if str(client_id) in self.eof_dict.keys():
                message_result_status = MessageResultStatus(client_id, ResultStatus.FINISHED)
            
            with self.file_lock:
                file_snapshot = self.get_file_snapshot(client_id)

            message_result = self.get_message_result_from_file_snapshot(client_id, file_snapshot)

            protocol.send(message_result_status)
            protocol.send(message_result)

    

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
            
    

    ## Proceso para actualizar resultados de la query
    ## --------------------------------------------------------------------------------
    def process_handle_result_updates(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.handle_new_update)

    def handle_new_update(self, ch, method, properties, message: Message):
        if message.is_eof():
            self.service_queues.ack(ch, method)
            self.eof_dict[(str(message.get_client_id()))] = True
            return

        with self.file_lock:
            self.update_results(message)

        self.service_queues.ack(ch, method)


    def get_message_result_from_file_snapshot(self, client_id, file_snapshot):
        return 0

    def get_file_snapshot(self, client_id):
        return 0

    def update_results(self, message):
        return 0
    
    def is_eof(self):
        return self.EOF