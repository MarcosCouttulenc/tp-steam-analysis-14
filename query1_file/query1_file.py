import csv
import logging
import os
from collections import defaultdict
logging.basicConfig(level=logging.CRITICAL)

from common.message import Message
from common.message import MessageBatch
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

        
    def init_file_state(self):
        # Estado del worker
        if not os.path.exists(self.path_status_info):
            os.makedirs(os.path.dirname(self.path_status_info), exist_ok=True)
        else:
            with open(self.path_status_info, 'r') as file:
                line = file.readline().strip()

                # La linea tiene esta forma -> seq_number_actual|F1,M1|F2,M3|F3,M6..
                data = line.split("|")
                self.actual_seq_number = int(data[0])
                for filter_data in data[1:]:
                    filter_info = filter_data.split(",")
                    self.last_seq_number_by_filter[filter_info[0]] = filter_info[1]
                    
                # La siguiente linea corresponde a los EOF de los clientes
                line = file.readline().strip()

                if line:
                    data_client = line.split("|")
                    aux = {}
                    for client_data in data_client:
                        client_data = client_data.split("!")
                        client_id = client_data[0]
                        eof_data = client_data[1].split("$")
                        client_aux = {}
                        for eof in eof_data:
                            eof = eof.split(",")
                            client_aux[eof[0]] = eof[1]
                        aux[client_id] = client_aux
                    
                    self.eof_dict = aux
                    
        self.recover_from_transaction_log()

        

    def get_file_snapshot(self, client_id):
        client_id = str(client_id)
        file_info = self.get_file_info()
        
        if not client_id in file_info.keys():
            file_info[client_id] = {"linux": 0, "mac": 0, "windows": 0}
        
        return (file_info[client_id]["linux"], file_info[client_id]["mac"], file_info[client_id]["windows"])
    

    def update_results(self, message):
        file_info = self.get_file_info()

        client_id = str(message.get_client_id())
        msg_batch = MessageBatch.from_message(message)

        for msg in msg_batch.batch:
            msg_query_one_file_update = MessageQueryOneUpdate.from_message(msg)
            client_id = str(msg_query_one_file_update.get_client_id())

            file_info = defaultdict(lambda: {"linux": 0, "mac": 0, "windows": 0}, file_info)

            os_field = msg_query_one_file_update.op_system_supported.lower()
            if os_field in file_info[client_id]:
                file_info[client_id][os_field] += 1
        
        self.update_results_in_disk(file_info)


    def update_results_in_disk(self, file_info):
        with open(self.file_path, mode='w', newline='') as file:
            fieldnames = ['client_id', 'total_linux', 'total_mac', 'total_windows']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for client_id, os_counts in file_info.items():
                writer.writerow({
                    'client_id': client_id,
                    'total_linux': os_counts["linux"],
                    'total_mac': os_counts["mac"],
                    'total_windows': os_counts["windows"]
                })

    def get_file_info(self):
        aux = {}
        
        if not os.path.exists(self.file_path):
            print("Archivo no encontrado:", self.file_path)
        
        try:
            with open(self.file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    aux[str(row['client_id'])] = {
                        "linux": int(row['total_linux']), 
                        "mac": int(row['total_mac']), 
                        "windows": int(row['total_windows'])
                    }
        except FileNotFoundError:
            print("No encontre el file del resultado")
        
        return aux

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
    
    def save_state_in_disk(self):
        last_seq_number_by_filter_data = "|".join(f"{key},{value}" for key, value in self.last_seq_number_by_filter.items())
        eof_clients_data = self.get_eof_dict_to_string()
        data = f"{str(self.actual_seq_number)}|{last_seq_number_by_filter_data}\n{eof_clients_data}"
        temp_path = self.path_status_info + '.tmp'
        
        with open(temp_path, 'w') as temp_file:
            temp_file.write(data)
            temp_file.flush() # Forzar escritura al sistema operativo
            os.fsync(temp_file.fileno()) # Asegurar que se escriba físicamente en disco

        os.replace(temp_path, self.path_status_info)

    
    def get_eof_dict_to_string(self):
        eof_client_list = []
        for client_id, dict_eofs in self.eof_dict.items():
            cadena = ""
            cadena += client_id
            cadena += "!"
            cadena += "$".join(f"{key},{value}" for key, value in dict_eofs.items())
            eof_client_list.append(cadena)
        eof_clients_data = "|".join(eof_client_list)
        return eof_clients_data

    
    ## Transaction Log
    ## --------------------------------------------------------------------------------

    def get_transaction_log(self, message: Message):
        transaction_log = ""

        file_info = self.get_file_info()
        client_id = str(message.get_client_id())
        msg_batch = MessageBatch.from_message(message)

        for msg in msg_batch.batch:
            msg_query_one_file_update = MessageQueryOneUpdate.from_message(msg)
            os_supported = msg_query_one_file_update.op_system_supported
        
            file_info = defaultdict(lambda: {"linux": 0, "mac": 0, "windows": 0}, file_info)
            previous_state = file_info[client_id][os_supported]

            file_info[client_id][os_supported] += 1

            transaction_log += f"msg::{message.get_message_id()}|client::{client_id}|os::{os_supported}|prev::{previous_state}|actual::{previous_state + 1}\n"

        return transaction_log
    
    def recover_from_transaction_log(self):
        if not os.path.exists(self.path_logging):
            os.makedirs(os.path.dirname(self.path_logging), exist_ok=True)
            return

        file_info = self.get_file_info()

        print(f"File info antes de recuperarse: {file_info}")
            
        with open(self.path_logging, 'r') as file:
            for line in file.readlines():
                print(line)

                line = line.strip()

                
                data = line.split("|")

                msg_id = data[0].split("::")[1]
                client_id = data[1].split("::")[1]
                os_supported = data[2].split("::")[1]
                actual_state = data[4].split("::")[1]

                if not client_id in file_info.keys():
                    file_info[client_id] = {}

                file_info[client_id][os_supported] = actual_state
        
        self.update_results_in_disk(file_info)
        self.last_msg_id_log_transaction = msg_id
        


    