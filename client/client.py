import logging
#import pika
import socket

from common.message import *
from common.protocol import *
from common.model.game import Game


class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

    def start(self):
        logging.info('action: client_start | result: success')
        
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((self.server_ip, int(self.server_port)))

        protocol = Protocol(client_sock)

        msg_server = protocol.receive()
        msg_welcome_client = MessageWelcomeClient.from_message(msg_server)
        if msg_welcome_client == None:
            logging.info(f'action: client_msg_received | result: invalid_msg | msg: {msg_server}')
            return

        logging.info(f'action: client_msg_received | result: success | msg: {msg_welcome_client}')
        
        game = Game(1, "Fifa")
        message_game = MessageGameInfo(game)
        protocol.send(message_game)

        logging.info(f'action: client_msg_sent | result: success | msg: {message_game}')

        client_sock.close()

