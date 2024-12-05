import csv
import logging
logging.basicConfig(level=logging.CRITICAL)
import errno
import os
import io
import socket
import time

from common.message import MessageClientAskResults
from common.message import MessageQueryOneResult
from common.message import MessageQueryTwoResult
from common.message import MessageQueryThreeResult
from common.message import MessageQueryFourResult
from common.message import MessageQueryFiveResult
from common.message import MessageResultStatus
from common.message import MessageResultContent
from common.message import ResultStatus
from common.protocol import Protocol
from common.protocol import *

CHUNK_SIZE_FILE_READ = 1024

class ResultResponser:
    def __init__(self, result_responser_port, tmp_file_path, listen_backlog, query1_file_ip_port, query2_file_ip_port, 
                query3_file_ip_port, query4_file_ip_port, query5_file_ip_port, ip_healthchecker, port_healthchecker):
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

        self.final_results = {}

        self.ip_healthchecker = ip_healthchecker
        self.port_healthchecker = int(port_healthchecker)

    def start(self):
        logging.critical("result responser corriendo")
        while self.running:
            client_sock = self.__accept_new_connection()
            protocol = Protocol(client_sock)

            message = protocol.receive()
            
            is_finished = self.get_queries_results_and_create_tmp_file(message.get_client_id())

            self.send_queries_results_in_batch(client_sock, is_finished, message.get_client_id())
            
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

    def get_queries_results_and_create_tmp_file(self, client_id):
        is_finished = True
        is_finished = self.get_query1_results(client_id) and is_finished 
        is_finished = self.get_query2_results(client_id) and is_finished 
        is_finished = self.get_query3_results(client_id) and is_finished
        is_finished = self.get_query4_results(client_id) and is_finished
        is_finished = self.get_query5_results(client_id) and is_finished
        return is_finished
        
        

    def get_query1_results(self, client_id: int):
        query1_file_connection_data = self.query1_file_ip_port.split(',')

        
        while True:
            try:
                client_q1_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_q1_sock.connect((query1_file_connection_data[0], int(query1_file_connection_data[1])))
                break
            except:
                print("Query1File caido al hacer connect, retry")
                time.sleep(5)
                continue

        self.protocol = Protocol(client_q1_sock)
        self.protocol.send(MessageClientAskResults(client_id))

        #Recibe el primer mensaje con el status de la operacion.
        msg_status = self.protocol.receive()
        if not msg_status:
            print("No se obtuvo resultado, queryFile1 caido en primer receive.")
            return False

        msg_query1_status = MessageResultStatus.from_message(msg_status)
        status = msg_query1_status.message_payload

        #Recibe el segundo mensaje con los resultados de la query.
        msg = self.protocol.receive()
        if msg == None:
            print("No se obtuvo resultado, queryFile1 caido en segundo receive.")
            return False
        
        try:
            client_q1_sock.close()
        except:
            print("Se quiso cerrar el socket y ya estaba cerrado")
            
        msg_query1_one_result = MessageQueryOneResult.from_message(msg)
        
        with open(self.tmp_file_path, "w") as file:
            file.write(f"Query1 Resultados: <br/>")
            file.write(f"Status: {status} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
            file.write(f"Total Linux: {msg_query1_one_result.total_linux} <br/>")
            file.write(f"Total Mac: {msg_query1_one_result.total_mac} <br/>")
            file.write(f"Total Windows: {msg_query1_one_result.total_windows} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
        
        return status == ResultStatus.FINISHED.value

    def get_query2_results(self, client_id: int):
        query2_file_connection_data = self.query2_file_ip_port.split(',')


        while True:
            try:
                client_q2_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_q2_sock.connect((query2_file_connection_data[0], int(query2_file_connection_data[1])))
                break
            except:
                print("Query2File caido, retry")
                time.sleep(5)
                continue

        self.protocol = Protocol(client_q2_sock)
        self.protocol.send(MessageClientAskResults(client_id))

        #Recibe el primer mensaje con el status de la operacion.
        msg_status = self.protocol.receive()
        if not msg_status:
            print("No se obtuvo resultado, queryFile2 caido en primer receive.")
            return False
        
        msg_query2_status = MessageResultStatus.from_message(msg_status)
        status = msg_query2_status.message_payload

        #Recibe el segundo mensaje con los resultados de la query.
        msg = self.protocol.receive()
        if msg == None:
            print("No se obtuvo resultado, queryFile2 caido en segundo receive.")
            return False

        try:
            client_q2_sock.close()
        except:
            print("Se quiso cerrar el socket y ya estaba cerrado")
        
        msg_query2_two_result = MessageQueryTwoResult.from_message(msg)
        
        with open(self.tmp_file_path, "a") as file:
            file.write(f"Query2 Resultados: <br/>")
            file.write(f"Status: {status} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
            for game_name, playtime in msg_query2_two_result.top_ten_buffer:
                file.write(f"{game_name}: {playtime} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
        
        return status == ResultStatus.FINISHED.value

    def get_query3_results(self, client_id: int):
        query3_file_connection_data = self.query3_file_ip_port.split(',')


        while True:
            try:
                client_q3_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_q3_sock.connect((query3_file_connection_data[0], int(query3_file_connection_data[1])))
        
                break
            except:
                print("Query3File caido, retry")
                time.sleep(5)
                continue
        
        self.protocol = Protocol(client_q3_sock)
        self.protocol.send(MessageClientAskResults(client_id))

        #Recibe el primer mensaje con el status de la operacion.
        msg_status = self.protocol.receive()

        if msg_status == None:
            print("No se obtuvo resultado, queryFile3 caido en primer receive.")
            return False
        
        msg_query3_status = MessageResultStatus.from_message(msg_status)
        status = msg_query3_status.message_payload

        #Recibe el segundo mensaje con los resultados de la query.
        msg = self.protocol.receive()
        if msg == None:
            print("No se obtuvo resultado, queryFile3 caido en segundo receive.")
            return False
        
        try:
            client_q3_sock.close()
        except:
            print("Se quiso cerrar el socket y ya estaba cerrado")

        msg_query3_three_result = MessageQueryThreeResult.from_message(msg)

        with open(self.tmp_file_path, "a") as file:
            file.write(f"Query3 Resultados: <br/>")
            file.write(f"Status: {status} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
            for game_name, total_pos_reviews in msg_query3_three_result.top_five_buffer:
                file.write(f"{game_name}: {total_pos_reviews} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")

        return status == ResultStatus.FINISHED.value

    def get_query4_results(self, client_id: int):
        query4_file_connection_data = self.query4_file_ip_port.split(',')


        while True:
            try:
                client_q4_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_q4_sock.connect((query4_file_connection_data[0], int(query4_file_connection_data[1])))
                break
            except:
                print("Query4File caido, retry")
                time.sleep(5)
                continue
        
        self.protocol = Protocol(client_q4_sock)
        self.protocol.send(MessageClientAskResults(client_id))

        #Recibe el primer mensaje con el status de la operacion.
        msg_status = self.protocol.receive()

        if msg_status == None:
            print("No se obtuvo resultado, queryFile4 caido en primer receive.")
            return False
        
        msg_query4_status = MessageResultStatus.from_message(msg_status)
        status = msg_query4_status.message_payload

        #Recibe el segundo mensaje con los resultados de la query.
        msg = self.protocol.receive()
        if msg == None:
            print("No se obtuvo resultado, queryFile4 caido en segundo receive.")
            return False
        
        try:
            client_q4_sock.close()
        except:
            print("Se quiso cerrar el socket y ya estaba cerrado")

        msg_query4_four_result = MessageQueryFourResult.from_message(msg)
        
        with open(self.tmp_file_path, "a") as file:
            file.write(f"Query4 Resultados: <br/>")
            file.write(f"Status: {status} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
            for name, _ in msg_query4_four_result.totals:
                file.write(f"{name} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")

        return status == ResultStatus.FINISHED.value

    def get_query5_results(self, client_id: int):
        query5_file_connection_data = self.query5_file_ip_port.split(',')


        while True:
            try:
                client_q5_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_q5_sock.connect((query5_file_connection_data[0], int(query5_file_connection_data[1])))
                break
            except:
                print("Query5File caido, retry")
                time.sleep(5)
                continue
        
        self.protocol = Protocol(client_q5_sock)
        self.protocol.send(MessageClientAskResults(client_id))

        #Recibe el primer mensaje con el status de la operacion.
        msg_status = self.protocol.receive()
        if not msg_status:
            print("No se obtuvo resultado, queryFile5 caido en el primer receive.")
            return False
        
        msg_query5_status = MessageResultStatus.from_message(msg_status)
        status = msg_query5_status.message_payload

        #Recibe el segundo mensaje con los resultados de la query.
        msg = self.protocol.receive()
        if not msg:
            print("No se obtuvo resultado, queryFile5 caido en el segundo receive.")
            return False

        try:
            client_q5_sock.close()
        except:
            print("Se quiso cerrar el socket y ya estaba cerrado")

        msg_query5_five_result = MessageQueryFiveResult.from_message(msg)
        
        with open(self.tmp_file_path, "a") as file:
            file.write(f"Query5 Resultados: <br/>")
            file.write(f"Status: {status} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
            for id, name in msg_query5_five_result.totals:
                file.write(f"{id},{name} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
            
        return status == ResultStatus.FINISHED.value

    def send_queries_results_in_batch(self, client_sock, is_finished, client_id):
        protocol = Protocol(client_sock)

        # Enviar un mensaje con el estado "Processing" o "Finalizado"
        msg_result_status = MessageResultStatus(client_id, ResultStatus.PENDING)
        if is_finished:
            msg_result_status = MessageResultStatus(client_id, ResultStatus.FINISHED)
        protocol.send(msg_result_status)

        # Enviar un mensaje con el contenido
        file_content = ""
        with open(self.tmp_file_path, "r") as file:
            while chunk := file.read(CHUNK_SIZE_FILE_READ):
                file_content += chunk
                
        msg_result_content = MessageResultContent(client_id, file_content)
        protocol.send(msg_result_content)
        