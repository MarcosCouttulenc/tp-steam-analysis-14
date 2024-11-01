import logging
logging.basicConfig(level=logging.CRITICAL)
import multiprocessing

from common.message import MessageGameInfo
from common.message import MessageQueryTwoFileUpdate
from common.reducer_worker import ReducerWorker

CHANNEL_NAME =  "rabbitmq"
BUFFER_MAX_SIZE = 0

#buffer:
#[(game_name, playtime)] ==> {"client_id": [(game_name, playtime)]}

class QueryTwoReducer(ReducerWorker):
    def update_buffer(self, message):
        msg_game_info = MessageGameInfo.from_message(message)
        client_id = str(msg_game_info.get_client_id())
        
        if client_id not in self.buffer:
            self.buffer[client_id] = []

        tmp = self.buffer[client_id]
        
        tmp.append((msg_game_info.game.name, msg_game_info.game.playTime))
        tmp.sort(key=lambda game_data: game_data[1], reverse=True)

        self.buffer[client_id] = tmp

    def send_buffer_to_file(self, _client_id, service_queues):
        for queue_name in self.queues_name_destiny:
            for client_id in self.buffer.keys():

                msg = MessageQueryTwoFileUpdate(client_id,self.buffer[client_id])
                service_queues.push(queue_name, msg)
        
        self.buffer = self.init_buffer()
    
    def init_buffer(self):
        manager = multiprocessing.Manager()
        return manager.dict()
    
    def buffer_contains_items(self):
        return len(self.buffer) > 0

    def buffer_is_full(self):
        return len(self.buffer) >= BUFFER_MAX_SIZE