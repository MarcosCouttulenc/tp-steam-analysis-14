import pika
from common.message import Message

class ServiceQueues:
    def __init__(self, connection_name):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(connection_name))
        self.channel = self.connection.channel()

    def push(self, queue_name: str, msg: Message):
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=msg
        )
    
    def pop(self, queue_name: str, callback):
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_consume(
            queue=queue_name, 
            on_message_callback=callback
        )
    
    def ack(self, ch, method):
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def close_connection(self):
        self.connection.close()
