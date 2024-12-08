import csv
import logging
import os
logging.basicConfig(level=logging.CRITICAL)

from common.message import MessageReviewInfo
from common.message import MessageQueryFourResult
from common.protocol import *
from common.query_file_worker import QueryFile

MIN_REVIWS = 5000

class QueryFourFile(QueryFile):
    def get_message_result_from_file_snapshot(self, client_id, file_snapshot):
        message_result = MessageQueryFourResult(client_id, file_snapshot)
        return message_result

    def get_file_snapshot(self, client_id):
        games_with_more_positive_reviews = []
        client_file_path = self.get_file_path_client(client_id)
        
        try:
            with open(client_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    cant_reviws = int(row['cant_reviews'])
                    if (cant_reviws > MIN_REVIWS):
                        games_with_more_positive_reviews.append((row['game'], cant_reviws))
        except FileNotFoundError:
            pass

        return games_with_more_positive_reviews
    
    def update_results(self, message):
        msg_review_info = MessageReviewInfo.from_message(message)
        client_id = str(msg_review_info.get_client_id())

        games = self.get_file_info(client_id)
        if not msg_review_info.review.game_name in games:
            games[msg_review_info.review.game_name] = 0

        games[msg_review_info.review.game_name] += 1

        self.update_results_in_disk(client_id, games)


    def get_file_info(self, client_id):
        client_file_path = self.get_file_path_client(client_id)

        games = {}
        try :
            with open(client_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    games[row['game']] = int(row['cant_reviews'])
        except FileNotFoundError:
            pass
        
        return games

    def update_results_in_disk(self, client_id, games_info):
        client_file_path = self.get_file_path_client(client_id)

        with open(client_file_path, mode='w') as file:
            fieldnames = ['game', 'cant_reviews']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for game, cant_reviews in games_info.items():
                writer.writerow({'game': game, 'cant_reviews': cant_reviews})


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
            cant_reviews = file_info[game_name] 
        else:
            cant_reviews = 0
    
        transaction_log = f"msg::{message.get_message_id()}|client::{client_id}|game::{game_name}|prev::{cant_reviews}|actual::{cant_reviews+1}"
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
            previous_state = data[3].split("::")[1]
            actual_state = data[4].split("::")[1]

        file_info = self.get_file_info(client_id)

        to_print = "No estaba en el dict"
        if game_name in file_info.keys():
            to_print = file_info[game_name]
        print(f"Antes de recuperar: {to_print}")
        
        file_info[game_name] = actual_state

        self.last_msg_id_log_transaction = msg_id
        self.update_results_in_disk(client_id, file_info)