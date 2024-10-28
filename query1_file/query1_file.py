import csv
import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageQueryOneFileUpdate
from common.message import MessageQueryOneResult
from common.protocol import *


from common.query_file_worker import QueryFile

class QueryOneFile(QueryFile):
    def get_message_result_from_file_snapshot(self, client_id, file_snapshot):
        total_linux = file_snapshot[0]
        total_mac = file_snapshot[1]
        total_windows = file_snapshot[2]
        message_result = MessageQueryOneResult(client_id, total_linux, total_mac, total_windows)
        return message_result

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
        
        return (total_linux, total_windows, total_mac)

    def update_results(self, message):
        msg_query_one_file_update = MessageQueryOneFileUpdate.from_message(message)
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