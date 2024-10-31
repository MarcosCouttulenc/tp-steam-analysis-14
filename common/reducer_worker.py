import logging
import errno
import socket
import time
import threading
logging.basicConfig(level=logging.CRITICAL)
from middleware.queue import ServiceQueues
from common.message import Message
from common.message import MessageGameInfo
from common.message import MessageQueryTwoFileUpdate
from common.message import MessageEndOfDataset
from common.protocol import Protocol

CHANNEL_NAME =  "rabbitmq"
LISTEN_BACKLOG = 100
FALSE_STRING = "False"
TRUE_STRING = "True"

def string_to_boolean(string_variable):
    if string_variable == TRUE_STRING:
        return True
    elif string_variable == FALSE_STRING:
        return False
    else:
        print(f"\n\n\n VARIABLE: {string_variable} \n\n\n")
        raise Exception("Variable booleana incorrecta")

class ReducerWorker:
    def __init__ (self,queue_name_origin_eof, queue_name_origin, queues_name_destiny_str, cant_slaves, is_master, ip_master, port_master):
        self.queue_name_origin = queue_name_origin
        self.queues_name_destiny = queues_name_destiny_str.split(",")
        self.running = True
        self.service_queues = ServiceQueues(CHANNEL_NAME)
        #self.service_queues_filter = ServiceQueues(CHANNEL_NAME)
        self.service_queues_eof = ServiceQueues(CHANNEL_NAME)
        
        self.buffer = self.init_buffer()

        self.queue_name_origin_eof = queue_name_origin_eof
        self.cant_slaves = int(cant_slaves)-1
        self.is_master = string_to_boolean(is_master)
        self.ip_master = ip_master
        self.port_master = int(port_master)
        self.running_threads = []


    def start(self):
        if (not self.is_master):
            # Lanzamos proceso filter
            reducer_process = threading.Thread(
                target = self.process_reducer 
            )
            reducer_process.start()
            self.running_threads.append(reducer_process)

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


    ## Proceso master eof handler
    ## --------------------------------------------------------------------------------      
    def process_control_master_eof_handler(self, socket_master_slave, socket_master_slave_addr, barrier):
        #print("Nuevo slave conectado en :", socket_master_slave_addr)
        protocol = Protocol(socket_master_slave)
        
        try:
            while self.running:
                print(f"[MASTER] Esperando un EOF desde {socket_master_slave_addr}")
                msg = protocol.receive()

                if (msg == None):
                    print(f"[MASTER] Recibe un None desde {socket_master_slave_addr}")
                    break

                print(f"[MASTER] Recibe un EOF desde {socket_master_slave_addr} idCliente: {msg}")
                barrier.wait()

                print(f"[MASTER] Se notifica a {socket_master_slave_addr} que ya llegaron todos los EOFs")
                protocol.send(msg)
        except OSError as e:
            if e.errno == errno.EBADF:  # Bad file descriptor, server socket closed
                print(f"[MASTER] SOCKET CERRADO - ACCEPT_NEW_CONNECTIONS")
                logging.critical('SOCKET CERRADO - ACCEPT_NEW_CONNECTIONS')
                return None
            else:
                raise
        


    ## Proceso slave eof handler
    ## --------------------------------------------------------------------------------
    def process_control_slave_eof_handler(self):
        #self.service_queues_eof = ServiceQueues(CHANNEL_NAME)
        #print(f"[SLAVE] Por conectarme a {str(self.ip_master)}:{str(self.port_master)}")
        
        time.sleep(10)
        self.socket_slave = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_slave.connect((self.ip_master, self.port_master))

        while self.running:
            self.service_queues_eof.pop_non_blocking(self.queue_name_origin_eof, self.process_message_slave_eof)

    def process_message_slave_eof(self, ch, method, properties, message: Message):
        print(f"[SLAVE] EMPIEZO CICLO DE EOFS DE CLIENTE, ME LLEGO EOF DE LA QUEUE DE EOFS de cliente: {message.get_client_id()}")

        if message == None:
            return
        
        #Le notificamos al master el eof
        protocol = Protocol(self.socket_slave)
        
        print(f"[SLAVE] Envio un EOF al master del clienteId: {message.get_client_id()}, msj: {message.message_payload}")
        bytes_sent = protocol.send(message)
        
        print(f"[SLAVE] Enviado un EOF al master del clienteId: {message.get_client_id()}; cant de bytes enviados: {bytes_sent}")

        self.service_queues_eof.ack(ch, method)

        #Nos quedamos esperando que el master nos notifique que se termino de procesar.
        _ = protocol.receive()

        msg_eof = MessageEndOfDataset.from_message(message)
        
        if (msg_eof.is_last_eof()):
            print(f"[SLAVE] Envio un EOF final al proximo paso para el clienteId: {message.get_client_id()}")
            self.send_eofs(msg_eof)

        time.sleep(4)
        

    def send_eofs(self, msg_eof):
        if  msg_eof.is_last_eof():
            print("push last eof")
        
        if self.buffer_contains_items():
           # print("Envio los ultimos datos")
            self.send_buffer_to_file(msg_eof.get_client_id())


    ## Proceso reducer
    ## --------------------------------------------------------------------------------

    def process_reducer(self):
        while self.running:
            self.service_queues.pop(self.queue_name_origin, self.process_message)

    def update_buffer(self, message: Message):
        return 0

    def send_buffer_to_file(self, client_id):
        return 0
    
    def init_buffer(self):
        return 0
    
    def buffer_contains_items(self):
        return True

    def buffer_is_full(self):
        return True

    def process_message(self, ch, method, properties, message: Message):
        if message.is_eof():
            self.handle_eof(ch, method, properties, message)
            return

        #print(f"voy a actualizar con: {message.message_payload}")

        #print("antes de actualizar buffer:")
        #print(self.buffer)
        self.update_buffer(message)

        #print("despues de actualizar buffer:")
        #print(self.buffer)

        if self.buffer_is_full():
            self.send_buffer_to_file(message.get_client_id())

        self.service_queues.ack(ch, method)

    def handle_eof(self, ch, method, properties, message: Message):
        #print("[FILTER] me llego EOF DE LA QUEUED DE DATA, lo pusheo a la queue de EOFS")
        self.service_queues.push(self.queue_name_origin_eof, message)
        self.service_queues.ack(ch, method)
    
    