import logging
logging.basicConfig(level=logging.CRITICAL)
import socket
import time
import os

from middleware.queue import ServiceQueues
from common.protocol import Protocol
from common.model.game import Game
from common.message import MessageGameInfo
from common.message import MessageQueryGameDatabase
from common.message import MessageReviewInfo
from common.message import *
from common.sharding import Sharding
from common.message import MessageBatch, USELESS_ID

from common.review_worker import  ReviewWorker

CHANNEL_NAME =  "rabbitmq"

class WorkerReviewValidator(ReviewWorker):
    def __init__(self, queue_name_origin_eof, queue_name_origin, queues_name_destiny, cant_next, cant_slaves, is_master, ip_master, 
                 port_master, db_games_ip, db_games_port, ip_healthchecker, port_healthchecker, id, path_status_info, bdd_ports):
        
        super().__init__(queue_name_origin_eof, queue_name_origin, queues_name_destiny, cant_next, cant_slaves, is_master, ip_master, 
                         port_master, ip_healthchecker, port_healthchecker, id, path_status_info)
        self.db_games_ip = db_games_ip
        self.db_games_port = db_games_port
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        self.bdd_ip_ports = self.get_bdd_ip_ports_dict(bdd_ports)
        self.cant_bdd = len(self.bdd_ip_ports.keys())

        print(f"bdd ip ports: {self.bdd_ip_ports}")
        print(f"cantidad bdds: {self.cant_bdd}")

        # {"database_1": <puerto1>, "database_2": <puerto2>}
    
    def get_bdd_ip_ports_dict(self, bdd_ports):
        rta = {}
        bdd_ports_list = bdd_ports.split(",")
        cant_ports = len(bdd_ports_list)
        for i in range(cant_ports):
            actual_ip = f"{self.db_games_ip}_{i+1}"
            rta[actual_ip] = int(bdd_ports_list[i])
        return rta

    def validate_review(self, _review):
        return True
    
    def process_filter(self):
        while self.running:
            queue_name_origin_id = f"{self.queue_name_origin}-{self.id}"

            try:
                self.service_queues.pop(queue_name_origin_id, self.process_message)
            except Exception as e:
                if "Channel is closed" in str(e):
                    time.sleep(5)  # Espera 5 segundos antes de reintentar
                    self.service_queues = ServiceQueues(CHANNEL_NAME)
                    self.service_queue_filter = ServiceQueues(CHANNEL_NAME)
                    continue
                else:
                    break

    def process_control_slave_eof_handler(self):
        time.sleep(5)
        self.slave_init()

        while True:
            try:    
                self.socket_slave = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket_slave.connect((self.ip_master, self.port_master))
                break
            except Exception as e:
                print(f"[SLAVE] Error: {e}")
                time.sleep(5)
                continue

        while self.running:
            try:
                self.service_queues_eof.pop_non_blocking(self.queue_name_origin_eof, self.process_message_slave_eof)
            except Exception as e:
                if "Channel is closed" in str(e):
                    time.sleep(5)  # Espera 5 segundos antes de reintentar
                    self.service_queues_eof = ServiceQueues(CHANNEL_NAME)
                    continue
                else:
                    break
            

    def forward_message(self, message):

        message_batch = MessageBatch.from_message(message)
        next_batch_list = []
        for msg in message_batch.batch:

            messageRI = MessageReviewInfo.from_message(msg)
            #print("Envio consulta a la bdd")
            game = self.get_game_from_db(message.get_client_id(), messageRI.review.game_id)
            #print(f"Me devolvio la bdd: {game.name}")

            if game.id == "-1":
                print(f"No encontre el juego")
                continue

            messageRI.review.set_genre(game.genre)

            message_to_push = MessageReviewInfo(USELESS_ID, message.get_client_id(), messageRI.review)

            next_batch_list.append(message_to_push)

        next_batch_msg = MessageBatch(message.get_client_id(), self.get_new_message_id(), next_batch_list)

        for queue_name_next, cant_queue_next in self.queues_destiny.items():
            queue_next_id = Sharding.calculate_shard(next_batch_msg.get_batch_id(), cant_queue_next)
            queue_name_destiny = f"{queue_name_next}-{str(queue_next_id)}"
            self.service_queues.push(queue_name_destiny, next_batch_msg)
            

    def get_game_from_db(self, client_id, game_id) -> Game:
        bdd_ident = Sharding.calculate_shard(game_id, self.cant_bdd)

        bdd_ip = f"{self.db_games_ip}_{bdd_ident}"
        bdd_port = self.bdd_ip_ports[bdd_ip]

        while True:
            try:
                db_games = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                db_games.connect((bdd_ip, bdd_port))
    
            except Exception as e:
                print(f"Bdd se cayo, retry de conexion. Error: {e}")
                time.sleep(5)
                continue

            protocol_db_games = Protocol(db_games)
            message_id = f"C_{str(client_id)}_QUERY_{str(game_id)}"
            msg_query_game = MessageQueryGameDatabase(message_id, client_id, game_id)
            sended = protocol_db_games.send(msg_query_game)

            if sended == None:
                print(f"Bdd se cayo, retry de conexion")
                time.sleep(5)
                continue

            try:
                msg = protocol_db_games.receive()
            except (ConnectionRefusedError, ConnectionError) as e:
                print(f"Bdd se cayo, retry de conexion")
                time.sleep(5)
                continue

            msg_game_info = MessageGameInfo.from_message(msg)

            try:
                db_games.close()
            except:
                pass
            
            return msg_game_info.game
        
    def simulate_failure(self):
        #para asegurarme que ya me conecte al healthchecker
        time.sleep(8)
        print("Me caigo")
        print(f"Seq Number {self.actual_seq_number} \n")
        print(f"Dict: {self.last_seq_number_by_filter} \n")
        
        self.running = False
        
        # return
        print("Simulando caída del contenedor...")
        self.service_queues_eof.close_connection()
        self.service_queue_filter.close_connection()
        self.service_queues.close_connection()

        print("cerre las colas de rabbit")

        os._exit(1)
        print("No debería llegar acá porque estoy muerto")