import csv
import logging
logging.basicConfig(level=logging.CRITICAL)

from common.message import MessageReviewInfo
from common.message import MessageQueryThreeResult
from common.protocol import *
from common.query_file_worker import QueryFile

class QueryThreeFile(QueryFile):
    def get_message_result_from_file_snapshot(self, client_id, file_snapshot):
        message_result = MessageQueryThreeResult(client_id, file_snapshot)
        return message_result


    def get_file_snapshot(self, client_id):
        total_list = []
        client_file_path = self.get_file_path_client(client_id)
        
        try:
            with open(client_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    total_list.append((row['game'], int(row['cant_positive'])))
        except FileNotFoundError:
            pass

        total_list_sorted = sorted(total_list, key=lambda item: item[1], reverse=True)

        if (len(total_list_sorted) > 5):
            return total_list_sorted[:5]

        return total_list_sorted


    def update_results(self, message):
        msg_review_info = MessageReviewInfo.from_message(message)

        if not msg_review_info.review.is_positive():
            return

            
        client_id = str(msg_review_info.get_client_id())

        client_file_path = self.get_file_path_client(client_id)

        games = {}
        try :
            with open(client_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    games[row['game']] = int(row['cant_positive'])
        except FileNotFoundError:
            pass
        
        if not msg_review_info.review.game_name in games:
            games[msg_review_info.review.game_name] = 0

        games[msg_review_info.review.game_name] += 1

        with open(client_file_path, mode='w') as file:
            fieldnames = ['game', 'cant_positive']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for game, cant_positive in games.items():
                writer.writerow({'game': game, 'cant_positive': cant_positive})


    def get_file_path_client(self, client_id):
        return f"{client_id}_{self.file_path}"
