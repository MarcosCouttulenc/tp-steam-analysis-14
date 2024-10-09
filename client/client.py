import logging
logging.basicConfig(level=logging.CRITICAL)
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
        
        #self.client_sock.close()

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

        batch_size = 50
        batch_list = []
        numero_mensaje_enivado = 0

        try: 
            with open('100games.csv', 'r') as file:
                csvReader = csv.reader(file)
                next(csvReader) #saltamos primera linea de headers
                for row in csvReader:
                    # logging.critical(f'action: send_games | result: success | AppID: {row[0]}')
                    # logging.critical(f'action: send_games | result: success | Name: {row[1]}')
                    # logging.critical(f'action: send_games | result: success | Windows: {row[17]}')
                    # logging.critical(f'action: send_games | result: success | Mac: {row[18]}')
                    # logging.critical(f'action: send_games | result: success | Linux: {row[19]}')
                    # logging.critical(f'action: send_games | result: success | Positive: {row[23]}')
                    # logging.critical(f'action: send_games | result: success | Negative: {row[24]}')
                    # logging.critical(f'action: send_games | result: success | Categories: {row[35]}')
                    # logging.critical(f'action: send_games | result: success | Genres: {row[36]}')
                    # logging.critical(f'action: send_games | result: success | Average playtime forever: {row[29]}')
                    # logging.critical(f'action: send_games | result: success | Release date: {row[2]}')

                    game_data = Game(
                        row[0].strip(),  # AppID
                        row[1].strip(),  # Name
                        row[17].strip(), # Windows
                        row[18].strip(), # Mac
                        row[19].strip(), # Linux
                        row[23].strip(), # Positive
                        row[24].strip(), # Negative
                        row[35].strip(), # Categories
                        row[36].strip(), # Genres
                        row[29].strip(), # Average playtime forever
                        row[2].strip()   # Release date
                    )


                    messageGI = MessageGameInfo(game_data)
                    batch_list.append(messageGI)

                    if len(batch_list) == batch_size:
                        self.protocol.send_batch(batch_list)
                        logging.info(f'action: send_games | result: success | msg: sent {len(batch_list)} games')
                        batch_list = []
                    
                    #print(f"Numero mensaje enviado: {numero_mensaje_enivado}")
                    numero_mensaje_enivado += 1

                if len(batch_list) > 0:

                    self.protocol.send_batch(batch_list)
                    logging.info(f'action: send_games | result: success | msg: sent {len(batch_list)} games')
                    batch_list = []

        except Exception as e:
            print("\n\n\n ERROR AL LEER CSV\n\n\n")
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



