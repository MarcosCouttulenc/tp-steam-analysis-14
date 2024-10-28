import logging
logging.basicConfig(level=logging.CRITICAL)
import socket
import csv
csv.field_size_limit(100000000)
import time
import multiprocessing

from common.message import *
from common.protocol import Protocol
from common.protocol import *
from common.model.game import Game
from common.model.review import Review

FILE_NAME_GAMES = 'fullgames.csv'
FILE_NAME_REVIEWS = 'data0.1porcent.csv'

class Client:
    def __init__(self, server_ip, server_port, result_responser_ip):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect((self.server_ip, int(self.server_port)))
        self.result_responser_ip = result_responser_ip

        self.client_id = 0
        self.listen_result_query_port = 0

        self.protocol = Protocol(self.client_sock)

    def start(self):
        logging.info('action: client_start | result: success')
        
        self.get_welcome_message()

        self.send_games()
        
        self.send_reviews()

        self.notify_end_of_data()

        self.ask_for_results()

    def get_welcome_message(self):
        logging.info('action: get_welcome_message | result: start')

        msg_server = self.protocol.receive()
        msg_welcome_client = MessageWelcomeClient.from_message(msg_server)
        if msg_welcome_client == None:
            logging.info(f'action: client_msg_received | result: invalid_msg | msg: {msg_server}')
            return

        self.client_id = msg_welcome_client.get_client_id()
        self.listen_result_query_port = int(msg_welcome_client.listen_result_query_port)

    def send_games(self):
        logging.info(f'Client_{self.client_id} action: send_games | result: start')

        batch_size = 50
        batch_list = []
        numero_mensaje_enivado = 0
        total_sent_games = 0

        try: 
            with open(FILE_NAME_GAMES, 'r') as file:
                csvReader = csv.reader(file)
                next(csvReader) #saltamos primera linea de headers
                for row in csvReader:
                    total_sent_games+=1
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

                    messageGI = MessageGameInfo(self.client_id, game_data)
                    batch_list.append(messageGI)

                    if len(batch_list) == batch_size:
                        self.protocol.send_batch(batch_list)
                        logging.info(f'Client_{self.client_id} action: send_games | result: success | msg: sent {len(batch_list)} games')
                        #logging.critical(f"Games sent: {total_sent_games}")
                        batch_list = []
                    
                    numero_mensaje_enivado += 1

                if len(batch_list) > 0:
                    self.protocol.send_batch(batch_list)
                    logging.info(f'Client_{self.client_id} action: send_games | result: success | msg: sent {len(batch_list)} games')
                    #logging.critical(f"Games sent: {total_sent_games}")
                    batch_list = []
                
                self.protocol.send_batch([MessageEndOfDataset(self.client_id,"Game")])
                logging.critical(" All Games sent")

        except Exception as e:
            print("\n\n\n ERROR AL LEER CSV DE JUEGOS \n\n\n")
            logging.critical(f'Client_{self.client_id} action: send_games | result: error | msg: {e}')

   
    def send_reviews(self):
        logging.info('action: send_reviews | result: start')
        
        batch_size = 50
        batch_list = []
        cant_sent = 0

        try:
            with open(FILE_NAME_REVIEWS, 'r') as file:
                csvReader = csv.reader(file)
                next(csvReader) #saltamos primera linea de headers
                for row in csvReader:
                    game_review = Review(
                        row[0].strip(),  # AppID
                        row[1].strip(),  # Name
                        row[2].strip(),  # Review
                        row[3].strip(),  # score
                        ""              # Genre
                    )

                    messageRI = MessageReviewInfo(self.client_id, game_review)
                    batch_list.append(messageRI)
                    

                    if len(batch_list) == batch_size:
                        self.protocol.send_batch(batch_list)
                        cant_sent += batch_size
                        logging.critical(f'Client_{self.client_id} action: send_reviews| result: success | msg: sent {cant_sent} reviews')
                        batch_list = []

                if len(batch_list) > 0:
                    self.protocol.send_batch(batch_list)
                    cant_sent += len(batch_list)
                    logging.critical(f'Client_{self.client_id} action: reviews | result: success | msg: sent {cant_sent} reviews')
                    batch_list = []
                
                self.protocol.send_batch([MessageEndOfDataset(self.client_id, "Review")])

        except Exception as e:
            print(f"\n\n\n Client_{self.client_id} ERROR AL LEER CSV DE REVIEWS\n\n\n")
            logging.critical(f'Client_{self.client_id} action: send_reviews | result: error | msg: {e}')
    
    
    def notify_end_of_data(self):
        logging.info(f'Client_{self.client_id} action: notify_end_of_data | result: start')
        logging.info(f'Client_{self.client_id} action: notify_end_of_data | result: success')

    def ask_for_results(self):
        logging.info(f'Client_{self.client_id} action: ask_for_results | result: start')

        while True:
            result_responser_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result_responser_sock.connect((self.result_responser_ip, int(self.listen_result_query_port)))

            protocol_result_responser = Protocol(result_responser_sock)
            protocol_result_responser.send(MessageClientAskResults(self.client_id))
            
            while True:
                data = protocol_result_responser.receive_stream()
                
                if not data:
                    break
                
                # Mostrar los datos recibidos por pantalla a medida que llegan
                print(data)
               
            result_responser_sock.close()
            time.sleep(5)  # Esperar 5 segundos antes de la próxima ejecución



