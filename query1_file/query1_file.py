import csv
import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageQueryOneFileUpdate
from common.message import MessageQueryOneResult
from common.protocol import *
import multiprocessing
import socket
import errno

CHANNEL_NAME = "rabbitmq"

# File format:
# <client_id>,<cant_linux>,<cant_mac>,<cant_windows>

class QueryOneFile:
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
            protocol = Protocol(client_sock)

            message = protocol.receive()
            client_id = int(message.get_client_id())
            
            with self.file_lock:
                total_linux, total_windows, total_mac = self.get_file_snapshot(client_id)

            message_result = MessageQueryOneResult(client_id, total_linux, total_mac, total_windows)
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
        total_linux = 0
        total_mac = 0
        total_windows = 0

        try:
            with open(self.file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if int(row['client_id']) != client_id:
                        continue
                    total_linux += int(row['total_linux'])
                    total_mac += int(row['total_mac'])
                    total_windows += int(row['total_windows'])
        except FileNotFoundError:
            # Si el archivo no existe, los totales permanecen en 0
            pass
        
        return total_linux, total_windows, total_mac

    
    def process_handle_result_updates(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.handle_new_update)

    def handle_new_update(self, ch, method, properties, message: Message):
        msg_query_one_file_update = MessageQueryOneFileUpdate.from_message(message)

        with self.file_lock:
            self.update_totals_from_csv(msg_query_one_file_update)

        self.service_queues.ack(ch, method)


    def update_totals_from_csv(self, msg_query_one_file_update):
        current_total_linux = 0
        current_total_mac = 0
        current_total_windows = 0

        client_id = int(msg_query_one_file_update.get_client_id())
        
        try:
            with open(self.file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if int(row['client_id']) != client_id:
                        continue
        
                    current_total_linux = int(row['total_linux'])
                    current_total_mac = int(row['total_mac'])
                    current_total_windows = int(row['total_windows'])
        except FileNotFoundError:
            # Si el archivo no existe, los totales permanecen en 0
            pass
        
        updated_total_linux = current_total_linux + int(msg_query_one_file_update.total_linux)
        updated_total_mac = current_total_mac + int(msg_query_one_file_update.total_mac)
        updated_total_windows = current_total_windows + int(msg_query_one_file_update.total_windows)

        logging.critical(f"---NUEVOS VALORES EN FILE---\nCLIENT: {client_id} LINUX: {updated_total_linux} MAC: {updated_total_mac} WINDOWS: {updated_total_windows}")
        
        with open(self.file_path, mode='w', newline='') as file:
            fieldnames = ['client_id', 'total_linux', 'total_mac', 'total_windows']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                'client_id': client_id,
                'total_linux': updated_total_linux,
                'total_mac': updated_total_mac,
                'total_windows': updated_total_windows
            })