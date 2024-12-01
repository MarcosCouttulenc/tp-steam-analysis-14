import logging
logging.basicConfig(level=logging.CRITICAL)
import socket
import csv
csv.field_size_limit(100000000)
import time

from common.message import *
from common.protocol import Protocol
from common.protocol import *
from common.model.game import Game
from common.model.review import Review
from common.message import MessageResultStatus
from common.message import MessageResultContent
from common.message import ResultStatus

class Client:
    def __init__(self, server_ip, server_port, result_responser_ip, games_file_path, reviews_file_path):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect((self.server_ip, int(self.server_port)))
        self.result_responser_ip = result_responser_ip

        self.client_id = 0
        self.listen_result_query_port = 0

        self.protocol = Protocol(self.client_sock)
        self.games_file_path = games_file_path 
        self.reviews_file_path = reviews_file_path 

    def start(self):
        logging.info('action: client_start | result: success')
        
        self.get_welcome_message()

        self.send_games()
        
        self.send_reviews()

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
            with open(self.games_file_path, 'r') as file:
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

                    message_id = f"C_{self.client_id}_GAME_{str(game_data.id)}"
                    messageGI = MessageGameInfo(message_id, self.client_id, game_data)
                    batch_list.append(messageGI)

                    if len(batch_list) == batch_size:
                        self.protocol.send_batch(batch_list)
                        logging.info(f'Client_{self.client_id} action: send_games | result: success | msg: sent {len(batch_list)} games')
                        batch_list = []
                    
                    numero_mensaje_enivado += 1

                if len(batch_list) > 0:
                    self.protocol.send_batch(batch_list)
                    logging.info(f'Client_{self.client_id} action: send_games | result: success | msg: sent {len(batch_list)} games')
                    batch_list = []
                
                message_id = f"C_{self.client_id}_GAME_EOF"
                self.protocol.send_batch([MessageEndOfDataset(message_id, self.client_id, "Game")])
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
            with open(self.reviews_file_path, 'r') as file:
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

                    message_id = f"C_{self.client_id}_REVIEW_{str(game_review.game_id)}"
                    messageRI = MessageReviewInfo(message_id, self.client_id, game_review)
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
                
                message_id = f"C_{self.client_id}_REVIEW_EOF"
                self.protocol.send_batch([MessageEndOfDataset(message_id, self.client_id, "Review")])

        except Exception as e:
            print(f"\n\n\n Client_{self.client_id} ERROR AL LEER CSV DE REVIEWS\n\n\n")
            logging.critical(f'Client_{self.client_id} action: send_reviews | result: error | msg: {e}')
            
    def ask_for_results(self):
        logging.info(f'Client_{self.client_id} action: ask_for_results | result: start')

        while True:
            result_responser_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result_responser_sock.connect((self.result_responser_ip, int(self.listen_result_query_port)))

            protocol_result_responser = Protocol(result_responser_sock)
            protocol_result_responser.send(MessageClientAskResults(self.client_id))
            
            msg_status = protocol_result_responser.receive()
            msg_results_status = MessageResultStatus.from_message(msg_status)

            msg_content = protocol_result_responser.receive()
            msg_results_content = MessageResultContent.from_message(msg_content)
            
            msg_results_content.message_payload = msg_results_content.message_payload.replace("<br/>", "\n")

            print(msg_results_content.message_payload)
            
            # Si el resultado esta listo, escribe en un archivo y finaliza
            if msg_results_status.message_payload == ResultStatus.FINISHED.value:
                file_path = f"resultados/resultados-{str(self.client_id)}.txt"
                with open(file_path, "w") as file:
                    file.write(msg_results_content.message_payload)
                break
            
            result_responser_sock.close()
            time.sleep(5)  # Esperar 5 segundos antes de la próxima ejecución

        logging.info(f'Client_{self.client_id} action: ask_for_results | result: success')
        logging.info(f'Client_{self.client_id} resultados procesados correctamente')

