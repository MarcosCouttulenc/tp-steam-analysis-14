import csv
import logging
logging.basicConfig(level=logging.CRITICAL)

from common.message import Message
from common.message import MessageQueryOneUpdate
from common.message import MessageQueryOneResult
from common.protocol import *
from common.query_file_worker import QueryFile

CANTIDAD_TIPOS_DE_WORKERS_PREVIOS = 3

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
        
        return (total_linux, total_mac, total_windows)

    def update_results(self, message):
        msg_query_one_file_update = MessageQueryOneUpdate.from_message(message)
        current_total_linux = 0
        current_total_mac = 0
        current_total_windows = 0

        aux = {}

        client_id = int(msg_query_one_file_update.get_client_id())
        
        try:
            with open(self.file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if int(row['client_id']) != client_id:
                        aux[row['client_id']] = (row['total_linux'], row['total_mac'], row['total_windows'])
                        continue
        
                    current_total_linux = int(row['total_linux'])
                    current_total_mac = int(row['total_mac'])
                    current_total_windows = int(row['total_windows'])
        except FileNotFoundError:
            pass

        if (msg_query_one_file_update.op_system_supported == "windows"):
            current_total_windows += 1

        if (msg_query_one_file_update.op_system_supported == "linux"):
            current_total_linux += 1

        if (msg_query_one_file_update.op_system_supported == "mac"):
            current_total_mac += 1

        #Log aux (estado previo)
        aux[str(client_id)] = (str(current_total_linux), str(current_total_mac), str(current_total_windows))

        #Log aux (nuevo estado)

        #logging.critical(f"---NUEVOS VALORES EN FILE---\nCLIENT: {client_id} LINUX: {current_total_linux} MAC: {current_total_mac} WINDOWS: {current_total_windows}")
        
        with open(self.file_path, mode='w', newline='') as file:
            fieldnames = ['client_id', 'total_linux', 'total_mac', 'total_windows']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for client_id in aux.keys():
                writer.writerow({
                    'client_id': client_id,
                    'total_linux': aux[client_id][0],
                    'total_mac': aux[client_id][1],
                    'total_windows': aux[client_id][2]
                })
    
    '''
    def set_client_as_finished(self, message):
        if not str(message.get_client_id()) in self.eof_dict.keys():
            self.eof_dict[str(message.get_client_id())] = 0
        self.eof_dict[str(message.get_client_id())] += 1
        print(f"llego EOF. actual: {self.eof_dict}")
    


    def client_finished(self, client_id):
        if not str(client_id) in self.eof_dict.keys():
            return False
        return self.eof_dict[str(client_id)] >= CANTIDAD_TIPOS_DE_WORKERS_PREVIOS
    '''

    def set_client_as_finished(self, message: Message):
        if not str(message.get_client_id()) in self.eof_dict.keys():
            self.eof_dict[str(message.get_client_id())] = {}
        aux = self.eof_dict[str(message.get_client_id())]

        if "Windows" in message.get_message_id():
            aux["Windows"] = True
        if "Linux" in message.get_message_id():
            aux["Linux"] = True
        if "Mac" in message.get_message_id():
            aux["Mac"] = True
        self.eof_dict[str(message.get_client_id())] = aux
        print(f"llego EOF. actual: {self.eof_dict}")
    
    def client_finished(self, client_id):
        if not str(client_id) in self.eof_dict.keys():
            return False
        
        return len(self.eof_dict[str(client_id)].keys()) == 3