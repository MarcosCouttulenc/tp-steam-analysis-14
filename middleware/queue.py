import pika
import time
from common.message import Message
from common.message_serializer import MessageSerializer

class ServiceQueues:
    def __init__(self, connection_name):
        credentials = pika.PlainCredentials('admin', 'admin')
        #connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', credentials))

        for _ in range(5):  # Intentar varias veces
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=connection_name,
                    port=5672,
                    credentials=credentials,
                ))
                self.channel = self.connection.channel()
                break  # Si la conexión es exitosa, salir del bucle
            except pika.exceptions.AMQPConnectionError:
                print("Esperando a que RabbitMQ esté disponible...")
                time.sleep(5)  # Esperar 5 segundos antes de volver a intentar
        else:
            print("No se pudo conectar a RabbitMQ después de varios intentos.")

    def push(self, queue_name: str, msg: Message):
        message_serializer = MessageSerializer()
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message_serializer.serialize(msg)
        )
    
    def pop(self, queue_name: str, callback):
        message_serializer = MessageSerializer()
        self.channel.queue_declare(queue=queue_name, durable=True)

        #def new_callback(ch, method, properties, body):
        #    message = message_serializer.deserialize(body)
        #    callback(ch, method, properties, message)

        print("\n\n se registro el pop \n")

        self.channel.basic_consume(
            queue=queue_name, 
            on_message_callback=callback,
        )

    def ack(self, ch, method):
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def close_connection(self):
        self.connection.close()
