import logging
logging.basicConfig(level=logging.CRITICAL)
import multiprocessing

from common.message import MessageReviewInfo
from common.message import MessageQueryFourFileUpdate
from common.reducer_worker import ReducerWorker

BUFFER_MAX_SIZE = 50

class QueryFourReducer(ReducerWorker):
    def __init__(self, queue_name_origin_eof, queue_name_origin,queues_name_destiny, cant_slaves, is_master, ip_master, port_master, ip_healthchecker, port_healthchecker):
        super().__init__(queue_name_origin_eof, queue_name_origin,queues_name_destiny, cant_slaves, is_master, ip_master, port_master, ip_healthchecker, port_healthchecker)
        self.curr_cant = 0

    def update_buffer(self, message):
        msg_review_info = MessageReviewInfo.from_message(message)
         
        self.curr_cant += 1

        #guardo en el buffer dict o actualizo si ya estaba la clave: (name, cant_reseñas_positivas)
        client_id = msg_review_info.get_client_id()
        if client_id not in self.buffer:
            self.buffer[client_id] = {}

        tmp = self.buffer[client_id]

        if not msg_review_info.review.game_name in tmp:
            tmp[msg_review_info.review.game_name] = 0

        tmp[msg_review_info.review.game_name] += 1

        self.buffer[client_id] = tmp


    def send_buffer_to_file(self, client_id, service_queues):
        for queue_name in self.queues_name_destiny:
            for client_id in self.buffer.keys():
                list_of_tuples = self.buffer_to_list_of_tuples(client_id)
                msg = MessageQueryFourFileUpdate("test", client_id,list_of_tuples)
                service_queues.push(queue_name, msg)
        
        self.buffer = self.init_buffer()
        self.curr_cant = 0

    def init_buffer(self):
        manager = multiprocessing.Manager()
        return manager.dict()
    
    def buffer_contains_items(self):
        return len(self.buffer) > 0

    def buffer_is_full(self):
        return self.curr_cant >= BUFFER_MAX_SIZE
    
    def buffer_to_list_of_tuples(self, client_id):
        rta = []
        for name, cant_reviews in self.buffer[client_id].items():
            rta.append((name, cant_reviews))
        return rta