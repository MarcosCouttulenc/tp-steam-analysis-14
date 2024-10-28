import csv
import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageQueryThreeFileUpdate
from common.message import MessageQueryThreeResult
from common.protocol import Protocol
from common.protocol import *
from common.query_file_worker import QueryFile

class QueryThreeFile(QueryFile):
    def get_message_result_from_file_snapshot(self, client_id, file_snapshot):
        message_result = MessageQueryThreeResult(client_id, file_snapshot)
        #logging.critical(f"TO SEND: {message_result.message_payload}")
        return message_result

    def get_file_snapshot(self, client_id):
        total_list = []
        for name, cant_reviews in self.totals.items():
            total_list.append((name, cant_reviews))

        
        total_list_sorted = sorted(total_list, key=lambda item: item[1], reverse=True)

        top_five = total_list_sorted[:5]
        #logging.critical(f"TOP FIVE TO SEND:")
        print(top_five)
        return top_five

    def update_results(self, message):
        #print(f"TO  UPDATE: {message.message_payload}")
        msg_query_three_file_update = MessageQueryThreeFileUpdate.from_message(message)
        for name, cant_reviews in msg_query_three_file_update.buffer:
            if not name in self.totals:
                self.totals[name] = 0
            self.totals[name] += int(cant_reviews)
        #print("AFTER UPDATE:")
        #print(self.totals)

