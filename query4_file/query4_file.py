import csv
import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageQueryFourFileUpdate
from common.message import MessageQueryFourResult
from common.protocol import Protocol
from common.protocol import *
from common.query_file_worker import QueryFile

class QueryFourFile(QueryFile):
    def get_message_result_from_file_snapshot(self, client_id, file_snapshot):
        message_result = MessageQueryFourResult(client_id, file_snapshot)
        return message_result

    def get_file_snapshot(self, client_id):
        client_id = str(client_id)
        if client_id not in self.totals:
            return []
        
        games_with_more_5000_positive_reviews = []

        for name, cant_reviews in self.totals[client_id].items():
            if (cant_reviews > 5000):
                games_with_more_5000_positive_reviews.append((name, cant_reviews))
            
        return games_with_more_5000_positive_reviews

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


