import logging
import socket
import csv
import time

from common.message import *
from common.protocol import Protocol
from common.protocol import *
from common.model.game import Game

class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect((self.server_ip, int(self.server_port)))
        self.listen_result_query_port = 0

        self.protocol = Protocol(self.client_sock)

    def start(self):
        logging.info('action: client_start | result: success')
        
        self.get_welcome_message()

        self.send_games()
        
        self.send_reviews()

        self.notify_end_of_data()
        
        self.client_sock.close()

        self.ask_for_results()

    def get_welcome_message(self):
        logging.info('action: get_welcome_message | result: start')

        msg_server = self.protocol.receive()
        msg_welcome_client = MessageWelcomeClient.from_message(msg_server)
        if msg_welcome_client == None:
            logging.info(f'action: client_msg_received | result: invalid_msg | msg: {msg_server}')
            return

        self.listen_result_query_port = int(msg_welcome_client.listen_result_query_port)

    def send_games(self):
        logging.info('action: send_games | result: start')

        batch_size = 10
        batch_list = []

        try: 
            with open('5games.csv', 'r') as file:
                csvReader = csv.reader(file)
                for row in csvReader:
                    game_data = Game(
                        row[0],  # AppID
                        row[1],  # Name
                        row[17], # Windows
                        row[18], # Mac
                        row[19], # Linux
                        row[23], # Positive
                        row[24], # Negative
                        row[35], # Categories
                        row[36], # Genres
                        row[29], # Average playtime forever
                        row[2]   # Release date
                    )

                    messageGI = MessageGameInfo(game_data)
                    batch_list.append(messageGI)

                    if len(batch_list) == batch_size:
                        self.protocol.send_batch(batch_list)
                        logging.info(f'action: send_games | result: success | msg: sent {len(batch_list)} games')
                        batch_list = []

                if len(batch_list) > 0:
                    self.protocol.send_batch(batch_list)
                    logging.info(f'action: send_games | result: success | msg: sent {len(batch_list)} games')
                    batch_list = []

        except Exception as e:
            logging.info(f'action: send_games | result: error | msg: {e}')

    def send_reviews(self):
        logging.info('action: send_reviews | result: start')


    def notify_end_of_data(self):
        logging.info('action: notify_end_of_data | result: start')
        self.protocol.send_batch([MessageEndOfDataset("OK")])
        logging.info(f'action: notify_end_of_data | result: success')

    def ask_for_results(self):
        logging.info('action: ask_for_results | result: start')

        while True:
            result_responser_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result_responser_sock.connect(("result_responser", int(self.listen_result_query_port)))

            protocol_result_responser = Protocol(result_responser_sock)
            
            while True:
                data = protocol_result_responser.receive_stream()
                
                if not data:
                    break
                
                # Mostrar los datos recibidos por pantalla a medida que llegan
                print(data)
               
            result_responser_sock.close()
            time.sleep(5)  # Esperar 5 segundos antes de la próxima ejecución
