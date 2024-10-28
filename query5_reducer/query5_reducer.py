import logging
logging.basicConfig(level=logging.CRITICAL)

from common.message import MessageReviewInfo
from common.message import MessageQueryFiveFileUpdate
from common.reducer_worker import ReducerWorker

BUFFER_MAX_SIZE = 50

class QueryFiveReducer(ReducerWorker):
    def __init__(self, queue_name_origin, queues_name_destiny_str):
        super().__init__(queue_name_origin, queues_name_destiny_str)
        self.curr_cant = 0
        

    def update_buffer(self, message):
        self.curr_cant += 1
        msg_review_info = MessageReviewInfo.from_message(message)

        #guardo en el buffer dict o actualizo si ya estaba la clave: (name, (cant_reseñas_positivas, cant_reseñas_negativas))
        if not msg_review_info.review.game_name in self.buffer:
            self.buffer[msg_review_info.review.game_name] = [0, 0, msg_review_info.review.game_id]
        
        if msg_review_info.review.is_positive():
            self.buffer[msg_review_info.review.game_name][0] += 1
        else:
            self.buffer[msg_review_info.review.game_name][1] += 1



    def send_buffer_to_file(self, client_id):
        for queue_name in self.queues_name_destiny:
            list_of_tuples = self.buffer_to_list_of_tuples()
            msg = MessageQueryFiveFileUpdate(client_id, list_of_tuples)
            self.service_queues.push(queue_name, msg)
        
        self.buffer = {}
        self.curr_cant = 0

    def init_buffer(self):
        return {}
    
    def buffer_contains_items(self):
        return len(self.buffer) > 0

    def buffer_is_full(self):
        return self.curr_cant >= BUFFER_MAX_SIZE
    
    def buffer_to_list_of_tuples(self):
        rta = []
        for name, cant_reviews in self.buffer.items():
            rta.append((name, cant_reviews[0], cant_reviews[1], cant_reviews[2]))
        return rta