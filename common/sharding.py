from random import randint, seed
class Sharding:

    @classmethod
    def calculate_shard(cls, id, cant_prox_nodes):
        seed(int(id))
        return randint(1, cant_prox_nodes)