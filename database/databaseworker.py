from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageGameInfo
from common.message import MessageQueryGameDatabase
from common.protocol import *
from common.protocol_healthchecker import ProtocolHealthChecker, get_container_name
from common.model.game import Game

import socket
import errno
import logging
import time
import os
import threading

logging.basicConfig(level=logging.CRITICAL)


CHANNEL_NAME =  "rabbitmq"  

class DataBaseWorker():
    
    def __init__ (self,queue_name_origin,data_base, result_query_port, listen_backlog, cant_clients, ip_healthchecker, port_healthchecker, id, port_reviews):
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.servive_queue_purge = ServiceQueues(CHANNEL_NAME)
        self.data_base =  data_base
        self.running_queue = True
        self.running_socket = False
        self.cant_clients = cant_clients
        self.id = id
        self.queue_name_origin = f"{queue_name_origin}_{self.id}"
        
        self.ip_healthchecker = ip_healthchecker
        self.port_healthchecker = int(port_healthchecker)
        self.new_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_socket.bind(('', port_reviews))
        self.new_connection_socket.listen(listen_backlog)
        self.clients_eof = {}
        self.last_msg_id_log_transaction = ""

        self.path_status_info = f"database/state_last_messages.txt"
        self.path_logging = f"database/transaction_logging.txt"

        self.running_threads = []

        self.init_file_state()
    
    def init_file_state(self):
        if not os.path.exists(self.path_status_info):
            os.makedirs(os.path.dirname(self.path_status_info), exist_ok=True)
        else:
            with open(self.path_status_info, 'r') as file:
                line = file.readline().strip()
                if line:
                    data = line.split("|")
                    print(f"Data: {data}")
                    for eofs_clients in data:
                        eof_info = eofs_clients.split(",")
                        self.clients_eof[eof_info[0]] = eof_info[1]

        self.recover_from_transaction_log()
    
    def start(self):

        # Lanzamos proceso para conectarnos al health checker
        connect_health_checker = threading.Thread(
            target = self.process_connect_health_checker 
        )
        connect_health_checker.start()
        self.running_threads.append(connect_health_checker)

        # Si al levantarse, ya proceso todos los clientes
        if  len(self.clients_eof.keys()) == self.cant_clients:
            self.running_queue = False

        # Procesamos todos los juegos.
        while self.running_queue:
            self.service_queues.pop(self.queue_name_origin, self.process_message)
        

        purge_eofs = threading.Thread(
            target = self.process_purge_eofs 
        )
        purge_eofs.start()
        self.running_threads.append(purge_eofs)

        
        # Cuando la bd esta llena, solo atiendo consultas.
        self.running_socket = True
        while self.running_socket:
            client_sock = self.__accept_new_connection()
            
            protocol = Protocol(client_sock)

            try:
                msg = protocol.receive()
            except (ConnectionError, ConnectionRefusedError) as e:
                print("Se cayo el Review Validator que se me conecto, corto comunicacion")
                continue

            msg_query = MessageQueryGameDatabase.from_message(msg)

            game = self.data_base.get_game(msg_query.get_client_id(), msg_query.game_id)

            print(f"Me pidieron el juego {msg_query.game_id} y respondo {game.name}")
            
            msg_game_info = MessageGameInfo(msg_query.message_id, msg_query.get_client_id(), game)

            protocol.send(msg_game_info)
        

        for thread_running in self.running_threads:
            thread_running.join()

    def __accept_new_connection(self):
        try:
            c, addr = self.new_connection_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError as e:
            if e.errno == errno.EBADF:  # Bad file descriptor, server socket closed
                logging.info('SOCKET CERRADO - ACCEPT_NEW_CONNECTIONS')
                return None
            else:
                raise
    

    def process_purge_eofs(self):
        while True:
            self.servive_queue_purge.pop(self.queue_name_origin, self.ignore_msg)
    
    def ignore_msg(self, ch, method, properties, message: Message):
        self.servive_queue_purge.ack(ch, method)
        time.sleep(5)
    
    ## Proceso de conexion con health checker
    ## --------------------------------------------------------------------------------      
    def process_connect_health_checker(self):
        time.sleep(5)

        while True:
            try:
                # Crear y conectar el socket
                skt_next_healthchecker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                skt_next_healthchecker.connect((self.ip_healthchecker, self.port_healthchecker))
                
                # Iniciar protocolo de comunicación
                healthchecker_protocol = ProtocolHealthChecker(skt_next_healthchecker)

                # Enviar nombre del contenedor
                if not healthchecker_protocol.send_container_name(get_container_name()):
                    raise ConnectionError("Fallo al enviar el nombre del contenedor.")

                # Ciclo de health check
                while healthchecker_protocol.wait_for_health_check():
                    healthchecker_protocol.health_check_ack()
            except (socket.error, ConnectionError) as e:
                print(f"Error en la conexión con el healthchecker: {e}")
                time.sleep(5)

    def save_state_in_disk(self):
        clients_eofs_data = "|".join(f"{key},{value}" for key, value in self.clients_eof.items())
        data = f"{str(clients_eofs_data)}"
        temp_path = self.path_status_info + '.tmp'
        
        with open(temp_path, 'w') as temp_file:
            temp_file.write(data)
            temp_file.flush() # Forzar escritura al sistema operativo
            os.fsync(temp_file.fileno()) # Asegurar que se escriba físicamente en disco

        os.replace(temp_path, self.path_status_info)

    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():
            print(f"Recibi un eof {message}")
            id = str(message.get_client_id())

            if not id in self.clients_eof:
                self.clients_eof[id] = True
                self.save_state_in_disk()

            if  len(self.clients_eof.keys()) == self.cant_clients:
                print("llegaron todos los eof, por lo que arranco con consultas")
                self.running_queue = False
                self.service_queues.ack(ch, method)
                self.service_queues.close_connection()
                return

            self.service_queues.ack(ch, method)
            return
        
        # Procesamiento de guardado en base de datos.
        if self.last_msg_id_log_transaction == message.get_message_id():
            print(f"msg filtrado por log: {message}")
            self.service_queues.ack(ch, method)
            return
        
        msg_game_info = MessageGameInfo.from_message(message)

        print(f"Me llega para guardar el juego {message}")

        game_actual = self.data_base.get_game(msg_game_info.get_client_id(), msg_game_info.game.id)

        if str(game_actual.id) == "-1":
            self.log_transaction(message)
            print(f"Voy a guardar el juego {msg_game_info.game.name}")
            self.data_base.store_game(msg_game_info.get_client_id(), msg_game_info.game)
        
        self.service_queues.ack(ch, method)



    ## Transaction Log
    ## --------------------------------------------------------------------------------
    def get_transaction_log(self, message):
        msg_game_info = MessageGameInfo.from_message(message)
        client_id = str(msg_game_info.get_client_id())
        game_id = msg_game_info.game.id
        game = msg_game_info.game

        transaction_log = f"msg::{message.get_message_id()}|client::{client_id}|game_id::{game_id}|name::{game.name}|windows::{game.windows}|mac::{game.mac}|linux::{game.linux}|positive_reviews::{game.positive_reviews}|negative_reviews::{game.negative_reviews}|categories::{game.categories}|genre::{game.genre}|playTime::{game.playTime}|playTime::{game.release_date}"
        return transaction_log

    def log_transaction(self, message):
        transaction_log = self.get_transaction_log(message)
        temp_path = self.path_logging + '.tmp'
        with open(temp_path, 'w') as temp_file:
            temp_file.write(transaction_log)
            temp_file.flush() # Forzar escritura al sistema operativo
            os.fsync(temp_file.fileno()) # Asegurar que se escriba físicamente en disco
        os.replace(temp_path, self.path_logging)
        self.last_msg_id_log_transaction = message.get_message_id()

    def recover_from_transaction_log(self):
        if not os.path.exists(self.path_logging):
            os.makedirs(os.path.dirname(self.path_logging), exist_ok=True)
            return
        
        print("Empieza recuperacion del log \n")
        with open(self.path_logging, 'r') as file:
            line = file.readline().strip()

            print(f"Nos levantamos y el log tiene: {line}")

            data = line.split("|")

            msg_id = data[0].split("::")[1]
            client_id = data[1].split("::")[1]
            game_id = data[2].split("::")[1]
            game_name = data[3].split("::")[1]
            game_windows = data[4].split("::")[1]
            game_mac = data[5].split("::")[1]
            game_linux = data[6].split("::")[1]
            game_positive_reviews = data[7].split("::")[1]
            game_negative_reviews = data[8].split("::")[1]
            game_categories = data[9].split("::")[1]
            game_genre = data[10].split("::")[1]
            game_playTime = data[11].split("::")[1]
            game_release_date = data[12].split("::")[1]
        
        game = Game(game_id, game_name, game_windows, game_mac, game_linux, game_positive_reviews, game_negative_reviews, game_categories, game_genre, game_playTime, game_release_date)
                     
        game_actual = self.data_base.get_game(client_id, game_id)

        if str(game_actual.id) == "-1":
            print(f"El juego {game_name} no habia sido guardado al caerse")
            self.data_base.store_game(client_id, game)
            
        self.last_msg_id_log_transaction = msg_id


#  str(game.name) + FIELD_DELIMITER + str(game.windows) + FIELD_DELIMITER + str(game.mac) + 
#                  FIELD_DELIMITER + str(game.linux) + FIELD_DELIMITER + str(game.positive_reviews) + FIELD_DELIMITER + str(game.negative_reviews) + 
#                  FIELD_DELIMITER + str(game.categories) + FIELD_DELIMITER +  str(game.genre) + FIELD_DELIMITER + str(game.playTime) + 
#                  FIELD_DELIMITER + str(game.release_date) + '\n')