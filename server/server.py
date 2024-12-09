import logging
logging.basicConfig(level=logging.CRITICAL)
import socket
import errno
import signal
import multiprocessing

from common.message import *
from common.protocol import Protocol
from common.protocol import *
from middleware.queue import ServiceQueues
from common.sharding import Sharding
from common.message import MessageBatch
from common.message import MessageEndOfDataset
from common.message import MessageWelcomeClient

CHANNEL_NAME =  "rabbitmq"
QUEUE_GAMES = "queue-games"
QUEUE_REVIEWS = "queue-reviews"

class Server:
    def __init__(self, listen_new_connection_port, listen_result_query_port, listen_backlog, cant_game_validators, 
                 cant_review_validators, ip_healthchecker, port_healthchecker):
        self.listen_new_connection_port = listen_new_connection_port
        self.listen_result_query_port = listen_result_query_port
        self.cant_game_validators = cant_game_validators
        self.cant_review_validators = cant_review_validators

        self.new_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_socket.bind(('', listen_new_connection_port))
        self.new_connection_socket.listen(listen_backlog)

        self._server_is_running = True
        self._server_connected_clients = []

        self.ip_healthchecker = ip_healthchecker
        self.port_healthchecker = int(port_healthchecker)

        self.actual_seq_number = multiprocessing.Value('i', 0)
        self.lock_msg_id = multiprocessing.Lock()

        # Initialize signals
        self.initialize_signals()

    def initialize_signals(self):
        signal.signal(signal.SIGTERM, self.stop)

    def stop(self, signum, frame):
        logging.info("action: server_stop | result: in_progress")
        self._server_is_running = False

        for connected_client in self._server_connected_clients:
            connected_client.join()

        self.new_connection_socket.close()
        logging.info("action: server_stop | result: success")
        
    
    def __accept_new_connection(self):
        try:
            c, addr = self.new_connection_socket.accept()
            return c
        except OSError as e:
            if e.errno == errno.EBADF:  # Bad file descriptor, server socket closed
                return None
            else:
                raise
    
    def start(self):
        client_id = 0
        while self._server_is_running:
            client_sock = self.__accept_new_connection()

            if client_sock:
                client_process = multiprocessing.Process(
                    target = self.handle_client, 
                    args = (client_sock, client_id)
                ) 
                client_process.start()
                self._server_connected_clients.append(client_process)

            client_id += 1

    def handle_client(self, client_sock, client_id):

        protocol = Protocol(client_sock)

        msg_welcome_client = MessageWelcomeClient(client_id, self.listen_result_query_port)
        protocol.send(msg_welcome_client)

        self.process_client_messages(protocol)

    def process_client_messages(self, protocol):

        service_queue_games = ServiceQueues(CHANNEL_NAME)
        service_queue_review = ServiceQueues(CHANNEL_NAME)

        end_of_data = False
        numero_menasje_recibido = 0

        while (not end_of_data):
            receive_batch = protocol.receive_batch()
            numero_menasje_recibido += len(receive_batch)

            if receive_batch == None:
                logging.critical(f'action: server_msg_received | result: invalid_msg | msg: {receive_batch}')
                return

            first_message = receive_batch[0]
            
            # Send eofs
            while first_message == None:
                receive_batch.pop(0)
                first_message = receive_batch[0]

            if first_message.is_eof():
                print("LLEgo EOF")
                msg_end_of_dataset = MessageEndOfDataset.from_message(first_message)

                if msg_end_of_dataset.type == "Game":
                    print("Era EOF de game")
                    self.send_eofs_to_queue(msg_end_of_dataset, QUEUE_GAMES, self.cant_game_validators, service_queue_games)
                else:
                    print("Era EOF de Review")
                    self.send_eofs_to_queue(msg_end_of_dataset, QUEUE_REVIEWS, self.cant_review_validators, service_queue_review)
                    end_of_data = True
                continue
            
            # Send batchs
            client_id = first_message.get_client_id()
            msg_batch = MessageBatch(client_id, self.get_new_message_id(), receive_batch)

            if first_message.is_game():
                self.forward_message(msg_batch, QUEUE_GAMES, self.cant_game_validators, service_queue_games)
            elif first_message.is_review():
                self.forward_message(msg_batch, QUEUE_REVIEWS, self.cant_review_validators, service_queue_review)

            #print(numero_menasje_recibido)
                
    
    def send_eofs_to_queue(self, msg_end_of_dataset, destiny_queue, cant_workers, service_queue):
        for id in range(1, cant_workers + 1):
            queue_name_destiny = f"{destiny_queue}-{id}"

            if (id == cant_workers):
                msg_end_of_dataset.set_last_eof()
            
            service_queue.push(queue_name_destiny, msg_end_of_dataset)

    def forward_message(self, message: MessageBatch, queue_name_next, cant_queue_next, service_queue):
        queue_next_id = Sharding.calculate_shard(message.get_batch_id(), cant_queue_next)
        queue_name_destiny = f"{queue_name_next}-{str(queue_next_id)}"
        service_queue.push(queue_name_destiny, message)

    def get_new_message_id(self):
        with self.lock_msg_id:
            self.actual_seq_number.value += 1
            return f"S1_M{str(self.actual_seq_number.value)}"