import logging
logging.basicConfig(level=logging.CRITICAL)

from common.message import MessageReviewInfo
from common.message import MessageQueryThreeFileUpdate
from common.reducer_worker import ReducerWorker

CHANNEL_NAME =  "rabbitmq"
BUFFER_MAX_SIZE = 50

#buffer:
# {"game_name": cant_reseñas_pos} ==> {"client_id": {"game_name": cant_reseñas_pos}}

class QueryThreeReducer(ReducerWorker):
    def __init__(self, queue_name_origin, queues_name_destiny_str):
        super().__init__(queue_name_origin, queues_name_destiny_str)
        self.curr_cant = 0
        

    def update_buffer(self, message):
        msg_review_info = MessageReviewInfo.from_message(message)
        
         #guardo en el buffer dict o actualizo si ya estaba la clave: (name, cant_reseñas_positivas)
        if msg_review_info.review.is_positive():
            self.curr_cant += 1
            client_id = str(msg_review_info.get_client_id())
            
            if client_id not in self.buffer:
                self.buffer[client_id] = {}

            if not msg_review_info.review.game_name in self.buffer[client_id]:
                self.buffer[client_id][msg_review_info.review.game_name] = 0
                
            self.buffer[client_id][msg_review_info.review.game_name] += 1


    def send_buffer_to_file(self, client_id):
        for queue_name in self.queues_name_destiny:
            for client_id in self.buffer.keys():

                list_of_tuples = self.buffer_to_list_of_tuples(client_id)
                msg = MessageQueryThreeFileUpdate(client_id, list_of_tuples)
                self.service_queues.push(queue_name, msg)
        
        self.buffer = {}
        self.curr_cant = 0
    
    def init_buffer(self):
        return {}
    
    def buffer_contains_items(self):
        return len(self.buffer) > 0

    def buffer_is_full(self):
        return self.curr_cant >= BUFFER_MAX_SIZE
    
    def buffer_to_list_of_tuples(self, client_id):
        rta = []
        for name, cant_reviews in self.buffer[client_id].items():
            rta.append((name, cant_reviews))
        return rta



