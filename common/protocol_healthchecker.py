from common.protocol import Protocol
from common.message import Message, DATA_DELIMITER, MESSAGE_HEALTH_CHECK_ASK, MESSAGE_HEALTH_CHECK_ACK, MESSAGE_CONTAINER_NAME


USELESS_CLIENT_ID = -1
class MessageHealthCheckerAsk(Message):
    def __init__(self):
        message_payload = "ASK"
        super().__init__(USELESS_CLIENT_ID, MESSAGE_HEALTH_CHECK_ASK, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageHealthCheckerAsk':
        if message.message_type != MESSAGE_HEALTH_CHECK_ASK:
            return None
        
        return cls()

class MessageHealthCheckerAck(Message):
    def __init__(self):
        message_payload = "ACK"
        super().__init__(USELESS_CLIENT_ID, MESSAGE_HEALTH_CHECK_ACK, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageHealthCheckerAck':
        if message.message_type != MESSAGE_HEALTH_CHECK_ACK:
            return None
        
        return cls()

class MessageContainerName(Message):
    def __init__(self, container_name):
        self.container_name = container_name

        message_payload = container_name
        super().__init__(USELESS_CLIENT_ID, MESSAGE_CONTAINER_NAME, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageContainerName':
        if message.message_type != MESSAGE_CONTAINER_NAME:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        return cls(str(data[0]))


class ProtocolHealthChecker:
    def __init__(self, socket):
        self.protocol = Protocol(socket)

    def wait_for_health_check(self):
        print(f"[wait_for_health_check] Esperando healthchecker..")
        message = self.protocol.receive()
        
        if message == None:
            print(f"[wait_for_health_check] Recibi un None")
            return False

        print(f"[wait_for_health_check] Me llego algo del healtchecker {message}")
        
        msg_ask = MessageHealthCheckerAsk.from_message(message)

        print(f"[wait_for_health_check] Es un ASK? {str(msg_ask != None)}")

        return msg_ask != None

    def wait_for_node_ack(self):
        print(f"[wait_for_node_ack] Esperando al nodo..")
        message = self.protocol.receive()
        
        if message == None:
            print(f"[wait_for_node_ack] Recibi un None")
            return False

        print(f"[wait_for_node_ack] Me llego algo del nodo {message}")
        
        msg_ack = MessageHealthCheckerAck.from_message(message)

        print(f"[wait_for_node_ack] Es un ACK? {str(msg_ack != None)}")

        return msg_ack != None

    def health_check_ask(self):
        msg_ask = MessageHealthCheckerAsk()

        print(f"[health_check_ask] Enviando ASK al nodo.. {msg_ask}")

        bytes_sent = self.protocol.send(msg_ask)

        print(f"[health_check_ask] Envie {str(bytes_sent)} bytes")

        return not(bytes_sent == None or bytes_sent <= 0)

    def health_check_ack(self):
        msg_ack = MessageHealthCheckerAck()

        print(f"[health_check_ack] Enviando ACK al healthchecker.. {msg_ack}")

        bytes_sent = self.protocol.send(msg_ack)

        print(f"[health_check_ack] Envie {str(bytes_sent)} bytes")

        return not(bytes_sent == None or bytes_sent <= 0)

    def receive_container_name(self):
        print(f"[receive_container_name] Esperando el nombre del nodo..")
        message = self.protocol.receive()
        
        if message == None:
            print(f"[receive_container_name] Recibi un None")
            return False

        print(f"[receive_container_name] Me llego algo del nodo {message}")
        
        msg_container_name = MessageContainerName.from_message(message)

        print(f"[receive_container_name] Nombre del nodo {msg_container_name}")

        return msg_container_name
    
    
    def send_container_name(self, container_name):
        print(f"[send_container_name] Por enviar el nombre del container: [{container_name}]")

        message = MessageContainerName(container_name)

        bytes_sent = self.protocol.send(message)
        
        if bytes_sent == None or bytes_sent < 0:
            print(f"[send_container_name] No envie el msg")
            return False
        else:
            print(f"[send_container_name] Envie {str(bytes_sent)} bytes")

        return not(bytes_sent == None or bytes_sent < 0)