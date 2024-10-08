import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageQueryOneUpdate

CHANNEL_NAME =  "rabbitmq"
BUFFER_MAX_SIZE = 1000

class QueryOneReducer:
    def __init__(self, queue_name_origin):
        self.queue_name_origin = queue_name_origin
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.totals = {}
    
    def pretty_str_totals(self):
        rta = "totals\n"
        for op_system_supported, total in self.totals.items():
            rta += f"[{op_system_supported} - {total}]\n"
        return rta
    
    def start(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    
    def process_message(self, ch, method, properties, message: Message):
        msg_query_one_update = MessageQueryOneUpdate.from_message(message)
        
        logging.critical(msg_query_one_update.op_system_supported)

        if msg_query_one_update.op_system_supported not in self.totals:
            self.totals[msg_query_one_update.op_system_supported] = 0

        self.totals[msg_query_one_update.op_system_supported] += 1

        logging.critical(self.pretty_str_totals())

        if sum(self.totals.values()) >= BUFFER_MAX_SIZE:
            self.save_buffer_in_file_and_clean_it()

        self.service_queues.ack(ch, method)

    def save_buffer_in_file_and_clean_it(self):
        #guardar en archivo.
        self.totals = {}