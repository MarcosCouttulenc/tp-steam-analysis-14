import logging
logging.basicConfig(level=logging.CRITICAL)
import socket

from middleware.queue import ServiceQueues
from common.protocol import Protocol
from common.model.game import Game
from common.message import MessageGameInfo
from common.message import MessageQueryGameDatabase
from common.model.review import Review
from common.message import *

CHANNEL_NAME =  "rabbitmq"

class WorkerReviewValidator:
    def __init__(self, queue_name_origin: str, queues_name_destiny_str: str, db_games_ip, db_games_port):
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queues_name_destiny_str.split(',')
        self.running = True
        self.db_games_ip = db_games_ip
        self.db_games_port = db_games_port

    def start(self):
        logging.critical(f'action: start | result: success')
        
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.on_pop_message)


    def on_pop_message(self, ch, method, properties, message):
        message_to_push = message

        if not message.is_eof():
            messageRI = MessageReviewInfo.from_message(message)
            game = self.get_game_from_db(messageRI.review.game_id)

            if game.id == "-1":
                self.service_queues.ack(ch, method)
                return

            messageRI.review.set_genre(game.genre)

            message_to_push = MessageReviewInfo(messageRI.review)

        #logging.critical(f'action: on_pop_message | result: start | body: {message_to_push}')

        for queue_name_destiny in self.queues_name_destiny:
            self.service_queues.push(queue_name_destiny, message_to_push)
            #logging.critical(f'action: on_pop_message | result: push | queue: {queue_name_destiny}  | body: {message_to_push}')

        #logging.info(f'action: on_pop_message | result: ack')

        self.service_queues.ack(ch, method)

        #logging.info(f'action: on_pop_message | result: success')

        if message.is_eof():
            self.running = False
            self.service_queues.close_connection()
            return

    def get_game_from_db(self, game_id) -> Game:
        db_games = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        db_games.connect((self.db_games_ip, self.db_games_port))

        protocol_db_games = Protocol(db_games)
        msg_query_game = MessageQueryGameDatabase(game_id)
        protocol_db_games.send(msg_query_game)

        msg = protocol_db_games.receive()
        msg_game_info = MessageGameInfo.from_message(msg)

        #logging.critical(f'\n\n Juego devuelto por la bd : {msg_game_info} \n\n')

        db_games.close()
        
        return msg_game_info.game