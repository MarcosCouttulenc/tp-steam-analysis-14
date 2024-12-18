
import logging
logging.basicConfig(level=logging.CRITICAL)

from common.message import Message
from common.message import MessageQueryOneUpdate
from common.message import MessageQueryOneFileUpdate
from common.reducer_worker import ReducerWorker
from middleware.queue import ServiceQueues

BUFFER_MAX_SIZE = 0
CANT_EOFS_TIL_CLOSE = 3
CHANNEL_NAME =  "rabbitmq"

#buffer:
# {"client_id": {"windows": int, "linux": int, "mac": int}}

class QueryOneReducer():
    def __init__(self, queue_name_origin, queues_name_destiny_str, ip_healthchecker, port_healthchecker):
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queues_name_destiny_str.split(",")
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        
        self.buffer = self.init_buffer()

        #super().__init__(queue_name_origin, queues_name_destiny_str)
        self.curr_cant = 0
        #self.total_eofs = 0
        self.total_eofs = {}
    
    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)
    
    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():

            self.handle_eof(ch, method, properties, message)
        
            return

        #print("Llego msj con data")
        self.update_buffer(message)

        if self.buffer_is_full():
            self.send_buffer_to_file(message.get_client_id())

        self.service_queues.ack(ch, method)

    def handle_eof(self, ch, method, properties, message: Message):

        client_id = str(message.get_client_id())
        if not client_id in self.total_eofs.keys():
            self.total_eofs[client_id] = 0
        self.total_eofs[client_id] += 1
        
    
        if self.total_eofs[client_id] >= CANT_EOFS_TIL_CLOSE:

            self.send_buffer_to_file(message.client_id)

            #Envio del eof al file. Chequear si va aca.
            for queue_name in self.queues_name_destiny:
                self.service_queues.push(queue_name, message)

            self.service_queues.ack(ch, method)

            return
        
        self.service_queues.ack(ch, method)

    def update_buffer(self, message: Message):
        self.curr_cant += 1
        client_id = str(message.get_client_id())
        msg_query_one_update = MessageQueryOneUpdate.from_message(message)

        if client_id not in self.buffer:
            self.buffer[client_id] = {'linux': 0, 'mac': 0, 'windows': 0}

        self.buffer[client_id][msg_query_one_update.op_system_supported] += 1



    def send_buffer_to_file(self,_client_id):
        for queue_name in self.queues_name_destiny:
            for client_id in self.buffer.keys():
                
                msg = MessageQueryOneFileUpdate(
                    "test", client_id, self.buffer[client_id]["linux"], self.buffer[client_id]["mac"], self.buffer[client_id]["windows"]
                )
                self.service_queues.push(queue_name, msg)
        
        self.buffer = self.init_buffer()
        self.curr_cant = 0

    def init_buffer(self):
        return {}
    
    def buffer_contains_items(self):
        return len(self.buffer) > 0

    def buffer_is_full(self):
        return self.curr_cant >= BUFFER_MAX_SIZE
    