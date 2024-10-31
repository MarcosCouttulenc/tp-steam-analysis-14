import logging
logging.basicConfig(level=logging.CRITICAL)
import errno
import socket
import time
import threading

from middleware.queue import ServiceQueues
from common.message import MessageGameInfo
from common.message import MessageEndOfDataset
from common.message import Message
from common.protocol import Protocol

CHANNEL_NAME =  "rabbitmq"

FALSE_STRING = "False"
TRUE_STRING = "True"
LISTEN_BACKLOG = 100

def string_to_boolean(string_variable):
    if string_variable == TRUE_STRING:
        return True
    elif string_variable == FALSE_STRING:
        return False
    else:
        print(f"\n\n\n VARIABLE: {string_variable} \n\n\n")
        raise Exception("Variable booleana incorrecta")

class GameWorker:
    #cant_next= "cant_positivas,cant_query5_reducers"
    def __init__(self, queue_name_origin_eof, queue_name_origin, queues_name_destiny, cant_next, cant_slaves, is_master, ip_master, port_master):
        
        self.running = True
        self.cant_slaves = int(cant_slaves)-1
        self.service_queues_filter = ServiceQueues(CHANNEL_NAME)
        #self.service_queues_eof = ServiceQueues(CHANNEL_NAME)
        self.queues_destiny = self.init_queues_destiny(queues_name_destiny, cant_next)
        self.queue_name_origin_eof = queue_name_origin_eof
        self.queue_name_origin = queue_name_origin

        self.is_master = string_to_boolean(is_master)
        self.ip_master = ip_master
        self.port_master = int(port_master)
        self.running_threads = []
    
    def init_queues_destiny(self, queues_name_destiny, cant_next):
        queues_name_destiny_list = queues_name_destiny.split(',')
        cant_next_list = cant_next.split(',')
        rta = {}
        for i in range(len(queues_name_destiny_list)):
            rta[queues_name_destiny_list[i]] = int(cant_next_list[i])- 1
        return rta


    def start(self):
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
            #print(f"cantidad de esclavos ")

            while self.running:
                try:
                    #por cada conexion, lanzamos el proceso para el manejo de eof de ese slave
                    print("por aceptar una conexion con slave")
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


    ## Proceso master eof handler
    ## --------------------------------------------------------------------------------      
    def process_control_master_eof_handler(self, socket_master_slave, socket_master_slave_addr, barrier):
        #print("Nuevo slave conectado en :", socket_master_slave_addr)
        protocol = Protocol(socket_master_slave)
        
        try:
            while self.running:
                #print(f"Esperando un EOF desde {socket_master_slave_addr}")
                msg = protocol.receive()

                if (msg == None):
                    break

                print(f"Recibe un EOF desde {socket_master_slave_addr}")
                barrier.wait()

                #print(f"Se notifica a {socket_master_slave_addr} que ya llegaron todos los EOFs")
                protocol.send(msg)
        except OSError as e:
            if e.errno == errno.EBADF:  # Bad file descriptor, server socket closed
                logging.critical('SOCKET CERRADO - ACCEPT_NEW_CONNECTIONS')
                return None
            else:
                raise
        


    ## Proceso slave eof handler
    ## --------------------------------------------------------------------------------
    def process_control_slave_eof_handler(self):
        self.service_queues_eof = ServiceQueues(CHANNEL_NAME)
        print(f"[SLAVE] Por conectarme a {str(self.ip_master)}:{str(self.port_master)}")
        
        time.sleep(10)
        self.socket_slave = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_slave.connect((self.ip_master, self.port_master))

        while self.running:
            self.service_queues_eof.pop_non_blocking(self.queue_name_origin_eof, self.process_message_slave_eof)

    def process_message_slave_eof(self, ch, method, properties, message: Message):
        print("ME LLEGO EOF DE LA QUEUE DE EOFS")

        #Le notificamos al master el eof
        protocol = Protocol(self.socket_slave)
        
        print(f"Envio un EOF al master del clienteId: {message.get_client_id()}")
        protocol.send(message)

        self.service_queues_eof.ack(ch, method)

        #Nos quedamos esperando que el master nos notifique que se termino de procesar.
        _ = protocol.receive()
        

        msg_eof = MessageEndOfDataset.from_message(message)
        
        if (msg_eof.is_last_eof()):
            print(f"Envio un EOF final al proximo paso para el clienteId: {message.get_client_id()}")
            self.send_eofs(msg_eof)

    def send_eofs(self, msg_eof):
        for queue_name, cant_next in self.queues_destiny.items():
            self.send_eofs_to_queue(queue_name, cant_next, msg_eof)

    def send_eofs_to_queue(self, queue_name, queue_cant, msg_eof):
        msg_eof.set_not_last_eof()

        for _ in range(queue_cant-1):
            self.service_queues_eof.push(queue_name, msg_eof)
            
        msg_eof.set_last_eof()
        self.service_queues_eof.push(queue_name, msg_eof)


    ## Proceso filter
    ## --------------------------------------------------------------------------------
    def process_filter(self):
        while self.running:
            self.service_queues_filter.pop(self.queue_name_origin, self.process_message)
    
    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():
            self.handle_eof(message, ch, method)
            return
        
        msg_game_info = MessageGameInfo.from_message(message)
        
        if self.validate_game(msg_game_info.game):
            self.forward_message(message)

        self.service_queues_filter.ack(ch, method)
    
    def handle_eof(self, message, ch, method):
        print("me llego EOF DE LA QUEUED DE DATA, lo pusheo a la queue de EOFS")
        self.service_queues_filter.push(self.queue_name_origin_eof, message)
        self.service_queues_filter.ack(ch, method)

    def validate_game(self, game):
        return False

    def forward_message(self, message):
        message_to_send = self.get_message_to_send(message)
        for queue_name_destiny in self.queues_destiny.keys():
            self.service_queues_filter.push(queue_name_destiny, message_to_send)
        
    def get_message_to_send(self, message):
        return message


    
