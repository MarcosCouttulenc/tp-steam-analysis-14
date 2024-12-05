import csv
import logging
import os
logging.basicConfig(level=logging.CRITICAL)

from common.message import MessageReviewInfo
from common.message import MessageQueryFiveResult
from common.protocol import *

from common.query_file_worker import QueryFile

class QueryFiveFile(QueryFile):
    def get_message_result_from_file_snapshot(self, client_id, file_snapshot):
        message_result = MessageQueryFiveResult(client_id, file_snapshot)
        return message_result

    def get_file_snapshot(self, client_id):
        file_snapshot = []
        
        data = self.get_file_info(client_id)

        percentil_90 = self.get_percentil_90(data)

        for name, game_info in sorted(data.items(), key=lambda x: x[1][2], reverse=False):
            if game_info[1] > percentil_90:
                file_snapshot.append((game_info[2], name))

        return file_snapshot[:10]
    
    def update_results(self, message):
        msg_review_info = MessageReviewInfo.from_message(message)
        client_id = str(msg_review_info.get_client_id())

        data = self.get_file_info(client_id)

        if not msg_review_info.review.game_name in data:
            data[msg_review_info.review.game_name] = [0, 0, msg_review_info.review.game_id]

        if msg_review_info.review.is_positive():
            data[msg_review_info.review.game_name][0] += 1
        else:
            data[msg_review_info.review.game_name][1] += 1

        self.update_results_in_disk(client_id, data)
    

    def get_percentil_90(self, data):
        if len(data) == 0:
            return None

        neg_reviews = [neg for pos, neg, id in data.values()]
        neg_reviews_sorted = sorted(neg_reviews)
        percentil_90_pos = int(0.90 * (len(neg_reviews_sorted) - 1))

        percentil_90 = neg_reviews_sorted[percentil_90_pos]
        return percentil_90

        
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



    ## Transaction Log
    ## --------------------------------------------------------------------------------
    def get_transaction_log(self, message):
        msg_review_info = MessageReviewInfo.from_message(message)
        client_id = str(msg_review_info.get_client_id())
        file_info = self.get_file_info(client_id)
        game_name = msg_review_info.review.game_name

        if game_name in file_info.keys():
            values = file_info[game_name] 
        else:
            values = [0,0,0]
        
        new_values = values

        if msg_review_info.review.is_positive():
            new_values[0] += 1
        else:
            new_values[1] += 1
    
        transaction_log = f"msg::{message.get_message_id()}|client::{client_id}|game::{game_name}|game_id::{msg_review_info.review.game_id}|prev::{values[0]}%!{values[1]}|actual::{new_values[0]}%!{new_values[1]}"
        return transaction_log 

        
    def recover_from_transaction_log(self):
        if not os.path.exists(self.path_logging):
            os.makedirs(os.path.dirname(self.path_logging), exist_ok=True)
            return
        
        print("Empieza recuperacion del log \n")
        with open(self.path_logging, 'r') as file:
            line = file.readline().strip()

            print(f"Nos levantamos y el log tiene: {line}")

            data = line.split("|")

            msg_id = data[0].split("::")[1]
            client_id = data[1].split("::")[1]
            game_name = data[2].split("::")[1]
            game_id = data[3].split("::")[1]
            previous_state = data[4].split("::")[1]
            actual_state = data[5].split("::")[1]

        file_info = self.get_file_info(client_id)

        to_print = "No estaba en el dict"
        if game_name in file_info.keys():
            to_print = file_info[game_name]
        print(f"Antes de recuperar: {to_print}")
        
        aux = []
        if not game_name in file_info.keys():
            aux = [0, 0, game_id]
        else:
            aux = file_info[game_name]

        pos_neg = actual_state.split("%!")

        aux[0] = pos_neg[0]
        aux[1] = pos_neg[1]

        file_info[game_name] = aux

        self.last_msg_id_log_transaction = msg_id
        self.update_results_in_disk(client_id, file_info)
        