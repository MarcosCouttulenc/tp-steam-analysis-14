import pika
import time
from common.message import Message
from common.message_serializer import MessageSerializer

class ServiceQueues:
    def __init__(self, connection_name):
        credentials = pika.PlainCredentials('admin', 'admin')
        
        for _ in range(5):  # Intentar varias veces
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=connection_name,
                    port=5672,
                    credentials=credentials,
                    heartbeat=300 
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
        try:
            message_serializer = MessageSerializer()
            self.channel.queue_declare(queue=queue_name, durable=True)

            def new_callback(ch, method, properties, body):
                message = message_serializer.deserialize(body.strip())
                callback(ch, method, properties, message)

            self.channel.basic_consume(
                queue=queue_name, 
                on_message_callback=new_callback,
            )

            self.channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print("[pop] Desconectado de rabbit")
        except Exception as e:
            raise e

    def pop_non_blocking(self, queue_name: str, callback):
        try:
            message_serializer = MessageSerializer()
            self.channel.queue_declare(queue=queue_name, durable=True)

            while True:
                method_frame, properties, body = self.channel.basic_get(queue=queue_name, auto_ack=False)
                
                if method_frame:
                    # Si hay un mensaje, procesarlo
                    message = message_serializer.deserialize(body.strip())
                    callback(self.channel, method_frame, properties, message)
                else:
                    # Si no hay mensajes, esperar un momento
                    time.sleep(1)
        except pika.exceptions.AMQPConnectionError:
            print("[pop_non_blocking] Desconectado de rabbit")
        except Exception as e:
            raise e

    def ack(self, ch, method):
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def close_connection(self):
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
        except pika.exceptions.AMQPConnectionError:
            print("[close_connection] Desconectado de rabbit")
        except Exception as e:
            raise e

    def purge(self, queue_name):
        try:
            if self.connection and not self.connection.is_closed:
                channel = self.connection.channel()
                channel.queue_purge(queue=queue_name)
        except pika.exceptions.AMQPConnectionError:
            print("[purge] Desconectado de rabbit")
        except Exception as e:
            raise e