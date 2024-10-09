import csv
import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageQueryTwoFileUpdate
from common.message import MessageQueryTwoResult
from common.protocol import *
import multiprocessing
import socket
import errno

CHANNEL_NAME = "rabbitmq"

class QueryTwoFile:
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
                top_ten = self.get_file_snapshot()

            message_result = MessageQueryTwoResult(top_ten)
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
        top_ten = {}
        with open(self.file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                top_ten[row['game']] = row['playTime']
        return top_ten


    
    def process_handle_result_updates(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.handle_new_update)

    def handle_new_update(self, ch, method, properties, message: Message):
        msg_query_two_file_update = MessageQueryTwoFileUpdate.from_message(message)

        with self.file_lock:
            self.update_totals_from_csv(msg_query_two_file_update)

        self.service_queues.ack(ch, method)


    def update_totals_from_csv(self, msg_query_one_file_update):

        old_top_ten = {}
        try :
            with open(self.file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    old_top_ten[row['game']] = row['playTime']
        except FileNotFoundError:
            pass

        new_doc = (old_top_ten + msg_query_one_file_update)
        new_top_ten = dict(sorted(new_doc.items(), key=lambda item: item[1], reverse=True)[:10])

        logging.critical(f"---NUEVOS VALORES EN FILE---\n{new_top_ten}")


        with open(self.file_path, mode='w') as file:
            fieldnames = ['game', 'playTime']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for game, playTime in new_top_ten.items():
                writer.writerow({'game': game, 'playTime': playTime})
        
                    


