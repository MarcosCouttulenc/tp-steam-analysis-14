import socket
import threading
from time import sleep
from common.protocol_healthchecker import ProtocolHealthChecker
import docker
import os

LISTEN_BACKLOG = 100
TIME_BETWEEN_HEALTH_CHECKS = 5


def get_container_name():
    # Leer el ID del contenedor actual
    with open('/etc/hostname', 'r') as f:
        container_id = f.read().strip()

    # Conectar al demonio de Docker
    client = docker.from_env()

    # Buscar el contenedor actual por su ID
    container = client.containers.get(container_id)

    # Retornar el nombre del contenedor
    return container.name

class HealthChecker:
    def __init__(self, listen_port, connect_port, connect_ip):
        self.connect_port = int(connect_port)
        self.listen_port = int(listen_port)
        self.connect_ip = connect_ip
        self.running = True
        self.docker_client = docker.DockerClient(base_url="unix://var/run/docker.sock")
        self.file_name_connected_containers = "connected_containers.txt"


    def restart_node(self, container_name):
        # Reiniciamos el nodo que se cayo
        try:
            print(f"Reiniciando contenedor {container_name}")
            container_name = self.docker_client.containers.get(container_name)
            container_name.restart()
            print(f"Contenedor {container_name} reiniciado")
        except Exception as e:
            print(f"Error reiniciando contenedor {container_name}: {e}")

    def is_node_running(self, container_name):
        try:
            container = self.docker_client.containers.get(container_name)
            return container.status == "running"
        except docker.errors.NotFound:
            return False
        

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

            # le envio el nombre de mi container
            if (not healthchecker_protocol.send_container_name(get_container_name())):
                continue

            # ciclo de checkeo de health
            while healthchecker_protocol.wait_for_health_check():
                healthchecker_protocol.health_check_ack()

    def process_accept_new_connection(self):
        print(f"[process_accept_new_connection] Iniciando...")

        # Apenas me levanto, lo primero que hago es revivir todos los nodos que dependian de mi (si es que alguno muri).
        my_containers_name = []
        if (os.path.isfile(self.file_name_connected_containers)):
            print("[process_accept_new_connection] encontro el archivo")
            with open(self.file_name_connected_containers, "r") as file:
                for line in file.readlines():
                    my_containers_name.append(line.strip())

        print(f"[process_accept_new_connection] se van a levantar {len(my_containers_name)} containers")
        for container_name in my_containers_name:
            if (not self.is_node_running(container_name)):
                self.restart_node(container_name)

        if (os.path.isfile(self.file_name_connected_containers)):
            os.remove(self.file_name_connected_containers)


        # Esperamos que los nodos que tengo que cuidar se conecten a mi.
        print(f"[process_accept_new_connection] Aceptando conexiones...")
        skt_accept_connections = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt_accept_connections.bind(('', self.listen_port))
        skt_accept_connections.listen(LISTEN_BACKLOG)

        new_connection_skts = []

        while self.running:
            new_connection_skt, address = skt_accept_connections.accept()

            healthcheck_container_process = threading.Thread(
                target = self.process_healthcheck_container,
                args = (new_connection_skt, address)
            ) 
            healthcheck_container_process.start()
            new_connection_skts.append(healthcheck_container_process)

        # Esperamos a que los procesos finalicen y joineamos
        for process in new_connection_skts:
            process.join()

    
    def process_healthcheck_container(self, socket, address):
        healthchecker_protocol = ProtocolHealthChecker(socket)

        # recibo el nombre del container a levantar
        container_name_msg = healthchecker_protocol.receive_container_name()

        if (container_name_msg == None):
            return

        container_name = container_name_msg.container_name

        with open(self.file_name_connected_containers, "w") as file:
            file.write(container_name)

        while True:
            try:
                if (not healthchecker_protocol.health_check_ask()):
                    self.restart_node(container_name)
                    break

                if (not healthchecker_protocol.wait_for_node_ack()):
                    self.restart_node(container_name)
                    break

                sleep(TIME_BETWEEN_HEALTH_CHECKS)
            except Exception as e:
                print(f"Error en nodo {container_name}: {e}")
                print(f"Reiniciando nodo {container_name}")
                self.restart_node(container_name)
                break
