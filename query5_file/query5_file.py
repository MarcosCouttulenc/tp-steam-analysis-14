import csv
import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageQueryFiveFileUpdate
from common.message import MessageQueryFiveResult
from common.protocol import Protocol
from common.protocol import *
import multiprocessing
import socket
import errno       
from common.query_file_worker import QueryFile

class QueryFiveFile(QueryFile):
    def get_message_result_from_file_snapshot(self, client_id, file_snapshot):
        message_result = MessageQueryFiveResult(client_id, file_snapshot)
        return message_result

    def get_file_snapshot(self, client_id):
        file_snapshot = []

        percentil_90 = self.get_percentil_90()

        if percentil_90 == None:
            return file_snapshot

        for name, cant_reviews in sorted(self.totals.items(), key=lambda x: x[1][2], reverse=False):
            if cant_reviews[1] > percentil_90:
                file_snapshot.append((cant_reviews[2], name))
        
        return file_snapshot[:10]

    def update_results(self, message):
        msg_query_five_file_update = MessageQueryFiveFileUpdate.from_message(message)
        for (name, cant_pos, cant_neg,game_id) in msg_query_five_file_update.buffer:
            if name not in self.totals:
                self.totals[name] = [0, 0, int(game_id)]
                
            temp = self.totals[name]
            temp[0] += int(cant_pos)
            temp[1] += int(cant_neg)
            self.totals[name] = temp
    

    def get_percentil_90(self):
        if len(self.totals) == 0:
            return None

        neg_reviews = [neg for pos, neg, id in self.totals.values()]
        neg_reviews_sorted = sorted(neg_reviews)
        percentil_90_pos = int(0.90 * (len(neg_reviews_sorted) - 1))

        percentil_90 = neg_reviews_sorted[percentil_90_pos]
        return percentil_90


