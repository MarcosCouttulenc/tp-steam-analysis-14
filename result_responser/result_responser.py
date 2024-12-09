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

        self.query_ports_dict = self.init_query_ports_dict(query1_file_ip_port, query2_file_ip_port, query3_file_ip_port, query4_file_ip_port, query5_file_ip_port)

        self.final_results = {}

        self.ip_healthchecker = ip_healthchecker
        self.port_healthchecker = int(port_healthchecker)

    def init_query_ports_dict(self, query1_file_ip_port, query2_file_ip_port, query3_file_ip_port, query4_file_ip_port, query5_file_ip_port):
        rta = {}
        query1_data = query1_file_ip_port.split(",")
        rta[query1_data[0]] = query1_data[1:]

        query2_data = query2_file_ip_port.split(",")
        rta[query2_data[0]] = query2_data[1:]

        query3_data = query3_file_ip_port.split(",")
        rta[query3_data[0]] = query3_data[1:]

        query4_data = query4_file_ip_port.split(",")
        rta[query4_data[0]] = query4_data[1:]

        query5_data = query5_file_ip_port.split(",")
        rta[query5_data[0]] = query5_data[1:]

        return rta



    def start(self):
        logging.critical("result responser corriendo")
        while self.running:
            client_sock = self.__accept_new_connection()
            print("Cliente conectado")
            protocol = Protocol(client_sock)

            message = protocol.receive()

            print(f"Comienzo respuesta de cliente: {message.get_client_id()}")
            
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
        cant_windows = 0
        cant_linux = 0
        cant_mac = 0
        is_finished = True

        query1_file_ip_base = "query1_file"
        cant_query1_files = len(self.query_ports_dict[query1_file_ip_base])
        for i in range(0, cant_query1_files):
            file_ip = f"{query1_file_ip_base}_{i+1}"
            file_port = self.query_ports_dict[query1_file_ip_base][i]

            (status, msg_info) = self.get_info_from_query_file_node(query1_file_ip_base, file_ip, file_port, client_id)
            
            if (status == ResultStatus.ERROR.value):
                return False
            
            msg_query1_one_result = MessageQueryOneResult.from_message(msg_info)

            cant_windows += msg_query1_one_result.total_windows
            cant_linux += msg_query1_one_result.total_linux
            cant_mac += msg_query1_one_result.total_mac

            is_finished = is_finished and (status == ResultStatus.FINISHED.value)
        
        if is_finished:
            status = ResultStatus.FINISHED.value
        else:
            status = ResultStatus.PENDING.value
        
        with open(self.tmp_file_path, "w") as file:
            file.write(f"Query1 Resultados: <br/>")
            file.write(f"Status: {status} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
            file.write(f"Total Linux: {cant_linux} <br/>")
            file.write(f"Total Mac: {cant_mac} <br/>")
            file.write(f"Total Windows: {cant_windows} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
        
        return is_finished
        
    def get_query2_results(self, client_id: int):
        print("Comienza get_query2_file")
        is_finished = True
        totals = []
        query2_file_ip_base = "query2_file"
        cant_query2_files = len(self.query_ports_dict[query2_file_ip_base])

        for i in range(0, cant_query2_files):
            file_ip = f"{query2_file_ip_base}_{i+1}"
            file_port = self.query_ports_dict[query2_file_ip_base][i]

            (status, msg_info) = self.get_info_from_query_file_node(query2_file_ip_base, file_ip, file_port, client_id)

            if (status == ResultStatus.ERROR.value):
                return False
            
            msg_query2_two_result = MessageQueryTwoResult.from_message(msg_info)
            totals += msg_query2_two_result.top_ten_buffer
            is_finished = is_finished and (status == ResultStatus.FINISHED.value)

        if is_finished:
            status = ResultStatus.FINISHED.value
        else:
            status = ResultStatus.PENDING.value

        total_list_sorted = sorted(totals, key=lambda item: item[1], reverse=True)
        top_ten = []

        if (len(total_list_sorted) > 10):
            top_ten = total_list_sorted[:10]
        else:
            top_ten = total_list_sorted

        with open(self.tmp_file_path, "a") as file:
            file.write(f"Query2 Resultados: <br/>")
            file.write(f"Status: {status} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
            for game_name, playtime in top_ten:
                file.write(f"{game_name}: {playtime} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")

        return is_finished

    '''
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
    '''

    def get_query3_results(self, client_id: int):
        print("Comienza get_query3_file")
        is_finished = True
        totals = []
        query3_file_ip_base = "query3_file"
        cant_query3_files = len(self.query_ports_dict[query3_file_ip_base])
        
        for i in range(0, cant_query3_files):
            file_ip = f"{query3_file_ip_base}_{i+1}"
            file_port = self.query_ports_dict[query3_file_ip_base][i]

            (status, msg_info) = self.get_info_from_query_file_node(query3_file_ip_base, file_ip, file_port, client_id)

            if (status == ResultStatus.ERROR.value):
                return False
            
            msg_query3_three_result = MessageQueryThreeResult.from_message(msg_info)
            totals += msg_query3_three_result.top_five_buffer
            is_finished = is_finished and (status == ResultStatus.FINISHED.value)

        if is_finished:
            status = ResultStatus.FINISHED.value
        else:
            status = ResultStatus.PENDING.value

        total_list_sorted = sorted(totals, key=lambda item: item[1], reverse=True)
        top_five = []

        if (len(total_list_sorted) > 5):
            top_five = total_list_sorted[:5]
        else:
            top_five = total_list_sorted

        with open(self.tmp_file_path, "a") as file:
            file.write(f"Query3 Resultados: <br/>")
            file.write(f"Status: {status} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
            for game_name, total_pos_reviews in top_five:
                file.write(f"{game_name}: {total_pos_reviews} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")

        return is_finished



    def get_query4_results(self, client_id: int):
        print("Comienza get_query4_file")
        is_finished = True
        totals = []
        query4_file_ip_base = "query4_file"
        cant_query4_files = len(self.query_ports_dict[query4_file_ip_base])
        
        for i in range(0, cant_query4_files):
            file_ip = f"{query4_file_ip_base}_{i+1}"
            file_port = self.query_ports_dict[query4_file_ip_base][i]

            (status, msg_info) = self.get_info_from_query_file_node(query4_file_ip_base, file_ip, file_port, client_id)

            if (status == ResultStatus.ERROR.value):
                return False
            
            msg_query4_four_result = MessageQueryFourResult.from_message(msg_info)

            totals += msg_query4_four_result.totals
            
            is_finished = is_finished and (status == ResultStatus.FINISHED.value)

        if is_finished:
            status = ResultStatus.FINISHED.value
        else:
            status = ResultStatus.PENDING.value
        
        with open(self.tmp_file_path, "a") as file:
            file.write(f"Query4 Resultados: <br/>")
            file.write(f"Status: {status} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
            for name, _ in totals:
                file.write(f"{name} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
        
        return is_finished


    def get_query5_results(self, client_id: int):
        print("Comienza get_query5_file")
        is_finished = True
        totals = {}
        query5_file_ip_base = "query5_file"
        cant_query5_files = len(self.query_ports_dict[query5_file_ip_base])
        
        for i in range(0, cant_query5_files):
            file_ip = f"{query5_file_ip_base}_{i+1}"
            file_port = self.query_ports_dict[query5_file_ip_base][i]

            (status, msg_info) = self.get_info_from_query_file_node(query5_file_ip_base, file_ip, file_port, client_id)

            if (status == ResultStatus.ERROR.value):
                return False
            
            msg_query5_five_result = MessageQueryFiveResult.from_message(msg_info)

            totals.update(msg_query5_five_result.totals)
            
            is_finished = is_finished and (status == ResultStatus.FINISHED.value)

        if is_finished:
            status = ResultStatus.FINISHED.value
        else:
            status = ResultStatus.PENDING.value
        
        result = []
        percentil_90 = self.get_percentil_90(totals)

        for name, game_info in sorted(totals.items(), key=lambda x: x[1][2], reverse=False):
            if game_info[1] > percentil_90:
                result.append((game_info[2], name))

        final_result = result[:10]

        with open(self.tmp_file_path, "a") as file:
            file.write(f"Query5 Resultados: <br/>")
            file.write(f"Status: {status} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
            for id, name in final_result:
                file.write(f"{id},{name} <br/>")
            file.write(f"---------------------------------------------------------- <br/>")
        
        return is_finished
        
    
    def get_percentil_90(self, data):
        if len(data) == 0:
            return None

        neg_reviews = [neg for pos, neg, id in data.values()]
        neg_reviews_sorted = sorted(neg_reviews)
        percentil_90_pos = int(0.90 * (len(neg_reviews_sorted) - 1))

        percentil_90 = neg_reviews_sorted[percentil_90_pos]
        return percentil_90


    def get_info_from_query_file_node(self, query_file_name, query_file_ip, query_file_port, client_id):
        print(f"[Conectando {query_file_name}] Voy a consultar a: {query_file_ip}, {query_file_port}")

        while True:
            try:
                client_query_node_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_query_node_sock.connect((query_file_ip, int(query_file_port)))
                break
            except Exception as e:
                print(f"[Fallo {query_file_name}] Nodo {query_file_port} caido, retry. Error: {e}")
                time.sleep(5)
                continue

        self.protocol = Protocol(client_query_node_sock)
        self.protocol.send(MessageClientAskResults(client_id))

        #Recibe el primer mensaje con el status de la operacion.
        msg_status = self.protocol.receive()
        if not msg_status:
            print(f"[Fallo {query_file_name}] No se obtuvo resultado, nodo de en puerto {query_file_port} caido en el primer receive.")
            return (ResultStatus.ERROR, None)
        
        msg_result_status = MessageResultStatus.from_message(msg_status)
        status = msg_result_status.message_payload

        #Recibe el segundo mensaje con los resultados de la query.
        msg_info = self.protocol.receive()
        if not msg_info:
            print(f"[Fallo {query_file_name}] No se obtuvo resultado, nodo de en puerto {query_file_port} caido en el segundo receive.")
            return (ResultStatus.ERROR, None)

        try:
            client_query_node_sock.close()
        except:
            print("Se quiso cerrar el socket y ya estaba cerrado")

        return (status, msg_info)


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
        