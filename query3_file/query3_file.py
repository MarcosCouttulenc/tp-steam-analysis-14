import csv
import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageQueryThreeFileUpdate
from common.message import MessageQueryThreeResult
from common.protocol import Protocol
from common.protocol import *
import multiprocessing
import socket
import errno

CHANNEL_NAME = "rabbitmq"

class QueryThreeFile:
    def __init__(self, queue_name_origin, file_path, result_query_port, listen_backlog):
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
    
    def start(self):
        process_updates = multiprocessing.Process(target=self.process_handle_result_updates, args=())
        process_queries = multiprocessing.Process(target=self.process_handle_result_queries, args=())


        process_updates.start()
        process_queries.start()

        process_updates.join()
        process_queries.join()
    
    def process_handle_result_queries(self):
        while self.running:
            client_sock = self.__accept_new_connection()
            protocol = Protocol(client_sock)

            message = protocol.receive()
            client_id = message.get_client_id()
            
            with self.file_lock:
                top_five = self.get_file_snapshot(client_id)

            message_result = MessageQueryThreeResult(client_id, top_five)
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
            
    def get_file_snapshot(self, client_id):
        
        total_list = []
        for name, cant_reviews in self.totals.items():
            total_list.append((name, cant_reviews))

        
        total_list_sorted = sorted(total_list, key=lambda item: item[1], reverse=True)

        top_five = total_list_sorted[:5]


        return top_five

    
    def process_handle_result_updates(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.handle_new_update)

    def handle_new_update(self, ch, method, properties, message: Message):
        msg_query_three_file_update = MessageQueryThreeFileUpdate.from_message(message)


        with self.file_lock:
            self.update_totals(msg_query_three_file_update)

        self.service_queues.ack(ch, method)


    def update_totals(self, msg_query_three_file_update):
        for name, cant_reviews in msg_query_three_file_update.buffer:
            if not name in self.totals:
                self.totals[name] = 0
            self.totals[name] += int(cant_reviews)

        
        
                    


