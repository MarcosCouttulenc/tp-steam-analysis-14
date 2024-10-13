import logging
logging.basicConfig(level=logging.CRITICAL)
import socket

from middleware.queue import ServiceQueues
from common.protocol import Protocol
from common.model.game import Game
from common.message import MessageGameInfo
from common.message import MessageQueryGameDatabase
from common.message import MessageEndOfDataset
from common.message import *

CHANNEL_NAME =  "rabbitmq"

class WorkerReviewValidator:
    def __init__(self, queue_name_origin: str, queues_name_destiny_str: str, db_games_ip, db_games_port, cant_rev_indie: int, cant_rev_action: int):
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queues_name_destiny_str.split(',')
        self.running = True
        self.db_games_ip = db_games_ip
        self.db_games_port = db_games_port
        self.cant_rev_indie = cant_rev_indie
        self.cant_rev_action = cant_rev_action 

    def start(self):
        logging.critical(f'action: start | result: success')
        
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.on_pop_message)


    def on_pop_message(self, ch, method, properties, message):
        message_to_push = message

        if message.is_eof():
            msg_eof = MessageEndOfDataset.from_message(message)
            
            if msg_eof.is_last_eof():
                self.send_eofs(msg_eof)
                self.send_eof_to_db(msg_eof)
            
            self.service_queues.ack(ch, method)
            self.service_queues.close_connection()
            self.running = False
            return
        
        messageRI = MessageReviewInfo.from_message(message)
        game = self.get_game_from_db(messageRI.review.game_id)

        if game.id == "-1":
            self.service_queues.ack(ch, method)
            return

        messageRI.review.set_genre(game.genre)

        message_to_push = MessageReviewInfo(messageRI.review)

        for queue_name_destiny in self.queues_name_destiny:
            self.service_queues.push(queue_name_destiny, message_to_push)

        self.service_queues.ack(ch, method)


    def get_game_from_db(self, game_id) -> Game:
        db_games = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        db_games.connect((self.db_games_ip, self.db_games_port))

        protocol_db_games = Protocol(db_games)
        msg_query_game = MessageQueryGameDatabase(game_id)
        protocol_db_games.send(msg_query_game)

        msg = protocol_db_games.receive()
        msg_game_info = MessageGameInfo.from_message(msg)

        db_games.close()
        
        return msg_game_info.game

    def send_eof_to_db(self, msg_eof):
        db_games = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        db_games.connect((self.db_games_ip, self.db_games_port))

        protocol_db_games = Protocol(db_games)
        protocol_db_games.send(msg_eof)

    def send_eofs(self, msg_eof):
        queue_review_indie = self.queues_name_destiny[0]
        queue_review_action = self.queues_name_destiny[1]

        self.send_eofs_to_queue(queue_review_indie, self.cant_rev_indie, msg_eof)
        self.send_eofs_to_queue(queue_review_action, self.cant_rev_action, msg_eof)

    def send_eofs_to_queue(self, queue_name, queue_cant, msg_eof):
        msg_eof.set_not_last_eof()

        for _ in range(queue_cant-1):
            self.service_queues.push(queue_name, msg_eof)
            
        msg_eof.set_last_eof()
        self.service_queues.push(queue_name, msg_eof)