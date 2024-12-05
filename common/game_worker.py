import logging
logging.basicConfig(level=logging.CRITICAL)
import errno
import socket
import time
import threading
import os
import multiprocessing
import signal

from common.sharding import Sharding
from middleware.queue import ServiceQueues
from common.message import MessageGameInfo
from common.message import MessageEndOfDataset
from common.message import MessageInvalidClient, MESSAGE_MASTER_INVALID_CLIENT
from common.message import MessageFinishedClient, MESSAGE_MASTER_FINISHED_CLIENT
from common.message import Message, string_to_boolean
from common.protocol import Protocol
from common.protocol_healthchecker import ProtocolHealthChecker, get_container_name
from common.message import Message


CHANNEL_NAME =  "rabbitmq"
LISTEN_BACKLOG = 100

PATH_FILE_STATE = "worker-state.txt"

AVAILABLE_CLIENT_ID = -1

class GameWorker:
    def __init__(self, queue_name_origin_eof, queue_name_origin, queues_name_destiny, cant_next, cant_slaves, 
            is_master, ip_master, port_master, ip_healthchecker, port_healthchecker, id, path_status_info):
        
        self.running = True
        self.cant_slaves = int(cant_slaves)-1
        self.service_queues_filter = ServiceQueues(CHANNEL_NAME)
        self.service_queues_eof = ServiceQueues(CHANNEL_NAME)
        self.queues_destiny = self.init_queues_destiny(queues_name_destiny, cant_next)
        self.queue_name_origin_eof = queue_name_origin_eof
        self.queue_name_origin = queue_name_origin

        self.is_master = string_to_boolean(is_master)
        self.ip_master = ip_master
        self.port_master = int(port_master)
        self.running_threads = []

        self.ip_healthchecker = ip_healthchecker
        self.port_healthchecker = int(port_healthchecker)
        self.current_client_id_processing = multiprocessing.Value('i', AVAILABLE_CLIENT_ID)
        self.current_client_id_processing_lock = multiprocessing.Lock()

        self.id = id
        self.actual_seq_number = 0
        self.last_seq_number_by_filter = {}
        self.path_status_info = f"{path_status_info}/state{str(self.id)}.txt"

        self.cant_mensajes_procesados = 0

        manager = multiprocessing.Manager()
        self.finished_clients = manager.dict()

        self.clients_pushed_eofs = {}
        
        self.init_worker_state()
        self.init_signals()

    def init_signals(self):
        signal.signal(signal.SIGTERM, self.stop)

    def stop(self, signum, frame):
        logging.info("action: stop | result: in_progress")
        
        self.running = False
        self.service_queues_eof.close_connection()
        self.service_queues_filter.close_connection()

        logging.info("action: stop | result: success")

    

    def init_queues_destiny(self, queues_name_destiny, cant_next):
        queues_name_destiny_list = queues_name_destiny.split(',')
        cant_next_list = cant_next.split(',')
        rta = {}
        for i in range(len(queues_name_destiny_list)):
            rta[queues_name_destiny_list[i]] = int(cant_next_list[i])
        return rta


    def init_worker_state(self):
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
                    print(f"Linea de EOFs: {line}")
                    data = line.split("|")
                    print(f"Data de EOFs: {data}")
                    
                    for clients_pushed_eofs_data in data:
                        clients_pushed_eofs_info = clients_pushed_eofs_data.split(",")
                        self.clients_pushed_eofs[clients_pushed_eofs_info[0]] = clients_pushed_eofs_info[1]

        print("Me levanto")
        print(f"Seq Number {self.actual_seq_number} \n")
        print(f"Dict: {self.last_seq_number_by_filter} \n")


    def start(self):
        # Lanzamos proceso para conectarnos al health checker
        connect_health_checker = threading.Thread(
            target = self.process_connect_health_checker 
        )
        connect_health_checker.start()
        self.running_threads.append(connect_health_checker)

        
        if (not self.is_master):
            # Lanzamos proceso filter
            filter_process = threading.Thread(
                target = self.process_filter 
            )
            filter_process.start()
            self.running_threads.append(filter_process)

            # Lanzamos el proceso para controlar al slave
            control_eof_handler_process = threading.Thread(
                target = self.process_control_slave_eof_handler
            )
            control_eof_handler_process.start()
            self.running_threads.append(control_eof_handler_process)
        else:
            # Lanzamos el proceso para aceptar conexiones desde el master
            socket_master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_master.bind(('', self.port_master))
            socket_master.listen(LISTEN_BACKLOG)
            barrier = threading.Barrier(self.cant_slaves)

            while self.running:
                try:
                    #por cada conexion, lanzamos el proceso para el manejo de eof de ese slave
                    #print("por aceptar una conexion con slave")
                    socket_master_slave, socket_master_slave_addr = socket_master.accept()

                    socket_master_slave_process = threading.Thread(
                        target = self.process_control_master_eof_handler, 
                        args = (socket_master_slave, socket_master_slave_addr, barrier)
                    ) 
                    socket_master_slave_process.start()
                    self.running_threads.append(socket_master_slave_process)
                except OSError as e:
                    if e.errno == errno.EBADF:  # Bad file descriptor, server socket closed
                        return None
                    else:
                        raise

        for process in self.running_threads:
            process.join()


    ## Proceso de conexion con health checker
    ## --------------------------------------------------------------------------------      
    def process_connect_health_checker(self):
        time.sleep(5)

        while self.running:
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
        


    ## Proceso master eof handler
    ## --------------------------------------------------------------------------------      
    def process_control_master_eof_handler(self, socket_master_slave, socket_master_slave_addr, barrier):
        protocol = Protocol(socket_master_slave)
        
        while self.running:
            try:
                msg = protocol.receive()

                if (msg == None):
                    print(f"[MASTER] None recibido desde {str(socket_master_slave_addr)}")
                    break

                if (msg.get_client_id() in self.finished_clients.keys()):
                    msg_finished_client = MessageFinishedClient(msg.get_client_id())
                    protocol.send(msg_finished_client)
                    continue
                
                with self.current_client_id_processing_lock:

                    # si no se estaba procesando el eof de ningun cliente, se comienza a procesar el de ese cliente y se setea la variable
                    if int(self.current_client_id_processing.value) == AVAILABLE_CLIENT_ID:
                        print(f"[MASTER] empezamos a recibir del cliente: {msg.get_client_id()}")
                        self.current_client_id_processing.value = int(msg.get_client_id())

                    #si el eof no es del cliente que estamos procesando ahora, lo devolvemos
                    if int(msg.get_client_id()) != int(self.current_client_id_processing.value):
                        msg_invalid_client = MessageInvalidClient(msg.get_client_id())
                        protocol.send(msg_invalid_client)
                        continue
                
                print(f"[MASTER] eof recibido: {msg} desde {str(socket_master_slave_addr)} clientId actual: {str(self.current_client_id_processing.value)}")
                barrier.wait()

                if not str(self.current_client_id_processing.value) in self.finished_clients.keys():
                    self.finished_clients[str(self.current_client_id_processing.value)] = 0

                # de nuevo no se esta procesando el eof de ningun cliente, se resetea la variable
                with self.current_client_id_processing_lock:
                    self.current_client_id_processing.value = AVAILABLE_CLIENT_ID
                

                protocol.send(msg)
            except (ConnectionResetError, ConnectionError):
                print(f"[MASTER] Slave caido, vuelvo a intentar esperar un msj")
                time.sleep(5)
                continue
                
            except OSError as e:
                if e.errno == errno.EBADF:  # Bad file descriptor, server socket closed
                    logging.critical('SOCKET CERRADO - ACCEPT_NEW_CONNECTIONS')
                    return None
                else:
                    raise
        

    ## Proceso slave eof handler
    ## --------------------------------------------------------------------------------
    def process_control_slave_eof_handler(self):
        time.sleep(5)

        self.socket_slave = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_slave.connect((self.ip_master, self.port_master))

        while self.running:
            self.service_queues_eof.pop_non_blocking(self.queue_name_origin_eof, self.process_message_slave_eof)


    def process_message_slave_eof(self, ch, method, properties, message: Message):
        if message == None:
            return
        
        print(f"[SLAVE] por enviar el eof: {message}, soy el id {self.id}")
        
        # Le notificamos al master el eof
        protocol = Protocol(self.socket_slave)
        
        _ = protocol.send(message)

        #self.service_queues_eof.ack(ch, method)
        

        # Nos quedamos esperando que el master nos notifique que se termino de procesar.
        msg_master = protocol.receive()
        
        # Si el master nos indica que el cliente ya fue procesado, ACK al mensaje.
        if (msg_master.message_type == MESSAGE_MASTER_FINISHED_CLIENT):
            self.service_queues_eof.ack(ch, method)
            return
        
        # Si el master nos indica que el cliente que esta procesando el EOF es otro, devolvemos el mensaje.
        if (msg_master.message_type == MESSAGE_MASTER_INVALID_CLIENT):
            self.service_queues_eof.push(self.queue_name_origin_eof, message)
            self.service_queues_eof.ack(ch, method)
            return

        # Sino, reenviamos el EOF si corresponde.
        print(f"[SLAVE] me devolvio el eof: {message}")
        msg_eof = MessageEndOfDataset.from_message(message)
        
        #if (msg_eof.is_last_eof()):
        print(f"[SLAVE] y lo reenvio")
        self.send_eofs(msg_eof)
        

        self.service_queues_eof.ack(ch, method)

        time.sleep(4)
        
        
    def send_eofs(self, msg_eof):
        for queue_name, cant_next in self.queues_destiny.items():
            self.send_eofs_to_queue(queue_name, cant_next, msg_eof)

    def send_eofs_to_queue(self, queue_name, queue_cant, msg_eof):
        msg_eof.set_not_last_eof()
        
        for id in range(1, queue_cant+1):
            queue_name_destiny = f"{queue_name}-{id}"
            
            if (id == queue_cant):
                msg_eof.set_last_eof()
            
            msg_eof.set_message_id(self.get_new_message_id())
            
            self.service_queues_eof.push(queue_name_destiny, msg_eof)


    ## Proceso filter
    ## --------------------------------------------------------------------------------
    def process_filter(self):
        while self.running:
            try:
                queue_name_origin_id = f"{self.queue_name_origin}-{self.id}"
                self.service_queues_filter.pop(queue_name_origin_id, self.process_message)
            except:
                print("Cerrando worker")
    
    def process_message(self, ch, method, properties, message: Message):
        #print(f"Me llega mensaje con id: {message.get_message_id()} \n")
        #print(f"Dict: {self.last_seq_number_by_filter} \n")

        # Chequeamos si el mensaje ya fue procesado.
        if self.message_was_processed(message):
            print(f"El mensaje {message.get_message_id()} ya fue procesado \n")
            print(f"Dict: {self.last_seq_number_by_filter} \n")
            self.service_queues_filter.ack(ch, method)
            return
        
        # Chequeamos si es un eof
        if message.is_eof():
            self.handle_eof(message, ch, method)
            return
        
        msg_game_info = MessageGameInfo.from_message(message)

        # Lo reenviamos a la proxima instancia si es un mensaje valido
        if self.validate_game(msg_game_info.game):
            self.forward_message(message)

        # Actualizamos el diccionario
        self.last_seq_number_by_filter[msg_game_info.get_filterid_from_message_id()] = msg_game_info.get_seqnum_from_message_id()

        # Bajamos la informacion a disco
        self.save_state_in_disk()


        #print(f"Voy procesando {self.cant_mensajes_procesados}")
        #if (self.cant_mensajes_procesados == 1000 and int(self.id) == 1):
        #    self.simulate_failure()

        self.cant_mensajes_procesados += 1


        self.service_queues_filter.ack(ch, method)

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
        self.service_queues_eof.close_connection()
        self.service_queues_filter.close_connection()

        print("cerre las colas de rabbit")

        os._exit(1)
        print("No debería llegar acá porque estoy muerto")
    
    def handle_eof(self, message: Message, ch, method):

        # Si ya proceso un eof de ese cliente lo descartamos
        client_id = str(message.get_client_id())
        if client_id in self.clients_pushed_eofs.keys():
            self.service_queues_filter.ack(ch, method)
            return
        
        self.service_queues_filter.push(self.queue_name_origin_eof, message)
        self.last_seq_number_by_filter[message.get_filterid_from_message_id()] = message.get_seqnum_from_message_id()
        self.clients_pushed_eofs[client_id] = True

        self.save_state_in_disk()
        
        self.service_queues_filter.ack(ch, method)

    def validate_game(self, game):
        return False

    def forward_message(self, message):
        message_to_send = self.get_message_to_send(message)

        msg_game_info = MessageGameInfo.from_message(message)

        message_to_send.set_message_id(self.get_new_message_id())

        for queue_name_next, cant_queue_next in self.queues_destiny.items():
            queue_next_id = Sharding.calculate_shard(msg_game_info.game.id, cant_queue_next)
            queue_name_destiny = f"{queue_name_next}-{str(queue_next_id)}"
            self.service_queues_filter.push(queue_name_destiny, message_to_send)
            
    def get_message_to_send(self, message):
        return message

    def get_new_message_id(self):
        self.actual_seq_number += 1
        return f"F{str(self.id)}_M{str(self.actual_seq_number)}"

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
        clients_pushed_eofs_data = "|".join(f"{key},{value}" for key, value in self.clients_pushed_eofs.items())
        data = f"{str(self.actual_seq_number)}|{last_seq_number_by_filter_data}\n{clients_pushed_eofs_data}"
        temp_path = self.path_status_info + '.tmp'
        
        with open(temp_path, 'w') as temp_file:
            temp_file.write(data)
            temp_file.flush() # Forzar escritura al sistema operativo
            os.fsync(temp_file.fileno()) # Asegurar que se escriba físicamente en disco

        os.replace(temp_path, self.path_status_info)