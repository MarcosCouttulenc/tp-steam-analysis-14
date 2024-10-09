from common.message import Message

END_OF_MESSAGE = "\n"
END_OF_MESSAGE_BYTES = b"\n"
END_OF_BATCH = "\n\n"
END_OF_BATCH_BYTES = b"\n\n"
DATA_DELIMITER = "$|"
DATA_DELIMITER_BYTES = b"$|"
LEN_END_OF_BATCH = len(END_OF_MESSAGE) + len(END_OF_BATCH)

class MessageSerializer:
    
    def serialize(self, message: Message) -> str:
        data = message.message_type + DATA_DELIMITER + message.message_payload + END_OF_MESSAGE
        return data.encode("utf-8")

    def deserialize(self, message_str: str) -> Message:
        data = message_str.decode('utf-8').split(DATA_DELIMITER)

        # if data[0] == "Dupio":
        #     print("\n\nDESERIALIZE\n\n")
        #     print(message_str)
        #     print(data[1:])
        #     print("\n\npost DESERIALIZE\n\n")
            
        #A la izquierda esta el tipo, todo lo que esta a la derecha es payload
        return Message(data[0], DATA_DELIMITER.join(data[1:]))

    def serialize_batch(self, messages: list[Message]) -> str:
        data_batch = [self.serialize(message) for message in messages]
        data_batch_bytes = b''.join(data_batch)
        data_batch_bytes += END_OF_BATCH_BYTES
        return data_batch_bytes

    def deserialize_batch(self, messages_batch_str: str) -> list[Message]:
        data_batch = messages_batch_str.split(END_OF_MESSAGE_BYTES)
        lst_messages = []
        for message_data in data_batch:
            lst_messages.append(self.deserialize(message_data))
        return lst_messages