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

from common.review_worker import  ReviewWorker

CHANNEL_NAME =  "rabbitmq"

class WorkerReviewValidator(ReviewWorker):
    def __init__(self, queue_name_origin_eof, queue_name_origin, queues_name_destiny, cant_next, cant_slaves, is_master, ip_master, 
                 port_master, db_games_ip, db_games_port):
        
        super().__init__(queue_name_origin_eof, queue_name_origin, queues_name_destiny, cant_next, cant_slaves, is_master, ip_master, port_master)
        self.db_games_ip = db_games_ip
        self.db_games_port = db_games_port
        self.service_queues = ServiceQueues(CHANNEL_NAME)

    def validate_review(self, _review):
        return True
    
    def forward_message(self, message):
        messageRI = MessageReviewInfo.from_message(message)
        game = self.get_game_from_db(message.get_client_id(), messageRI.review.game_id)

        if game.id == "-1":
            return

        messageRI.review.set_genre(game.genre)
        message_to_push = MessageReviewInfo(message.get_client_id(), messageRI.review)
        
        for queue_name_destiny in self.queues_destiny.keys():
            self.service_queues.push(queue_name_destiny, message_to_push)

    def get_game_from_db(self, client_id, game_id) -> Game:
        db_games = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        db_games.connect((self.db_games_ip, self.db_games_port))

        protocol_db_games = Protocol(db_games)
        msg_query_game = MessageQueryGameDatabase(client_id, game_id)
        protocol_db_games.send(msg_query_game)

        msg = protocol_db_games.receive()
        msg_game_info = MessageGameInfo.from_message(msg)

        db_games.close()
        
        return msg_game_info.game


