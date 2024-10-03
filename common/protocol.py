
from common.message import Message
from common.message_serializer import MessageSerializer, END_OF_BATCH_BYTES, END_OF_MESSAGE_BYTES

BUFFER_RECEIVE_SIZE_BYTES = 1024
BUFFER_RECEIVE_BATCH_SIZE_BYTES = BUFFER_RECEIVE_SIZE_BYTES * 3

class Protocol:
    def __init__(self, socket):
        self.socket = socket
        self.message_serializer = MessageSerializer()

    def receive_batch(self) -> list[Message]:
        """
        Funcion utilizada para recibir un batch de mensajes.
        """

        buffer = b""

        while True:
            data = self.socket.recv(BUFFER_RECEIVE_BATCH_SIZE_BYTES)
            
            if not data:
                return None

            buffer += data

            #Si hay un END_OF_BATCH_BYTES en el buffer entonces cortamos el buffer ahi.
            if END_OF_BATCH_BYTES in buffer:
                data_batch = buffer[:buffer.index(END_OF_BATCH_BYTES)].strip()
                return self.message_serializer.deserialize_batch(data_batch)

    def send_batch(self, messages: list[Message]):
        """
        Funcion utilizada para enviar un listado de mensajes en batch.
        """

        data = self.message_serializer.serialize_batch(messages)

        sent_bytes = 0
        bytes_to_send = len(data)

        while sent_bytes < bytes_to_send:
            n = self.socket.send(data[sent_bytes:])
            if (n == 0):
                return None
            sent_bytes += n

    def receive(self) -> Message:
        """
        Funcion utilizada para reicbir un mensaje.
        """

        buffer = b""

        while True:
            data = self.socket.recv(BUFFER_RECEIVE_SIZE_BYTES)
            
            if not data:
                return None

            buffer += data

            #Si hay un END_OF_MESSAGE_BYTES en el buffer entonces cortamos el buffer ahi.
            if END_OF_MESSAGE_BYTES in buffer:
                data_message = buffer[:buffer.index(END_OF_MESSAGE_BYTES)].strip()
                return self.message_serializer.deserialize(data_message)

    def send(self, message: Message):
        """
        Funcion utilizada para enviar un mensaje.
        """

        data = self.message_serializer.serialize(message)

        sent_bytes = 0
        bytes_to_send = len(data)

        while sent_bytes < bytes_to_send:
            n = self.socket.send(data[sent_bytes:])
            if (n == 0):
                return None
            sent_bytes += n
            
