from common.message import Message


class Sharding():
    def __init__(self, cant_prox_nodes):
        self.cant_prox_nodes = cant_prox_nodes

    def calculate_shard(self, message: Message):
        return self.hash_function(message.message_id) % self.cant_prox_nodes

    def hash_function(self, message_id):
        return message_id
    
    