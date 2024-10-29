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
        client_id = str(client_id)
        if client_id not in self.totals:
            print("NO HAY NADA")
            return []

        total_list = []
        for name, cant_reviews in self.totals[client_id].items():
            total_list.append((name, cant_reviews))

        total_list_sorted = sorted(total_list, key=lambda item: item[1], reverse=True)

        top_five = total_list_sorted[:5]
        print(top_five)

        return top_five

    def update_results(self, message):
        msg_query_three_file_update = MessageQueryThreeFileUpdate.from_message(message)
        client_id = str(msg_query_three_file_update.get_client_id())

        if not client_id in self.totals:
            self.totals[client_id] = {}
        
        #print("A ACTUALIZAR:")
        #print(msg_query_three_file_update.buffer)

        #print("ANTES DE ACTUALIZAR:")
        #print(self.totals)

        dict = self.totals[client_id]

        for name, cant_reviews in msg_query_three_file_update.buffer:
            if not name in dict:
                dict[name] = 0
            dict[name] += int(cant_reviews)
        
        self.totals[client_id] = dict

        #print("DESPUES DE ACTUALIZAR:")
        #print(self.totals)

