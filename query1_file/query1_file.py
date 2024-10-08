import csv
import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageQueryOneFileUpdate
import multiprocessing

CHANNEL_NAME = "rabbitmq"

class QueryOneFile:
    def __init__(self, queue_name_origin, file_path):
        self.queue_name_origin = queue_name_origin
        self.file_path = file_path
        self.file_lock = multiprocessing.Lock()
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.totals = {}
    
    def start(self):
        process_updates = multiprocessing.Process(target=self.process_handle_result_updates, args=())
        process_queries = multiprocessing.Process(target=self.process_handle_result_queries, args=())

        process_updates.join()
        process_queries.join()
    
    def process_handle_result_updates(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.handle_new_update)
    
    def process_handle_result_queries(self):
        print("todo")
        #todo
        #while is running
            #socket.accept
            #lockear file
            #get snapshot_file
            #unlock
            #socket.send(snapshot_file)
            #socker.close()

    
    def handle_new_update(self, ch, method, properties, message: Message):
        msg_query_one_file_update = MessageQueryOneFileUpdate.from_message(message)

        with self.file_lock:
            self.update_totals_from_csv(msg_query_one_file_update)

        self.service_queues.ack(ch, method)


    def update_totals_from_csv(self, msg_query_one_file_update):
        current_total_linux = 0
        current_total_mac = 0
        current_total_windows = 0
        
        try:
            with open(self.file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    current_total_linux = int(row['total_linux'])
                    current_total_mac = int(row['total_mac'])
                    current_total_windows = int(row['total_windows'])
        except FileNotFoundError:
            # Si el archivo no existe, los totales permanecen en 0
            pass
        
        updated_total_linux = current_total_linux + int(msg_query_one_file_update.total_linux)
        updated_total_mac = current_total_mac + int(msg_query_one_file_update.total_mac)
        updated_total_windows = current_total_windows + int(msg_query_one_file_update.total_windows)
        
        with open(self.file_path, mode='w', newline='') as file:
            fieldnames = ['total_linux', 'total_mac', 'total_windows']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                'total_linux': updated_total_linux,
                'total_mac': updated_total_mac,
                'total_windows': updated_total_windows
            })