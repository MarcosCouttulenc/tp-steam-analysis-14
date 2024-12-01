import csv
import logging
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


        '''

        client_id = str(client_id)
        if client_id not in self.totals:
            return []
        
        games_with_more_5000_positive_reviews = []

        for name, cant_reviews in self.totals[client_id].items():
            if (cant_reviews > 5000):
                games_with_more_5000_positive_reviews.append((name, cant_reviews))
            
        return games_with_more_5000_positive_reviews

        '''

    '''
    def update_results(self, message):
        msg_query_four_file_update = MessageQueryFourFileUpdate.from_message(message)
        client_id = str(msg_query_four_file_update.get_client_id())

        if not client_id in self.totals:
            self.totals[client_id] = {}
        
        dict = self.totals[client_id]

        for name, cant_reviews in msg_query_four_file_update.buffer:
            if not name in dict:
                dict[name] = 0

            dict[name] += int(cant_reviews)
        
        self.totals[client_id] = dict
    '''

    def update_results(self, message):
        msg_review_info = MessageReviewInfo.from_message(message)
        client_id = str(msg_review_info.get_client_id())
        client_file_path = self.get_file_path_client(client_id)

        games = {}
        try :
            with open(client_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    games[row['game']] = int(row['cant_reviews'])
        except FileNotFoundError:
            pass
        
        if not msg_review_info.review.game_name in games:
            games[msg_review_info.review.game_name] = 0

        games[msg_review_info.review.game_name] += 1

        with open(client_file_path, mode='w') as file:
            fieldnames = ['game', 'cant_reviews']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for game, cant_reviews in games.items():
                writer.writerow({'game': game, 'cant_reviews': cant_reviews})


    def get_file_path_client(self, client_id):
        return f"{client_id}_{self.file_path}"

