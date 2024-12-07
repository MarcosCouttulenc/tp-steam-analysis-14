import csv
import logging
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageResultStatus
from common.message import ResultStatus
from common.protocol import *
from common.protocol_healthchecker import ProtocolHealthChecker, get_container_name
import multiprocessing
import socket
import errno
import time
import os
import signal
import shutil


CHANNEL_NAME = "rabbitmq"
MAX_LOG_LEN = 1000

class QueryFile:
    def __init__(self, queue_name_origin, file_path, result_query_port, listen_backlog,ip_healthchecker, port_healthchecker, path_status_info, listen_to_result_responser_port, id):
        print(f"queue_name_origin: {queue_name_origin}")
        print(f"file_path: {file_path}")
        print(f"result_query_port: {result_query_port}")
        print(f"listen_backlog: {listen_backlog}")
        print(f"ip_healthchecker: {ip_healthchecker}")
        print(f"port_healthchecker: {port_healthchecker}")
        print(f"path_status_info: {path_status_info}")
        print(f"listen_to_result_responser_port: {listen_to_result_responser_port}")
        
        self.file_path = file_path
        
        self.new_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_socket.bind(('', int(listen_to_result_responser_port)))
        self.new_connection_socket.listen(listen_backlog)
        self.file_lock = multiprocessing.Lock()
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        manager = multiprocessing.Manager()
        self.totals = manager.dict()
        self.eof_dict = manager.dict()
        self.ip_healthchecker = ip_healthchecker
        self.port_healthchecker = int(port_healthchecker)

        self.actual_seq_number = 0
        
        self.last_seq_number_by_filter = {}
        self.last_msg_id_log_transaction = ""
        self.path_status_info = f"{path_status_info}/state_last_messages.txt"
        self.path_logging = f"{path_status_info}/transaction_logging.txt"

        self.cant_mensajes_procesados = 0

        self.init_file_state()
        self.init_signals()

        self.listen_to_result_responser_port = listen_to_result_responser_port
        self.id = id
        self.queue_name_origin = f"{queue_name_origin}-{self.id}"
        print(f"queue_name_origin: {self.queue_name_origin}")

        self.log_transaction_len = {}



    def init_signals(self):
        signal.signal(signal.SIGTERM, self.stop)

    def stop(self, signum, frame):
        logging.info("action: stop | result: in_progress")
        
        self.running = False
        self.service_queues.close_connection()
        self.new_connection_socket.close()

        logging.info("action: stop | result: success")

    def init_file_state(self):
        if not os.path.exists(self.path_status_info):
            os.makedirs(os.path.dirname(self.path_status_info), exist_ok=True)
        else:
            with open(self.path_status_info, 'r') as file:
                line = file.readline().strip()

                # La linea tiene esta forma -> seq_number_actual|F1,M1|F2,M3|F3,M6..
                data = line.split("|")
                self.actual_seq_number = int(data[0])
                for filter_data in data[1:]:
                    filter_info = filter_data.split(",")
                    self.last_seq_number_by_filter[filter_info[0]] = filter_info[1]

                # La segunda linea tiene la informacion de los EOFs por cliente
                
                line = file.readline().strip()
                if line:
                    data = line.split("|")
                    print(f"Data: {data}")
                    for eofs_clients in data:
                        eof_info = eofs_clients.split(",")
                        self.eof_dict[eof_info[0]] = eof_info[1]

        print("Me levanto")
        print(f"Seq Number {self.actual_seq_number} \n")
        print(f"Dict: {self.last_seq_number_by_filter} \n")
        print(f"Eof: {self.eof_dict} \n")

        self.recover_from_transaction_log()
    
    def start(self):
        # Lanzamos proceso para conectarnos al health checker
        connect_health_checker = multiprocessing.Process(
            target = self.process_connect_health_checker 
        )

        process_updates = multiprocessing.Process(target=self.process_handle_result_updates, args=())
        process_queries = multiprocessing.Process(target=self.process_handle_result_queries, args=())

        process_updates.start()
        process_queries.start()
        connect_health_checker.start()

        process_updates.join()
        process_queries.join()
        connect_health_checker.join()


    ## Proceso de conexion con health checker
    ## --------------------------------------------------------------------------------      
    def process_connect_health_checker(self):
        time.sleep(5)

        while self.running:
            try:
                # Crear y conectar el socket
                skt_next_healthchecker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                skt_next_healthchecker.connect((self.ip_healthchecker, self.port_healthchecker))

                print("Conectado al healthchecker")
                
                # Iniciar protocolo de comunicación
                healthchecker_protocol = ProtocolHealthChecker(skt_next_healthchecker)

                # Enviar nombre del contenedor
                if not healthchecker_protocol.send_container_name(get_container_name()):
                    raise ConnectionError("Fallo al enviar el nombre del contenedor.")

                print("Comienzo ciclo de healthcheck")
                # Ciclo de health check
                while healthchecker_protocol.wait_for_health_check():
                    healthchecker_protocol.health_check_ack()
            except (socket.error, ConnectionError) as e:
                print(f"Error en la conexión con el healthchecker: {e}")
                time.sleep(5)
    

    ## Proceso para devolver informacion de la query
    ## --------------------------------------------------------------------------------
    def process_handle_result_queries(self):
        while self.running:
            client_sock = self.__accept_new_connection()
            protocol = Protocol(client_sock)

            message = protocol.receive()
            client_id = int(message.get_client_id())

            message_result_status = MessageResultStatus(str(client_id), ResultStatus.PENDING)
            if (self.client_finished(client_id)):
                message_result_status = MessageResultStatus(str(client_id), ResultStatus.FINISHED)
            
            with self.file_lock:
                file_snapshot = self.get_file_snapshot(client_id)

            message_result = self.get_message_result_from_file_snapshot(client_id, file_snapshot)

            protocol.send(message_result_status)
            protocol.send(message_result)

    def client_finished(self, client_id):
        return (str(client_id) in self.eof_dict.keys())
    

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
            
    

    ## Proceso para actualizar resultados de la query
    ## --------------------------------------------------------------------------------
    def process_handle_result_updates(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.handle_new_update)

    def handle_new_update(self, ch, method, properties, message: Message):
        self.cant_mensajes_procesados += 1

        if self.message_was_processed(message):
            self.service_queues.ack(ch, method)
            return
        
        if message.is_eof():
            self.handle_eof(message, ch, method)
            return

        if self.last_msg_id_log_transaction == message.get_message_id():
            self.service_queues.ack(ch, method)
            return

        with self.file_lock:
            self.log_transaction(message)
            self.update_results(message)

        self.last_seq_number_by_filter[message.get_filterid_from_message_id()] = message.get_seqnum_from_message_id()
        
        self.save_state_in_disk()

        self.service_queues.ack(ch, method)

    def handle_eof(self, message, ch, method):
        self.last_seq_number_by_filter[message.get_filterid_from_message_id()] = message.get_seqnum_from_message_id()
        self.save_state_in_disk()
        self.set_client_as_finished(message)
        self.service_queues.ack(ch, method)
    

    def set_client_as_finished(self, message):
        self.eof_dict[str(message.get_client_id())] = True

    def get_message_result_from_file_snapshot(self, client_id, file_snapshot):
        return 0

    def get_file_snapshot(self, client_id):
        return 0

    def update_results(self, message):
        return 0
    
    def message_was_processed(self, message : Message):
        if self.last_seq_number_by_filter == None:
            return False

        if len(self.last_seq_number_by_filter.items()) == 0:
            return False

        filter = message.get_filterid_from_message_id()
        seq_num = message.get_seqnum_from_message_id()

        return (filter,seq_num) in self.last_seq_number_by_filter.items()
    
    def save_state_in_disk(self):
        last_seq_number_by_filter_data = "|".join(f"{key},{value}" for key, value in self.last_seq_number_by_filter.items())
        eof_clients_data = "|".join(f"{key},{value}" for key, value in self.eof_dict.items())
        data = f"{str(self.actual_seq_number)}|{last_seq_number_by_filter_data}\n{eof_clients_data}"
        temp_path = self.path_status_info + '.tmp'
        
        with open(temp_path, 'w') as temp_file:
            temp_file.write(data)
            temp_file.flush()
            os.fsync(temp_file.fileno())

        os.replace(temp_path, self.path_status_info)
    

    def log_transaction(self, message):
        transaction_log = self.get_transaction_log(message)
        self.atomic_write(transaction_log, self.path_logging)
        self.last_msg_id_log_transaction = message.get_message_id()


    def atomic_write(self, data, path):
        temp_path = path + '.tmp'
        with open(temp_path, 'w') as temp_file:
            temp_file.write(data)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_path, path)

    def atomic_append(self, data, path_origin):
        if not os.path.exists(path_origin):
            os.makedirs(os.path.dirname(path_origin), exist_ok=True)

            with open(path_origin, "w") as _:
                pass

        temp_path = path_origin + '.tmp'
        shutil.copy(path_origin, temp_path)

        with open(temp_path, 'a') as temp_file:
            temp_file.write(data + "\n")
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_path, path_origin)

    
    def get_transaction_log(self, message):
        #implementar en cada queryFile
        pass


    def simulate_failure(self):
        #para asegurarme que ya me conecte al healthchecker
        time.sleep(8)
        print("Me caigo")
        print(f"Seq Number {self.actual_seq_number} \n")
        print(f"Dict: {self.last_seq_number_by_filter} \n")
        self.running = False
        
        # return
        print("Simulando caída del contenedor...")
        #sys.stdout.flush()  # Asegúrate de vaciar el buffer
        self.service_queues.close_connection()

        print("cerre las colas de rabbit")

        os._exit(1)
        print("No debería llegar acá porque estoy muerto")
    
    def recover_from_transaction_log(self):
        #print("Debe implementarla los query files")
        pass