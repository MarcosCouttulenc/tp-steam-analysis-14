import logging
import socket
import csv

from common.message import *
from common.protocol import *
from common.model.game import Game

class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect((self.server_ip, int(self.server_port)))

        self.protocol = Protocol(self.client_sock)

    def start(self):
        logging.info('action: client_start | result: success')
        
        self.get_welcome_message()

        self.send_games()

        self.send_reviews()

        self.notify_end_of_data()

        self.client_sock.close()

    def get_welcome_message(self):
        logging.info('action: get_welcome_message | result: start')

        msg_server = self.protocol.receive()
        msg_welcome_client = MessageWelcomeClient.from_message(msg_server)
        if msg_welcome_client == None:
            logging.info(f'action: client_msg_received | result: invalid_msg | msg: {msg_server}')
            return

    def send_games(self):
        logging.info('action: send_games | result: start')

        batch_size = 10
        batch_list = [MessageGameInfo]

        try: 
            with open('games.csv', 'r') as file:
                csvReader = csv.reader(file)
                for row in csvReader:
                    game_data = Game(
                        row["AppID"], row["Name"],row["Linux"],row["Windows"],row["Mac"],row["Positive"],
                        row["Negative"],row["Average playtime forever"],row["Categories"],row["Genres"]
                    )

                    batch_list.append(MessageGameInfo(game_data))

                    if len(batch_list) == batch_size:
                        self.protocol.send_batch(batch_list)
                        logging.info(f'action: send_games | result: success | msg: sent {len(batch_list)} games')
                        batch_list = []

                if batch_list:
                    self.protocol.send_batch(batch_list)
                    logging.info(f'action: send_games | result: success | msg: sent {len(batch_list)} games')
                    batch_list = [MessageGameInfo]

        except Exception as e:
            logging.info(f'action: send_games | result: error | msg: {e}')

    def send_reviews(self):
        logging.info('action: send_reviews | result: start')


    def notify_end_of_data(self):
        logging.info('action: notify_end_of_data | result: start')
        self.protocol.send_batch([MessageEndOfDataset("OK")])
        logging.info(f'action: notify_end_of_data | result: success')