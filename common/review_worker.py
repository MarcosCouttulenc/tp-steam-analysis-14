import logging
logging.basicConfig(level=logging.CRITICAL)
import errno
import socket
import time
import threading

from middleware.queue import ServiceQueues
from common.message import MessageReviewInfo
from common.message import MessageEndOfDataset
from common.message import Message
from common.protocol import Protocol
from common.protocol_healthchecker import ProtocolHealthChecker, get_container_name


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

class ReviewWorker:
    def __init__(self, queue_name_origin_eof, queue_name_origin, queues_name_destiny, cant_next, cant_slaves, 
                 is_master, ip_master, port_master, ip_healthchecker, port_healthchecker, id):
        self.queue_name_origin = queue_name_origin
        self.running = True
        self.service_queue_filter = ServiceQueues(CHANNEL_NAME)
        self.queues_destiny = self.init_queues_destiny(queues_name_destiny, cant_next)

        self.queue_name_origin_eof = queue_name_origin_eof
        self.cant_slaves = int(cant_slaves)-1
        self.is_master = string_to_boolean(is_master)
        self.ip_master = ip_master
        self.port_master = int(port_master)
        self.running_threads = []

        self.ip_healthchecker = ip_healthchecker
        self.port_healthchecker = int(port_healthchecker)
        
        self.id = id
    
    def init_queues_destiny(self, queues_name_destiny, cant_next):
        queues_name_destiny_list = queues_name_destiny.split(',')
        cant_next_list = cant_next.split(',')
        rta = {}
        for i in range(len(queues_name_destiny_list)):
            rta[queues_name_destiny_list[i]] = int(cant_next_list[i])
        return rta


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
            #print(f"cantidad de esclavos ")

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
        time.sleep(10)

        while self.running:
            skt_next_healthchecker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            skt_next_healthchecker.connect((self.ip_healthchecker, self.port_healthchecker))
            
            # comienza la comunicacion
            healthchecker_protocol = ProtocolHealthChecker(skt_next_healthchecker)

            # le envio el nombre de mi container
            if (not healthchecker_protocol.send_container_name(get_container_name())):
                continue

            # ciclo de checkeo de health
            while healthchecker_protocol.wait_for_health_check():
                healthchecker_protocol.health_check_ack()


    ## Proceso master eof handler
    ## --------------------------------------------------------------------------------      
    def process_control_master_eof_handler(self, socket_master_slave, socket_master_slave_addr, barrier):
        #print("Nuevo slave conectado en :", socket_master_slave_addr)
        protocol = Protocol(socket_master_slave)

        try:
            while self.running:
               #print(f"[MASTER] Esperando un EOF desde {socket_master_slave_addr}")
                msg = protocol.receive()

                if (msg == None):
                    print(f"[MASTER] Recibe un None desde {socket_master_slave_addr}")
                    break

                #print(f"[MASTER] Recibe un EOF desde {socket_master_slave_addr} idCliente: {msg}")
                barrier.wait()

                #print(f"[MASTER] Se notifica a {socket_master_slave_addr} que ya llegaron todos los EOFs")
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
        #print(f"[SLAVE] Por conectarme a {str(self.ip_master)}:{str(self.port_master)}")
        
        time.sleep(10)
        self.socket_slave = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_slave.connect((self.ip_master, self.port_master))

        while self.running:
            self.service_queues_eof.pop_non_blocking(self.queue_name_origin_eof, self.process_message_slave_eof)

    def process_message_slave_eof(self, ch, method, properties, message: Message):
        #print(f"[SLAVE] EMPIEZO CICLO DE EOFS DE CLIENTE, ME LLEGO EOF DE LA QUEUE DE EOFS de cliente: {message.get_client_id()}")

        if message == None:
            return
        
        #Le notificamos al master el eof
        protocol = Protocol(self.socket_slave)
        
        #print(f"Envio un EOF al master del clienteId: {message.get_client_id()}")
        bytes_sent = protocol.send(message)
        
        #print(f"[SLAVE] Enviado un EOF al master del clienteId: {message.get_client_id()}; cant de bytes enviados: {bytes_sent}")

        self.service_queues_eof.ack(ch, method)

        #Nos quedamos esperando que el master nos notifique que se termino de procesar.
        _ = protocol.receive()
        

        msg_eof = MessageEndOfDataset.from_message(message)
        
        if (msg_eof.is_last_eof()):
            #print(f"Envio un EOF final al proximo paso para el clienteId: {message.get_client_id()}")
            self.send_eofs(msg_eof)

        time.sleep(4)

    def send_eofs(self, msg_eof):
        for queue_name, cant_next in self.queues_destiny.items():
            self.send_eofs_to_queue(queue_name, cant_next, msg_eof)

    def send_eofs_to_queue(self, queue_name, queue_cant, msg_eof):
        msg_eof.set_not_last_eof()

        for id in range(2, queue_cant):
            queue_name_destiny = f"{queue_name}-{id}"

            if (id == queue_cant):
                msg_eof.set_last_eof()
            
            self.service_queues_eof.push(queue_name_destiny, msg_eof)

    ## Proceso filter
    ## --------------------------------------------------------------------------------
    def process_filter(self):
        while self.running:
            queue_name_origin_id = f"{self.queue_name_origin}-{self.id}"
            #print(f"Voy a popear de {queue_name_origin_id}")
            self.service_queue_filter.pop(queue_name_origin_id, self.process_message)

    def process_message(self, ch, method, properties, message: Message):
        #print(f"Me llego un mensaje de la cola {self.queue_name_origin} y lo popie ")

        if message.is_eof():
            #print(f"EOF de la cola {self.queue_name_origin}")
            self.handle_eof(message, ch, method)
            return
        
        msg_review_info = MessageReviewInfo.from_message(message)
        
       # print("Voy a validar el review")
        if self.validate_review(msg_review_info.review):
            #print("Review validado")
            self.forward_message(message)

        #print("Voy a hacer ack")
        self.service_queue_filter.ack(ch, method)
        #print("Hice ack")
    
    def handle_eof(self, message, ch, method):
        #print("me llego EOF DE LA QUEUED DE DATA, lo pusheo a la queue de EOFS")
        self.service_queue_filter.push(self.queue_name_origin_eof, message)
        self.service_queue_filter.ack(ch, method)

    def validate_review(self, review):
        return False

    def forward_message(self, message):
        message_to_send = self.get_message_to_send(message)
        msg_review_info = MessageReviewInfo.from_message(message)

        '''
        for queue_name_destiny in self.queues_destiny.keys():
            self.service_queue_filter.push(queue_name_destiny, message_to_send)
        '''

        for queue_name_next, cant_queue_next in self.queues_destiny.items():
            queue_next_id = ( round(int(msg_review_info.review.game_id) / 10 )% int(cant_queue_next)) + 1 
            #print(f"El id de la cola que voy a pushear es {queue_next_id}")

            if queue_next_id == 1:
                    queue_next_id += 1

            queue_name_destiny = f"{queue_name_next}-{str(queue_next_id)}"
            #print(f"Envio mensaje a {queue_name_destiny}")
            self.service_queues_filter.push(queue_name_destiny, message_to_send)

    def get_message_to_send(self, message):
        return message


    
