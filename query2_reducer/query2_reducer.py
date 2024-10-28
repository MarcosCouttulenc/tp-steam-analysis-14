import logging
logging.basicConfig(level=logging.CRITICAL)

from common.message import MessageGameInfo
from common.message import MessageQueryTwoFileUpdate
from common.reducer_worker import ReducerWorker

CHANNEL_NAME =  "rabbitmq"
BUFFER_MAX_SIZE = 0

class QueryTwoReducer(ReducerWorker):
    def update_buffer(self, message):
        msg_game_info = MessageGameInfo.from_message(message)
        self.buffer.append((msg_game_info.game.name, msg_game_info.game.playTime))
        self.buffer.sort(key=lambda game_data: game_data[1], reverse=True)

    def send_buffer_to_file(self,client_id):
        for queue_name in self.queues_name_destiny:
            msg = MessageQueryTwoFileUpdate(client_id,self.buffer)
            self.service_queues.push(queue_name, msg)
        
        self.buffer = []
    
    def init_buffer(self):
        return []
    
    def buffer_contains_items(self):
        return len(self.buffer) > 0

    def buffer_is_full(self):
        return len(self.buffer) >= BUFFER_MAX_SIZE