import logging
logging.basicConfig(level=logging.CRITICAL)
import socket

from middleware.queue import ServiceQueues
from common.protocol import Protocol
from common.model.game import Game
from common.message import MessageGameInfo
from common.message import MessageQueryGameDatabase
from common.message import MessageReviewInfo
from common.message import *
from common.sharding import Sharding

from common.review_worker import  ReviewWorker

CHANNEL_NAME =  "rabbitmq"

class WorkerReviewValidator(ReviewWorker):
    def __init__(self, queue_name_origin_eof, queue_name_origin, queues_name_destiny, cant_next, cant_slaves, is_master, ip_master, 
                 port_master, db_games_ip, db_games_port, ip_healthchecker, port_healthchecker, id, path_status_info):
        
        super().__init__(queue_name_origin_eof, queue_name_origin, queues_name_destiny, cant_next, cant_slaves, is_master, ip_master, 
                         port_master, ip_healthchecker, port_healthchecker, id, path_status_info)
        self.db_games_ip = db_games_ip
        self.db_games_port = db_games_port
        self.service_queues = ServiceQueues(CHANNEL_NAME)

    def validate_review(self, _review):
        return True
    
    def forward_message(self, message):
        messageRI = MessageReviewInfo.from_message(message)
        print("Envio consulta a la bdd")
        game = self.get_game_from_db(message.get_client_id(), messageRI.review.game_id)
        print(f"Me devolvio la bdd: {game.name}")

        if game.id == "-1":
            print(f"No encontre el juego")
            return

        messageRI.review.set_genre(game.genre)
        message_to_push = MessageReviewInfo(message.message_id, message.get_client_id(), messageRI.review)

        for queue_name_next, cant_queue_next in self.queues_destiny.items():
            queue_next_id = Sharding.calculate_shard(messageRI.review.game_id, cant_queue_next)
            queue_name_destiny = f"{queue_name_next}-{str(queue_next_id)}"
            self.service_queues.push(queue_name_destiny, message_to_push)
            

    def get_game_from_db(self, client_id, game_id) -> Game:
        db_games = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        db_games.connect((self.db_games_ip, self.db_games_port))

        protocol_db_games = Protocol(db_games)
        message_id = f"C_{str(client_id)}_QUERY_{str(game_id)}"
        msg_query_game = MessageQueryGameDatabase(message_id, client_id, game_id)
        protocol_db_games.send(msg_query_game)

        msg = protocol_db_games.receive()
        msg_game_info = MessageGameInfo.from_message(msg)

        db_games.close()
        
        return msg_game_info.game


