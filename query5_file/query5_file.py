import csv
import logging
import os
logging.basicConfig(level=logging.CRITICAL)

from common.message import MessageReviewInfo
from common.message import MessageQueryFiveResult
from common.protocol import *
from common.message import Message, MessageBatch

from common.query_file_worker import QueryFile, MAX_LOG_LEN

class QueryFiveFile(QueryFile):
    def get_message_result_from_file_snapshot(self, client_id, file_snapshot):
        message_result = MessageQueryFiveResult(client_id, file_snapshot)
        return message_result


    def get_file_snapshot(self, client_id):
        return self.get_file_info(client_id)

    '''
    def get_file_snapshot(self, client_id):
        # Ahora la file snapshot va a ser de la forma: [[id, name, pos, neg], [id, name, pos, neg]]
        # y van a ser TODOS los juegos
        file_snapshot = []
        
        data = self.get_file_info(client_id)

        percentil_90 = self.get_percentil_90(data)

        for name, game_info in sorted(data.items(), key=lambda x: x[1][2], reverse=False):
            if game_info[1] > percentil_90:
                file_snapshot.append((game_info[2], name))

        return file_snapshot[:10]
    '''
    
    '''
    def get_percentil_90(self, data):
        if len(data) == 0:
            return None

        neg_reviews = [neg for pos, neg, id in data.values()]
        neg_reviews_sorted = sorted(neg_reviews)
        percentil_90_pos = int(0.90 * (len(neg_reviews_sorted) - 1))

        percentil_90 = neg_reviews_sorted[percentil_90_pos]
        return percentil_90
    '''

    def update_results(self, message):
        client_id = str(message.get_client_id())
        if self.log_transaction_len[client_id] < MAX_LOG_LEN:
            return
            
        self.update_results_from_log_transaction(client_id)
        

    def update_results_from_log_transaction(self, client_id):
        # comparar archivo actual con el de logs para saber si ya fue aplicado y se cayo.
        client_file_path = self.get_file_path_client(client_id)
        client_log_path = self.get_file_path_log_client(client_id)
        if self.verify_modification_time(client_log_path, client_file_path):
            # borramos el log
            # setear len de log en 0
            self.clean_log_transaction(client_id)
            return

        # traemos todos los logs
        # obtenemos datos del file del cliente
        # actualizamos datos con los logs en memoria.
        new_data = self.get_data_updated_with_transaction_log(client_id)

        if (new_data == None):
            return
        
        # escribimos el tmp del file del cliente completo (atomic_write)
        # lo impactamos en el file posta del cliente (atomic_write)
        self.update_results_in_disk(client_id, new_data)

        # borramos el log
        # setear len de log en 0
        self.clean_log_transaction(client_id)
        
    def get_file_info(self, client_id):
        client_file_path = self.get_file_path_client(client_id)

        games = {}

        try :
            with open(client_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    games[row['game']] = [int(row['cant_pos']), int(row['cant_neg']), int(row['game_id'])]
        except FileNotFoundError:
            pass

        return games

    def update_results_in_disk(self, client_id, games_info):
        client_file_path = self.get_file_path_client(client_id)

        with open(client_file_path, mode='w') as file:
            fieldnames = ['game', 'cant_pos', 'cant_neg', 'game_id']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for game, info in games_info.items():
                writer.writerow({'game': game, 'cant_pos': info[0], 'cant_neg': info[1], 'game_id': info[2]})
    

    def get_file_path_client(self, client_id):
        return f"{client_id}_{self.file_path}"

    def get_file_path_log_client(self, client_id):
        aux = self.path_logging
        return aux.replace(".txt", f'_{client_id}.txt')

    def verify_modification_time(self, file_a, file_b):
        # Devuelve True si el archivo A fue modificado después que el archivo B.
        try:
            mtime_a = os.path.getmtime(file_a)
            mtime_b = os.path.getmtime(file_b)
            return mtime_a > mtime_b
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return False



    ## Transaction Log
    ## --------------------------------------------------------------------------------
    def clean_log_transaction(self, client_id):
        self.log_transaction_len[client_id] = 0
        with open(self.get_file_path_log_client(client_id), "w") as _:
            pass

    def log_transaction(self, message: Message):
        client_id = str(message.get_client_id())
        transaction_log = self.get_transaction_log(message)
        self.atomic_append(transaction_log, self.get_file_path_log_client(client_id))
        self.last_msg_id_log_transaction = message.get_message_id()

        if not client_id in self.log_transaction_len.keys():
            self.log_transaction_len[client_id] = 0

        self.log_transaction_len[client_id] += 1

    def get_transaction_log(self, message):
        transaction_log = ""

        client_id = str(message.get_client_id())
        msg_batch = MessageBatch.from_message(message)

        for msg in msg_batch.batch:     
            msg_review_info = MessageReviewInfo.from_message(msg)
            game_name = msg_review_info.review.game_name
            log_action = "positive" if msg_review_info.review.is_positive() else "negative"
            transaction_log += f"msg::{message.get_message_id()}|client::{client_id}|game::{game_name}|game_id::{msg_review_info.review.game_id}|action::{log_action}\n"

        return transaction_log
        
    def get_data_updated_with_transaction_log(self, client_id):
        path_logging_client = self.get_file_path_log_client(client_id)

        if not os.path.exists(path_logging_client):
            os.makedirs(os.path.dirname(path_logging_client), exist_ok=True)
            return None
        
        #Obtengo la data que tiene actualmente ese cliente.
        file_info = self.get_file_info(client_id)
        
        #Leo el archivo de log y le impacto a file_info cada uno de los logs
        with open(path_logging_client, "r") as file:
            for line in file.readlines():
                data = line.strip().split("|")
                msg_id = data[0].split("::")[1]
                client_id = data[1].split("::")[1]
                game_name = data[2].split("::")[1]
                game_id = data[3].split("::")[1]
                log_action = data[4].split("::")[1]
        
                aux = []
                if not game_name in file_info.keys():
                    aux = [0, 0, game_id]
                else:
                    aux = file_info[game_name]
                
                if (log_action == "positive"):
                    aux[0] += 1
                else:
                    aux[1] += 1

                file_info[game_name] = aux
                self.last_msg_id_log_transaction = msg_id

        return file_info
        