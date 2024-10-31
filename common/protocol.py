
from common.message import Message
from common.message_serializer import MessageSerializer, END_OF_BATCH_BYTES, END_OF_MESSAGE_BYTES, LEN_END_OF_BATCH

BUFFER_RECEIVE_SIZE_BYTES = 1024*1
BUFFER_RECEIVE_BATCH_SIZE_BYTES = BUFFER_RECEIVE_SIZE_BYTES * 2

class Protocol:
    def __init__(self, socket):
        self.socket = socket
        self.message_serializer = MessageSerializer()
        self.previous_batch = b""
        self.previous_message = b""


    def receive_batch(self) -> list[Message]:
        """
        Funcion utilizada para recibir un batch de mensajes.
        """

        buffer = b""
        buffer += self.previous_batch
        self.previous_batch = b""
        
        if END_OF_BATCH_BYTES in buffer:
            data_batch = buffer[:buffer.index(END_OF_BATCH_BYTES)]
            self.previous_batch = buffer[buffer.index(END_OF_BATCH_BYTES) + LEN_END_OF_BATCH:]
            return self.message_serializer.deserialize_batch(data_batch)
        
        while True:
            data = self.socket.recv(BUFFER_RECEIVE_BATCH_SIZE_BYTES)
            if not data:
                return None

            buffer += data

            #Si hay un END_OF_BATCH_BYTES en el buffer entonces cortamos el buffer ahi.
            if END_OF_BATCH_BYTES in buffer:
                data_batch = buffer[:buffer.index(END_OF_BATCH_BYTES)]
                self.previous_batch = buffer[buffer.index(END_OF_BATCH_BYTES) + LEN_END_OF_BATCH:]
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
        buffer += self.previous_message
        self.previous_message = ""

        if END_OF_MESSAGE_BYTES in buffer:
            data_message = buffer[:buffer.index(END_OF_MESSAGE_BYTES)].strip()
            return self.message_serializer.deserialize(data_message)

        while True:
            data = self.socket.recv(BUFFER_RECEIVE_SIZE_BYTES)
            
            if not data:
                return None

            buffer += data

            #Si hay un END_OF_MESSAGE_BYTES en el buffer entonces cortamos el buffer ahi.
            if END_OF_MESSAGE_BYTES in buffer:
                data_message = buffer[:buffer.index(END_OF_MESSAGE_BYTES)].strip()
                self.previous_message = buffer[buffer.index(END_OF_MESSAGE_BYTES):]
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


    def send_stream(self, stream_message: str):
        sent_bytes = 0
        bytes_to_send = len(stream_message)

        while sent_bytes < bytes_to_send:
            n = self.socket.send(stream_message[sent_bytes:])
            if (n == 0):
                return None
            sent_bytes += n

    def receive_stream(self):
        data = self.socket.recv(BUFFER_RECEIVE_SIZE_BYTES)
            
        if not data:
            return None

        return data.decode("utf-8")