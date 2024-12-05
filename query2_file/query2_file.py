import csv
import logging
logging.basicConfig(level=logging.CRITICAL)

from common.message import MessageGameInfo
from common.message import MessageQueryTwoResult
from common.protocol import *
from common.query_file_worker import QueryFile

TOP_NUMBER = 10

class QueryTwoFile(QueryFile):

    def __init__(self, queue_name_origin, file_path, result_query_port, listen_backlog, ip_healthchecker, port_healthchecker, path_status_info):
        super().__init__(queue_name_origin, file_path, result_query_port, listen_backlog, ip_healthchecker, port_healthchecker, path_status_info)
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
        msg_game_info = MessageGameInfo.from_message(message)
        client_id = str(msg_game_info.get_client_id())

        client_file_path = self.get_file_path_client(client_id)

        top_games = []
        try :
            with open(client_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    top_games.append((row['game'], row['playTime']))
        except FileNotFoundError:
            pass

        top_games.append((msg_game_info.game.name, msg_game_info.game.playTime))
        new_doc_sorted = sorted(top_games, key=lambda game_data: int(game_data[1]), reverse=True)
        new_top_ten = new_doc_sorted[:TOP_NUMBER]

        with open(client_file_path, mode='w') as file:
            fieldnames = ['game', 'playTime']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for game, playTime in new_top_ten:
                writer.writerow({'game': game, 'playTime': playTime})

    def get_file_path_client(self, client_id):
        return f"{client_id}_{self.file_path}"