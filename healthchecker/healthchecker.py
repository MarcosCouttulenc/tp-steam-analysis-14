import socket
import threading
from time import sleep
from common.protocol_healthchecker import ProtocolHealthChecker, get_container_name
import docker
import os
import signal

LISTEN_BACKLOG = 100
TIME_BETWEEN_HEALTH_CHECKS = 5

class HealthChecker:
    def __init__(self, listen_port, connect_port, connect_ip):
        self.connect_port = int(connect_port)
        self.listen_port = int(listen_port)
        self.connect_ip = connect_ip
        self.running = True
        self.docker_client = docker.DockerClient(base_url="unix://var/run/docker.sock")
        self.file_name_connected_containers = "connected_containers.txt"
        self.file_lock = threading.Lock()
        self.init_signals()

    def init_signals(self):
        signal.signal(signal.SIGTERM, self.stop)

    def stop(self, signum, frame):
        print("action: stop | result: in_progress")
        
        self.running = False

        print("action: stop | result: success")


    def restart_node(self, container_name):
        # Reiniciamos el nodo que se cayo
        try:
            print(f"Reiniciando contenedor {container_name}")
            container_name = self.docker_client.containers.get(container_name)

            container_name.restart()

            #time.sleep(5)  # Tiempo de espera para darle al contenedor oportunidad de levantarse
            #container_name.reload()  # Actualizamos el estado del contenedor
            
            # if container_name.status == "running":
            #     print(f"Contenedor {container_name} está en estado 'running'")
            #     return True  # Salimos del bucle si el contenedor está en "running"
            
            print(f"Contenedor {container_name} reiniciado \n")
        except Exception as e:
            print(f"Error reiniciando contenedor {container_name}: {e} \n")

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


        # Lanzamos proceso que realiaz el health-check a todos
        health_check_process = threading.Thread(
            target = self.process_health_check_all 
        )
        health_check_process.start()
        processes.append(health_check_process)

        # Esperamos a que los procesos finalicen y joineamos
        for process in processes:
            process.join()
    

    def process_health_check_all(self):
        while self.running:
            my_containers_name = self.get_containers_name_from_file()

            print(f"[process_health_check_all] se van a levantar {len(my_containers_name)} containers")
            for container_name in my_containers_name:
                if (not self.is_node_running(container_name)):
                    print(f"[process_health_check_all] el contenedor {container_name} no esta corriendo")
                    self.restart_node(container_name)
            
        sleep(5)
    
    def get_containers_name_from_file(self):
        my_containers_name = []
        with self.file_lock:
            if (os.path.isfile(self.file_name_connected_containers)):
                with open(self.file_name_connected_containers, "r") as file:
                    for line in file.readlines():
                        my_containers_name.append(line.strip())
        return my_containers_name

    def process_my_healthchecker(self):
        # Conectamos al socket del mi healthchecker, si algo sale mal me
        # vuelvo a intentar conectar
        while self.running:
            while True:
                try:
                    skt_next_healthchecker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    skt_next_healthchecker.connect((self.connect_ip, self.connect_port))
                    break   
                except:
                    print("Healthchecker anterior cauido, retry")
                    sleep(5)
                    continue

            
            # comienza la comunicacion
            healthchecker_protocol = ProtocolHealthChecker(skt_next_healthchecker)

            # le envio el nombre de mi container
            if (not healthchecker_protocol.send_container_name(get_container_name())):
                continue

            # # ciclo de checkeo de health
            # while healthchecker_protocol.wait_for_health_check():
            #     healthchecker_protocol.health_check_ack()

    def process_accept_new_connection(self):
        print(f"[process_accept_new_connection] Iniciando...")

        # Apenas me levanto, lo primero que hago es revivir todos los nodos que dependian de mi (si es que alguno murio).
        my_containers_name = self.get_containers_name_from_file()

        print(f"[process_accept_new_connection] se van a levantar {len(my_containers_name)} containers")
        for container_name in my_containers_name:
            if (not self.is_node_running(container_name)):
                print(f"el contenedor {container_name} no esta corriendo")
                self.restart_node(container_name)

        # if (os.path.isfile(self.file_name_connected_containers)):
        #     os.remove(self.file_name_connected_containers)


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

        container_id = container_name_msg.container_name
        container = self.docker_client.containers.get(container_id)

        container_name = container.name

        my_containers_name = self.get_containers_name_from_file()
        if container_name in my_containers_name:
            return

        with self.file_lock:
            with open(self.file_name_connected_containers, "a") as file:
                file.write(container_name + '\n')

        
        #if (container_name == "worker_windows_1"):
        #    print("Empezando a monitorear worker_windows_1")
        
        # print(f"empezando a monitorear: {container_name}")

        # while True:
        #     try:
        #         if (not healthchecker_protocol.health_check_ask(container_name)):
        #             print(f"Error en nodo {container_name}")
        #             print(f"Reiniciando nodo {container_name}")
        #             self.restart_node(container_name)
        #             break

        #         if (not healthchecker_protocol.wait_for_node_ack(container_name)):
        #             print(f"Error en nodo {container_name}")
        #             print(f"Reiniciando nodo {container_name}")
        #             self.restart_node(container_name)
        #             break

        #         sleep(TIME_BETWEEN_HEALTH_CHECKS)
        #     except Exception as e:
        #         print(f"Error en nodo {container_name}: {e}")
        #         print(f"Reiniciando nodo {container_name}")
        #         self.restart_node(container_name)
        #         break
