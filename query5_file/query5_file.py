import csv
import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageQueryFiveFileUpdate
from common.message import MessageQueryFiveResult
from common.protocol import Protocol
from common.protocol import *
import multiprocessing
import socket
import errno

CHANNEL_NAME = "rabbitmq"

class QueryFiveFile:
    def __init__(self, queue_name_origin, file_path, result_query_port, listen_backlog):
        self.queue_name_origin = queue_name_origin
        self.file_path = file_path
        self.new_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_socket.bind(('', result_query_port))
        self.new_connection_socket.listen(listen_backlog)
        self.file_lock = multiprocessing.Lock()
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.totals = {}
    
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
            
            with self.file_lock:
                file_snapshot = self.get_file_snapshot()

            message_result = MessageQueryFiveResult(file_snapshot)
            protocol = Protocol(client_sock)
            protocol.send(message_result)
            client_sock.close()

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
            
    def get_file_snapshot(self):
        file_snapshot = []

        percentil_90 = self.get_percentil_90()

        for name, cant_reviews in self.totals.items():
            if cant_reviews[1] > percentil_90:
                file_snapshot.append(name)
        
        
        
        return file_snapshot

    def get_percentil_90(self):
        neg_reviews = [neg for pos, neg in self.totals.values()]
        neg_reviews_sorted = sorted(neg_reviews)
        percentil_90_pos = int(0.90 * (len(neg_reviews_sorted) - 1))
        percentil_90 = neg_reviews_sorted[percentil_90_pos]
        return percentil_90

    def process_handle_result_updates(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.handle_new_update)

    def handle_new_update(self, ch, method, properties, message: Message):
        msg_query_five_file_update = MessageQueryFiveFileUpdate.from_message(message)

        print(f"VOY A ACTUALIZAR:\n{message.message_payload}")

        with self.file_lock:
            self.update_totals(msg_query_five_file_update)

        self.service_queues.ack(ch, method)


    def update_totals(self, msg_query_five_file_update):
        for (name, cant_pos, cant_neg) in msg_query_five_file_update.buffer:
            if not name in self.totals:
                self.totals[name] = [0, 0]

            self.totals[name][0] += int(cant_pos)
            self.totals[name][1] += int(cant_neg)


        
        
                    


