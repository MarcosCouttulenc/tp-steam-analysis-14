import csv
import logging
logging.basicConfig(level=logging.CRITICAL)
import errno
import os
import socket

from common.message import MessageQueryOneResult
from common.protocol import *

CHUNK_SIZE_FILE_READ = 1024

class ResultResponser:
    def __init__(self, result_responser_port, tmp_file_path, listen_backlog, query1_file_ip_port, query2_file_ip_port, 
                query3_file_ip_port, query4_file_ip_port, query5_file_ip_port):
        self.running = True
        self.new_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.new_connection_socket.bind(('', result_responser_port))
        self.new_connection_socket.listen(listen_backlog)

        self.tmp_file_path = tmp_file_path
        self.query1_file_ip_port = query1_file_ip_port
        self.query2_file_ip_port = query2_file_ip_port
        self.query3_file_ip_port = query3_file_ip_port
        self.query4_file_ip_port = query4_file_ip_port
        self.query5_file_ip_port = query5_file_ip_port

    def start(self):
        logging.critical("result responser corriendo")
        while self.running:
            client_sock = self.__accept_new_connection()
            
            self.get_queries_results_and_create_tmp_file()

            self.send_queries_results_in_batch(client_sock)
            
            os.remove(self.tmp_file_path)

            client_sock.close()

    def __accept_new_connection(self):
        try:
            c, addr = self.new_connection_socket.accept()
            logging.critical(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError as e:
            if e.errno == errno.EBADF:  # Bad file descriptor, server socket closed
                logging.critical('SOCKET CERRADO - ACCEPT_NEW_CONNECTIONS')
                return None
            else:
                raise

    def get_queries_results_and_create_tmp_file(self):
        self.get_query1_results()
        self.get_query2_results()
        self.get_query3_results()
        self.get_query4_results()
        self.get_query5_results()
        

    def get_query1_results(self):
        query1_file_connection_data = self.query1_file_ip_port.split(',')

        client_q1_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_q1_sock.connect((query1_file_connection_data[0], int(query1_file_connection_data[1])))

        self.protocol = Protocol(client_q1_sock)

        msg = self.protocol.receive()
        msg_query1_one_result = MessageQueryOneResult.from_message(msg)
        if msg_query1_one_result == None:
            return
        
        with open(self.tmp_file_path, "w") as file:
            file.write(f"Query1 Resultados:\n")
            file.write(f"----------------------------------------------------------\n")
            file.write(f"Total Linux: {msg_query1_one_result.total_linux}\n")
            file.write(f"Total Mac: {msg_query1_one_result.total_mac}\n")
            file.write(f"Total Windows: {msg_query1_one_result.total_windows}\n")
            file.write(f"----------------------------------------------------------\n")

        client_q1_sock.close()

    def get_query2_results(self):
        with open(self.tmp_file_path, "a") as file:
            file.write(f"Query2 Resultados:\n")
            file.write(f"----------------------------------------------------------\n")
            file.write(f"Por el momento no hay resultados procesados \n")
            file.write(f"----------------------------------------------------------\n")

    def get_query3_results(self):
        with open(self.tmp_file_path, "a") as file:
            file.write(f"Query3 Resultados:\n")
            file.write(f"----------------------------------------------------------\n")
            file.write(f"Por el momento no hay resultados procesados \n")
            file.write(f"----------------------------------------------------------\n")

    def get_query4_results(self):
        with open(self.tmp_file_path, "a") as file:
            file.write(f"Query4 Resultados:\n")
            file.write(f"----------------------------------------------------------\n")
            file.write(f"Por el momento no hay resultados procesados \n")
            file.write(f"----------------------------------------------------------\n")

    def get_query5_results(self):
        with open(self.tmp_file_path, "a") as file:
            file.write(f"Query5 Resultados:\n")
            file.write(f"----------------------------------------------------------\n")
            file.write(f"Por el momento no hay resultados procesados \n")
            file.write(f"----------------------------------------------------------\n")

    def send_queries_results_in_batch(self, client_sock):
        protocol = Protocol(client_sock)

        with open(self.tmp_file_path, "rb") as file:
            while chunk := file.read(CHUNK_SIZE_FILE_READ):
                protocol.send_stream(chunk)