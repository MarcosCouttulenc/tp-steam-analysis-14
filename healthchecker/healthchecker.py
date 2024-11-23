import socket
import threading
from time import sleep
from common.protocol_healthchecker import ProtocolHealthChecker


LISTEN_BACKLOG = 100

class HealthChecker:
    def __init__(self, listen_port, connect_port, connect_ip):
        self.connect_port = connect_port
        self.listen_port = listen_port
        self.connect_ip = connect_ip
        self.running = True


    def start(self):
        processes = []

        # Lanzamos proceso para atender nodos que van a depender de mi
        accept_new_connections_process = threading.Thread(
            target = self.process_accept_new_connection 
        )
        accept_new_connections_process.start()
        processes.append(accept_new_connections_process)

        # Margen para que todos los healthcheckers se pongan a aceptar conexiones
        sleep(10)

        # Lanzamos el proceso que se conecta con el nodo que va a ser 
        # mi healthchecker
        my_healthchecker_process = threading.Thread(
            target = self.process_my_healthchecker 
        )
        my_healthchecker_process.start()
        processes.append(my_healthchecker_process)

        # Esperamos a que los procesos finalicen y joineamos
        for process in processes:
            process.join()
    

    def process_my_healthchecker(self):
        # Conectamos al socket del mi healthchecker, si algo sale mal me
        # vuelvo a intentar conectar
        while self.running:
            skt_next_healthchecker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            skt_next_healthchecker.connect((self.connect_ip, self.connect_port))
            
            # comienza la comunicacion
            healthchecker_protocol = ProtocolHealthChecker(skt_next_healthchecker)

            # ciclo de checkeo de health
            while healthchecker_protocol.wait_for_health_check():
                healthchecker_protocol.healt_check_ack()


    def process_accept_new_connection(self):
        # Esperamos que los nodos que tengo que cuidar se conecten a mi.

        skt_accept_connections = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt_accept_connections.bind(('', self.listen_port))
        skt_accept_connections.listen(LISTEN_BACKLOG)

        new_connection_skts = []

        while self.running:
            new_connection_skt = skt_accept_connections.accept()

            healthcheck_container_process = threading.Thread(
                target = self.process_healthcheck_container,
                args = (new_connection_skt)
            ) 
            healthcheck_container_process.start()
            new_connection_skts.append(healthcheck_container_process)

        # Esperamos a que los procesos finalicen y joineamos
        for process in new_connection_skts:
            process.join()

    
    def process_healthcheck_container(self, socket):
        healthchecker_protocol = ProtocolHealthChecker(socket)

        while True:
            if (not healthchecker_protocol.health_check_ask()):
                break

            if (not healthchecker_protocol.wait_for_node_ack()):
                break

            sleep(5)
