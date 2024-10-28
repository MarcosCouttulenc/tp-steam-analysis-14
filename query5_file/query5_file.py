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

class QueryFiveInfo:
    def __init__(self, id, name, cant_neg):
        self.id = id
        self.name = name
        self.cant_neg = cant_neg
    
    def sum_cant_neg(self, new_cant_neg):
        self.cant_neg += new_cant_neg
    
    
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
                file_snapshot = self.get_file_snapshot(client_id)
                
            message_result = MessageQueryFiveResult(client_id, file_snapshot)
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
        file_snapshot = []

        percentil_90 = self.get_percentil_90()

        if percentil_90 == None:
            return file_snapshot

        for name, cant_reviews in sorted(self.totals.items(), key=lambda x: x[1][2], reverse=False):
            if cant_reviews[1] > percentil_90:
                file_snapshot.append((cant_reviews[2], name))
        
        return file_snapshot[:10]

    def get_percentil_90(self):
        if len(self.totals) == 0:
            return None

        neg_reviews = [neg for pos, neg, id in self.totals.values()]
        neg_reviews_sorted = sorted(neg_reviews)
        percentil_90_pos = int(0.90 * (len(neg_reviews_sorted) - 1))

        percentil_90 = neg_reviews_sorted[percentil_90_pos]
        return percentil_90

    def process_handle_result_updates(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.handle_new_update)

    def handle_new_update(self, ch, method, properties, message: Message):
        msg_query_five_file_update = MessageQueryFiveFileUpdate.from_message(message)
        
        with self.file_lock:
            self.update_totals(msg_query_five_file_update)

        self.service_queues.ack(ch, method)


    def update_totals(self, msg_query_five_file_update):
        for (name, cant_pos, cant_neg,game_id) in msg_query_five_file_update.buffer:
            if name not in self.totals:
                self.totals[name] = [0, 0, int(game_id)]
                
            temp = self.totals[name]
            temp[0] += int(cant_pos)
            temp[1] += int(cant_neg)
            self.totals[name] = temp


        
        
                    


