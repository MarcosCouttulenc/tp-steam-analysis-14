import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageQueryOneUpdate
from common.message import MessageQueryOneFileUpdate

CHANNEL_NAME =  "rabbitmq"
BUFFER_MAX_SIZE = 50
CANT_EOFS_TIL_CLOSE = 3

class QueryOneReducer:
    def __init__(self, queue_name_origin, queues_name_destiny_str):
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queues_name_destiny_str.split(",")
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.totals = {}
        self.total_eofs = 0
    
    def pretty_str_totals(self):
        rta = "totals\n"
        for op_system_supported, total in self.totals.items():
            rta += f"[{op_system_supported} - {total}]\n"
        return rta
    
    def start(self):
        self.init_buffer()
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    
    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():
            self.total_eofs += 1
            print(f"ME LLEGO EOF numero: {self.total_eofs}")
            if  self.total_eofs >= CANT_EOFS_TIL_CLOSE:
                self.save_buffer_in_file_and_clean_it()
                self.running = False
                self.service_queues.ack(ch, method)
                self.service_queues.close_connection()
                return
        else:
            msg_query_one_update = MessageQueryOneUpdate.from_message(message)

            if msg_query_one_update.op_system_supported not in self.totals:
                self.totals[msg_query_one_update.op_system_supported] = 0

            self.totals[msg_query_one_update.op_system_supported] += 1

            if sum(self.totals.values()) >= BUFFER_MAX_SIZE:
                self.save_buffer_in_file_and_clean_it()

        self.service_queues.ack(ch, method)

    def save_buffer_in_file_and_clean_it(self):
        for queue_name in self.queues_name_destiny:
            msg = MessageQueryOneFileUpdate(
                self.totals["linux"], self.totals["mac"], self.totals["windows"]
            )
            self.service_queues.push(queue_name, msg)
        #guardar en archivo.
        self.init_buffer()

    def init_buffer(self):
        self.totals = {
            'linux': 0,
            'mac': 0,
            'windows': 0
        }