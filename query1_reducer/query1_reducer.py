
import logging
logging.basicConfig(level=logging.CRITICAL)

from common.message import Message
from common.message import MessageQueryOneUpdate
from common.message import MessageQueryOneFileUpdate
from common.reducer_worker import ReducerWorker

BUFFER_MAX_SIZE = 50
CANT_EOFS_TIL_CLOSE = 3

class QueryOneReducer(ReducerWorker):
    def __init__(self, queue_name_origin, queues_name_destiny_str):
        super().__init__(queue_name_origin, queues_name_destiny_str)
        self.curr_cant = 0
        self.total_eofs = 0

    def handle_eof(self, ch, method, properties, message: Message):
        if message.is_eof():
            self.total_eofs += 1
            if  self.total_eofs >= CANT_EOFS_TIL_CLOSE:
                self.send_buffer_to_file(message.client_id)
                #push eof to query1_file
                self.running = False
                self.service_queues.ack(ch, method)
                self.service_queues.close_connection()
                return

    def update_buffer(self, message):
        self.curr_cant += 1
        msg_query_one_update = MessageQueryOneUpdate.from_message(message)

        if msg_query_one_update.op_system_supported not in self.buffer:
            self.buffer[msg_query_one_update.op_system_supported] = 0

        self.buffer[msg_query_one_update.op_system_supported] += 1

    def send_buffer_to_file(self,client_id):
        for queue_name in self.queues_name_destiny:
            msg = MessageQueryOneFileUpdate(
                client_id,self.buffer["linux"], self.buffer["mac"], self.buffer["windows"]
            )
            self.service_queues.push(queue_name, msg)
        
        self.buffer = self.init_buffer()
        self.curr_cant = 0

    def init_buffer(self):
        return {
            'linux': 0,
            'mac': 0,
            'windows': 0
        }
    
    def buffer_contains_items(self):
        return len(self.buffer) > 0

    def buffer_is_full(self):
        return self.curr_cant >= BUFFER_MAX_SIZE
    