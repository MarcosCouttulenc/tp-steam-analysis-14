import csv
import logging
import os
logging.basicConfig(level=logging.CRITICAL)

from common.message import MessageGameInfo
from common.message import MessageQueryTwoResult
from common.message import MessageGameInfo, MessageBatch
from common.protocol import *
from common.query_file_worker import QueryFile

TOP_NUMBER = 10

class QueryTwoFile(QueryFile):

    def __init__(self, queue_name_origin, file_path, result_query_port, listen_backlog, ip_healthchecker, port_healthchecker, path_status_info, listen_to_result_responser_port, id):
        super().__init__(queue_name_origin, file_path, result_query_port, listen_backlog, ip_healthchecker, port_healthchecker, path_status_info, listen_to_result_responser_port, id)
        self.clients_file_paths = []

    def get_message_result_from_file_snapshot(self, client_id, file_snapshot):
        message_result = MessageQueryTwoResult(client_id, file_snapshot)
        return message_result

    def get_file_snapshot(self, client_id):
        top_ten = []
        client_file_path = self.get_file_path_client(client_id)
        
        try:
            with open(client_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    top_ten.append((row['game'], row['playTime']))
            return top_ten
        except FileNotFoundError:
            pass
        return top_ten

    def update_results(self, message):
        client_id = str(message.get_client_id())
        top_games = self.get_file_info(client_id)
        msg_batch = MessageBatch.from_message(message)

        for msg in msg_batch.batch:
            msg_game_info = MessageGameInfo.from_message(msg)
            client_id = str(msg_game_info.get_client_id())
            top_games.append((msg_game_info.game.name, msg_game_info.game.playTime))

        self.update_results_in_disk(client_id, top_games)
    
    def get_file_info(self, client_id):
        client_file_path = self.get_file_path_client(client_id)

        top_games = []
        try :
            with open(client_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    top_games.append((row['game'], row['playTime']))
        except FileNotFoundError:
            pass
        
        return top_games

    def update_results_in_disk(self, client_id, top_games):
        client_file_path = self.get_file_path_client(client_id)
        new_top_ten = self.get_top_games_sorted(top_games)

        with open(client_file_path, mode='w') as file:
            fieldnames = ['game', 'playTime']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for game, playTime in new_top_ten:
                writer.writerow({'game': game, 'playTime': playTime})

    def get_top_games_sorted(self, top_games):
        new_doc_sorted = sorted(top_games, key=lambda game_data: int(game_data[1]), reverse=True)
        return new_doc_sorted[:TOP_NUMBER]


    def get_file_path_client(self, client_id):
        return f"{client_id}_{self.file_path}"
    

    ## Transaction Log
    ## --------------------------------------------------------------------------------
    def get_transaction_log(self, message):
        transaction_log = ""

        client_id = str(message.get_client_id())
        file_info = self.get_file_info(client_id)
        msg_batch = MessageBatch.from_message(message)

        for msg in msg_batch.batch:
            msg_game_info = MessageGameInfo.from_message(msg)
            client_id = str(msg_game_info.get_client_id())
            file_info.append((msg_game_info.game.name, msg_game_info.game.playTime))
            
            file_info_new = self.get_top_games_sorted(file_info)
            file_info_new_data = self.get_top_to_string(file_info_new)

            transaction_log += f"msg::{message.get_message_id()}|client::{client_id}|actual::{file_info_new_data}\n"

        return transaction_log 
    
    def get_top_to_string(self, top):
        top_list = []
        for game, playTime in top:
            top_list.append(f"{game}%!{playTime}")
        top_data = "%$".join(top_list)
        return top_data
    
    def get_top_from_string(self, top_data_string):
        top_data = top_data_string.split("%$")
        top_list = []
        for game_data in top_data:
            game_name_playTime = game_data.split("%!")
            top_list.append((game_name_playTime[0], game_name_playTime[1]))
        return top_list
    
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
            actual_state = data[2].split("::")[1]

        file_info = self.get_file_info(client_id)

        print(f"Antes de recuperar: {file_info}")

        actual_file_info = self.get_top_from_string(actual_state)
        
        self.last_msg_id_log_transaction = msg_id
        self.update_results_in_disk(client_id, actual_file_info)

        file_info_then = self.get_file_info(client_id)

        print(f"Last transaction log id: {msg_id}\n")
        print(f"Luego de ejecutar recuperacion: {file_info_then}")