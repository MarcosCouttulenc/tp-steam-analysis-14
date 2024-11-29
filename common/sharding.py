
def calculate_shard(self, id, cant_prox_nodes):
        return id % cant_prox_nodes

class Sharding():
    def __init__(self, cant_prox_nodes):
        self.cant_prox_nodes = cant_prox_nodes

    def calculate_shard(self, id):
        return id % self.cant_prox_nodes

    # def hash_function(self, message_id):
    #     return message_id
    
    