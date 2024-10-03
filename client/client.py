import logging
#import pika
import socket

class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

    def start(self):
        logging.info('action: client_start | result: success')
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_ip, int(self.server_port)))


        # Recibir y enviar mensaje al servidor
        response = client_socket.recv(1024).decode()
        logging.info(f'action: client_msg_received | result: success | msg: {response}')

        message_client = response + "client"

        client_socket.send(message_client.encode())

        logging.info(f'action: client_msg_sent | result: success | msg: {message_client}')

        client_socket.close()
    #def send_message(message):
        # logging.info(f"Sending Message: {message}")
        # conn = pika.BlockingConnection([pika.ConnectionParameters(host='rabbitmq')])
        # channel = conn.channel()

        # channel.queue_declare(queue = 'task_queue', durable=True)

        # channel.basic_publish(exchange='',
        #                       routing_key='task_queue',
        #                       body=message,
        #                       properties=pika.BasicProperties(delivery_mode=2,))

        # conn.close()

