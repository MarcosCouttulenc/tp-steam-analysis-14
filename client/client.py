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
FILE_NAME_REVIEWS = 'data1porcent.csv'

class Client:
    def __init__(self, server_ip, server_port, result_responser_ip):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect((self.server_ip, int(self.server_port)))
        self.result_responser_ip = result_responser_ip
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

                    messageGI = MessageGameInfo(game_data)
                    batch_list.append(messageGI)

                    if len(batch_list) == batch_size:
                        self.protocol.send_batch(batch_list)
                        logging.info(f'action: send_games | result: success | msg: sent {len(batch_list)} games')
                        #logging.critical(f"Games sent: {total_sent_games}")
                        batch_list = []
                    
                    numero_mensaje_enivado += 1

                if len(batch_list) > 0:
                    self.protocol.send_batch(batch_list)
                    logging.info(f'action: send_games | result: success | msg: sent {len(batch_list)} games')
                    #logging.critical(f"Games sent: {total_sent_games}")
                    batch_list = []
                
                self.protocol.send_batch([MessageEndOfDataset("Game")])
                logging.critical(" All Games sent")

        except Exception as e:
            print("\n\n\n ERROR AL LEER CSV DE JUEGOS \n\n\n")
            logging.critical(f'action: send_games | result: error | msg: {e}')

   
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

                    messageRI = MessageReviewInfo(game_review)
                    batch_list.append(messageRI)
                    

                    if len(batch_list) == batch_size:
                        self.protocol.send_batch(batch_list)
                        cant_sent += batch_size
                        logging.critical(f'action: send_reviews| result: success | msg: sent {cant_sent} reviews')
                        batch_list = []

                if len(batch_list) > 0:
                    self.protocol.send_batch(batch_list)
                    cant_sent += len(batch_list)
                    logging.critical(f'action: reviews | result: success | msg: sent {cant_sent} reviews')
                    batch_list = []
                
                self.protocol.send_batch([MessageEndOfDataset("Review")])

        except Exception as e:
            print("\n\n\n ERROR AL LEER CSV DE REVIEWS\n\n\n")
            logging.critical(f'action: send_reviews | result: error | msg: {e}')
    
    '''
    def count_reviews(self, file_name):
        """Función para contar cuántas reviews hay en el archivo CSV."""
        with open(file_name, 'r') as file:
            csvReader = csv.reader(file)
            next(csvReader)  # Saltar encabezado
            total_reviews = sum(1 for _ in csvReader)
        return total_reviews

    def process_chunk(self, start, end, chunk_id, protocol):
        """Función que procesa un segmento de reviews desde start hasta end."""
        batch_size = 50
        batch_list = []
        cant_sent = 0

        logging.info(f'action: send_reviews | process_id: {chunk_id} | result: start')

        try:
            with open(FILE_NAME_REVIEWS, 'r') as file:
                csvReader = csv.reader(file)
                next(csvReader)  # Saltar encabezado
                
                for i, row in enumerate(csvReader):
                    if i < start:
                        continue
                    if i >= end:
                        break

                    game_review = Review(
                        row[0].strip(),  # AppID
                        row[1].strip(),  # Name
                        row[2].strip(),  # Review
                        row[3].strip(),  # score
                        ""               # Genre
                    )

                    messageRI = MessageReviewInfo(game_review)
                    batch_list.append(messageRI)

                    if len(batch_list) == batch_size:
                        protocol.send_batch(batch_list)
                        cant_sent += batch_size
                        logging.info(f'action: send_reviews | process_id: {chunk_id} | sent {cant_sent} reviews')
                        batch_list = []

            # Enviar las reviews restantes
            if batch_list:
                protocol.send_batch(batch_list)
                cant_sent += len(batch_list)
                logging.info(f'action: send_reviews | process_id: {chunk_id} | sent {cant_sent} reviews')
                protocol.send_batch([MessageEndOfDataset("Review")])

        except Exception as e:
            logging.critical(f'action: send_reviews | process_id: {chunk_id} | error: {e}')


    def send_reviews(self):
        num_processes = 45  # Número de procesos que quieres usar
        file_name = FILE_NAME_REVIEWS
        total_reviews = self.count_reviews(file_name)  # Contar cuántas reviews hay

        chunk_size = total_reviews // num_processes  # Dividir equitativamente
        remainder = total_reviews % num_processes  # Resto para distribuir

        processes = []
        start = 0
        for i in range(num_processes):
            # Calcular el rango que debe procesar cada proceso
            end = start + chunk_size + (1 if i < remainder else 0)
            p = multiprocessing.Process(target=self.process_chunk, args=(start, end, i, self.protocol))
            processes.append(p)
            p.start()
            start = end  # Actualizar para el siguiente proceso

        for p in processes:
            p.join()
    '''
    def notify_end_of_data(self):
        logging.info('action: notify_end_of_data | result: start')
        logging.info(f'action: notify_end_of_data | result: success')

    def ask_for_results(self):
        logging.info('action: ask_for_results | result: start')

        while True:
            result_responser_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result_responser_sock.connect((self.result_responser_ip, int(self.listen_result_query_port)))

            protocol_result_responser = Protocol(result_responser_sock)
            
            while True:
                data = protocol_result_responser.receive_stream()
                
                if not data:
                    break
                
                # Mostrar los datos recibidos por pantalla a medida que llegan
                print(data)
               
            result_responser_sock.close()
            time.sleep(5)  # Esperar 5 segundos antes de la próxima ejecución



