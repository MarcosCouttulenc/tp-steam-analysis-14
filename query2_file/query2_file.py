import csv
import logging
logging.basicConfig(level=logging.CRITICAL)

from common.message import MessageQueryTwoFileUpdate
from common.message import MessageQueryTwoResult
from common.protocol import *
from common.query_file_worker import QueryFile

class QueryTwoFile(QueryFile):

    def __init__(self, queue_name_origin, file_path, result_query_port, listen_backlog, ip_healthchecker, port_healthchecker):
        super().__init__(queue_name_origin, file_path, result_query_port, listen_backlog, ip_healthchecker, port_healthchecker)
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
        msg_query_two_file_update = MessageQueryTwoFileUpdate.from_message(message)
        client_id = str(msg_query_two_file_update.get_client_id())

        client_file_path = self.get_file_path_client(client_id)

        old_top_ten = []
        try :
            with open(client_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    old_top_ten.append((row['game'], row['playTime']))
        except FileNotFoundError:
            pass
        
        new_doc = (old_top_ten + msg_query_two_file_update.top_ten_buffer)

        new_doc_sorted = sorted(new_doc, key=lambda game_data: int(game_data[1]), reverse=True)

        new_top_ten = new_doc_sorted[:10]

        with open(client_file_path, mode='w') as file:
            fieldnames = ['game', 'playTime']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for game, playTime in new_top_ten:
                writer.writerow({'game': game, 'playTime': playTime})

    def get_file_path_client(self, client_id):
        return f"{client_id}_{self.file_path}"