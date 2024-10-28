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
        games_with_more_5000_positive_reviews = []

        for name, cant_reviews in self.totals.items():
            if (cant_reviews > 5000):
                games_with_more_5000_positive_reviews.append((name, cant_reviews))
            
        return games_with_more_5000_positive_reviews

    def update_results(self, message):
        msg_query_four_file_update = MessageQueryFourFileUpdate.from_message(message)
        for name, cant_reviews in msg_query_four_file_update.buffer:
            if not name in self.totals:
                self.totals[name] = 0

            self.totals[name] += int(cant_reviews)


