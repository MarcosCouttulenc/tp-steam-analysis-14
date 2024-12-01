import csv
import logging
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
        client_file_path = self.get_file_path_client(client_id)
        
        data = self.get_data_from_file(client_file_path)

        percentil_90 = self.get_percentil_90(data)

        for name, cant_reviews in sorted(data.items(), key=lambda x: x[1][2], reverse=False):
            if cant_reviews[1] > percentil_90:
                file_snapshot.append((cant_reviews[2], name))

        return file_snapshot[:10]
    
    def update_results(self, message):
        msg_review_info = MessageReviewInfo.from_message(message)
        client_id = str(msg_review_info.get_client_id())
        client_file_path = self.get_file_path_client(client_id)

        data = self.get_data_from_file(client_file_path)

        if not msg_review_info.review.game_name in data:
            data[msg_review_info.review.game_name] = [0, 0, msg_review_info.review.game_id]

        if msg_review_info.review.is_positive():
            data[msg_review_info.review.game_name][0] += 1
        else:
            data[msg_review_info.review.game_name][1] += 1

        with open(client_file_path, mode='w') as file:
            fieldnames = ['game', 'cant_pos', 'cant_neg', 'game_id']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for game, cant_reviews in data.items():
                writer.writerow({'game': game, 'cant_pos': cant_reviews[0], 'cant_neg': cant_reviews[1], 'game_id': cant_reviews[2]})
    

    def get_percentil_90(self, data):
        if len(data) == 0:
            return None

        neg_reviews = [neg for pos, neg, id in data.values()]
        neg_reviews_sorted = sorted(neg_reviews)
        percentil_90_pos = int(0.90 * (len(neg_reviews_sorted) - 1))

        percentil_90 = neg_reviews_sorted[percentil_90_pos]
        return percentil_90

    def get_data_from_file(self, client_file_path):
        data = {}

        try :
            with open(client_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data[row['game']] = [int(row['cant_pos']), int(row['cant_neg']), int(row['game_id'])]
        except FileNotFoundError:
            pass

        return data
    

    def get_file_path_client(self, client_id):
        return f"{client_id}_{self.file_path}"

