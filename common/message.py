from common.model.game import Game
from common.model.review import Review
from enum import Enum

MESSAGE_TYPE_GAME_DATA = "game"
MESSAGE_TYPE_REVIEW_DATA = "review"
MESSAGE_TYPE_QUERY_DATABASE = "query-db"
MESSAGE_TYPE_END_OF_DATASET = "end-of-dataset"
MESSAGE_TYPE_QUERY_ONE_UPDATE = "query-one-update"
MESSAGE_TYPE_QUERY_ONE_FILE_UPDATE = "query-one-file-update"
MESSAGE_TYPE_QUERY_TWO_FILE_UPDATE = "query-two-file-update"
MESSAGE_TYPE_QUERY_THREE_FILE_UPDATE = "query-three-file-update"
MESSAGE_TYPE_QUERY_FOUR_FILE_UPDATE = "query-four-file-update"
MESSAGE_TYPE_QUERY_FIVE_FILE_UPDATE = "query-five-file-update"
MESSAGE_QUERY_ONE_RESULT = "query-one-result"
MESSAGE_QUERY_TWO_RESULT = "query-two-result"
MESSAGE_QUERY_THREE_RESULT = "query-three-result"
MESSAGE_QUERY_FOUR_RESULT = "query-four-result"
MESSAGE_QUERY_FIVE_RESULT = "query-five-result"

MESSAGE_TYPE_CLIENT_ASK_RESULTS = "client-ask-results"
MESSAGE_TYPE_SERVER_WELCOME_CLIENT = "server-welcome-client"
MESSAGE_TYPE_PEDING_RESULTS = "pending-results"
MESSAGE_TYPE_CONTENT_RESULTS = "content-results"

MESSAGE_HEALTH_CHECK_ASK = 'health-check-ask'
MESSAGE_HEALTH_CHECK_ACK = 'health-check-ack'
MESSAGE_CONTAINER_NAME = 'container-name'

MESSAGE_BATCH_TYPE = 'batch'

MESSAGE_MASTER_INVALID_CLIENT = 'invalid-client'
MESSAGE_MASTER_FINISHED_CLIENT = 'finished-client'

FALSE_STRING = "False"
TRUE_STRING = "True"

DATA_DELIMITER = "$|"
FIELD_DELIMITER = '*%$*'
BATCH_DELIMITER = '/&+'

USELESS_ID = "bow_id"

'''
Todos los mensajes estan conformados por un tipo y un payload,
el tipo es para indicar que forma o contenido va a tener el payload
y luego el payload es la informacion del mensaje.

Un mensaje va a estar serializado como:
tipo$|dato1$|dato2$| ... $|datoN , en la primera posicion vamos a tener siempre el tipo
'''

def string_to_boolean(string_variable):
    if string_variable == TRUE_STRING:
        return True
    elif string_variable == FALSE_STRING:
        return False
    else:
        print(f"\n\n\n VARIABLE: {string_variable} \n\n\n")
        raise Exception("Variable booleana incorrecta")
    
class Message:
    def __init__(self, message_id, client_id: int, message_type: str, message_payload: str):
        self.message_id = message_id
        self.client_id = client_id
        self.message_type = message_type
        self.message_payload = message_payload

    def set_message_id(self, message_id):
        self.message_id = message_id

    def get_client_id(self) -> int:
        return self.client_id
    
    def get_message_id(self) -> str:
        return self.message_id
    
    def get_filterid_from_message_id(self) -> str:
        vec = self.message_id.split('_')

        #print("[FilterID] vec despues de splitear: ", end='')
        #print(vec)

        if (len(vec) == 0):
            return None
        return vec[0]
    
    def get_seqnum_from_message_id(self) -> str:
        vec = self.message_id.split('_')

        #print("[FilterID] vec despues de splitear: ", end='')
        #print(vec)
        
        if (len(vec) == 1):
            return None
        return vec[1]

    def is_game(self) -> bool:
        return (self.message_type == MESSAGE_TYPE_GAME_DATA)

    def is_review(self) -> bool:
        return (self.message_type == MESSAGE_TYPE_REVIEW_DATA)
    
    def is_eof(self) -> bool:
        return  (self.message_type == MESSAGE_TYPE_END_OF_DATASET)

    def __str__(self) -> str:
        return f"messageId: {str(self.message_id)} | clientId: {str(self.client_id)} | type: {self.message_type} | payload: {self.message_payload}"


'''
Mensaje para enviar informacion sobre un juego.
'''
class MessageGameInfo(Message):
    def __init__(self, message_id, client_id: int, game: Game):
        self.game = game

        message_payload = (str(game.id) + DATA_DELIMITER + str(game.name) + DATA_DELIMITER + str(game.windows) + DATA_DELIMITER + str(game.mac) + 
                        DATA_DELIMITER + str(game.linux) + DATA_DELIMITER + str(game.positive_reviews) + DATA_DELIMITER + str(game.negative_reviews) + 
                        DATA_DELIMITER + str(game.categories) + DATA_DELIMITER +  str(game.genre) + DATA_DELIMITER + str(game.playTime) + 
                        DATA_DELIMITER + str(game.release_date)
        )

        super().__init__(message_id, client_id, MESSAGE_TYPE_GAME_DATA, message_payload)
    
    def pretty_str(self):
        rta = f"[id: {self.game.id}]\n"
        rta += f"[name: {self.game.name}]\n"
        rta += f"[windows: {str(self.game.windows)}]\n"
        rta += f"[mac: {str(self.game.mac)}]\n"
        rta += f"[linux: {str(self.game.linux)}]\n"
        rta += f"[positive_reviews: {self.game.positive_reviews}]\n"
        rta += f"[negative_reviews: {self.game.negative_reviews}]\n"
        rta += f"[categories: {self.game.categories}]\n"
        rta += f"[genre: {self.game.genre}]\n"
        rta += f"[playtime: {self.game.playTime}]\n"
        rta += f"[release_date: {self.game.release_date}]\n"
        return rta


    def __str__(self) -> str:
        return super().__str__()


    @classmethod
    def from_message(cls, message: Message) -> 'MessageGameInfo':
        if message.message_type != MESSAGE_TYPE_GAME_DATA:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        game = Game(data[0], data[1], string_to_boolean(data[2]), string_to_boolean(data[3]), string_to_boolean(data[4]), int(data[5]), int(data[6]), data[7], data[8], int(data[9]), data[10])
        return cls(message.message_id, message.client_id, game)

'''
Mensaje para enviar informacion sobre una review.
'''
class MessageReviewInfo(Message):
    def __init__(self, message_id, client_id: int, review: Review):
        self.review = review

        message_payload = str(review.game_id) + DATA_DELIMITER + review.game_name + DATA_DELIMITER + review.review_text + DATA_DELIMITER +  str(review.score) + DATA_DELIMITER + review.game_genre
        super().__init__(message_id, client_id, MESSAGE_TYPE_REVIEW_DATA, message_payload)

    def __str__(self) -> str:
        return super().__str__()

    @classmethod
    def from_message(cls, message: Message) -> 'MessageReviewInfo':
        if message.message_type != MESSAGE_TYPE_REVIEW_DATA:
            return None

        data = message.message_payload.split(DATA_DELIMITER)        
        review = Review(data[0], data[1], data[2], data[3], data[4])
        return cls(message.message_id, message.client_id, review)


'''
Mensaje de bienvenida a un nuevo cliente cuando se conecta al servidor
'''
class MessageWelcomeClient(Message):
    def __init__(self, client_id, listen_result_query_port):
        self.client_id = client_id
        self.listen_result_query_port = listen_result_query_port

        message_payload = str(client_id) + DATA_DELIMITER + str(listen_result_query_port)
        super().__init__(USELESS_ID, self.client_id,MESSAGE_TYPE_SERVER_WELCOME_CLIENT, message_payload)

    def __str__(self) -> str:
        return super().__str__()

    @classmethod
    def from_message(cls, message: Message) -> 'MessageWelcomeClient':
        if message.message_type != MESSAGE_TYPE_SERVER_WELCOME_CLIENT:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        return cls(data[0], data[1])

'''
Mensaje que envia el cliente cuando termina de enviar el dataset
'''
class MessageEndOfDataset(Message):
    def __init__(self,message_id, client_id: int, type, last_eof=False):
        self.type = type
        self.last_eof = last_eof

        message_payload = type + DATA_DELIMITER + str(last_eof)
        super().__init__(message_id,client_id, MESSAGE_TYPE_END_OF_DATASET, message_payload)

    def __str__(self) -> str:
        return super().__str__()

    def set_last_eof(self):
        self.last_eof = True
        self.message_payload = self.type + DATA_DELIMITER + str(self.last_eof)
    
    def set_not_last_eof(self):
        self.last_eof = False
        self.message_payload = self.type + DATA_DELIMITER + str(self.last_eof)

    def is_last_eof(self):
        return (self.last_eof == True)

    @classmethod
    def from_message(cls, message: Message) -> 'MessageEndOfDataset':
        if message.message_type != MESSAGE_TYPE_END_OF_DATASET:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        return cls(message.message_id,message.client_id, data[0], string_to_boolean(data[1]))


class MessageQueryOneUpdate(Message):
    def __init__(self,message_id, client_id: int, op_system_supported):
        self.op_system_supported = op_system_supported
        
        super().__init__(message_id,client_id, MESSAGE_TYPE_QUERY_ONE_UPDATE, op_system_supported)
    
    def __str__(self) -> str:
        return super().__str__()

    @classmethod
    def from_message(cls, message: Message) -> 'MessageQueryOneUpdate':
        if message.message_type != MESSAGE_TYPE_QUERY_ONE_UPDATE:
            return None

        return cls(message.message_id,message.client_id, message.message_payload)

class MessageQueryOneFileUpdate(Message):
    def __init__(self, message_id,client_id: int, total_linux, total_mac, total_windows):
        self.total_linux = total_linux
        self.total_mac = total_mac
        self.total_windows = total_windows
        
        message_payload = str(total_linux) + DATA_DELIMITER + str(total_mac) + DATA_DELIMITER + str(total_windows)
        super().__init__(message_id,client_id, MESSAGE_TYPE_QUERY_ONE_FILE_UPDATE, message_payload)
    
    def __str__(self) -> str:
        return super().__str__()

    @classmethod
    def from_message(cls, message: Message) -> 'MessageQueryOneFileUpdate':
        if message.message_type != MESSAGE_TYPE_QUERY_ONE_FILE_UPDATE:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        return cls(message.message_id,message.client_id, int(data[0]), int(data[1]), int(data[2]))

class MessageQueryOneResult(Message):
    def __init__(self, client_id: int, total_linux, total_mac, total_windows):
        self.total_linux = total_linux
        self.total_mac = total_mac
        self.total_windows = total_windows

        message_payload = str(total_linux) + DATA_DELIMITER + str(total_mac) + DATA_DELIMITER + str(total_windows)
        super().__init__(USELESS_ID, client_id, MESSAGE_QUERY_ONE_RESULT, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageQueryOneResult':
        if message.message_type != MESSAGE_QUERY_ONE_RESULT:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        return cls(message.client_id, int(data[0]), int(data[1]), int(data[2]))

class MessageQueryTwoFileUpdate(Message):
    def __init__(self, message_id,client_id: int, top_ten_buffer):
        self.top_ten_buffer = top_ten_buffer
        
        message_payload = ""
        for game_data in top_ten_buffer:
            message_payload +=  game_data[0] + FIELD_DELIMITER + str(game_data[1]) + DATA_DELIMITER 

        message_payload = message_payload[:-1*len(DATA_DELIMITER)]

        super().__init__(message_id,client_id, MESSAGE_TYPE_QUERY_TWO_FILE_UPDATE, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageQueryTwoFileUpdate':
        if message.message_type != MESSAGE_TYPE_QUERY_TWO_FILE_UPDATE:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        top_ten_buffer = []

        for game in data:
            game_data = game.split(FIELD_DELIMITER)
            top_ten_buffer.append((game_data[0], game_data[1]))

        return cls(message.message_id,message.client_id, top_ten_buffer)

class MessageQueryTwoResult(Message):
    def __init__(self, client_id: int, top_ten_buffer):
        self.top_ten_buffer = top_ten_buffer
        
        message_payload = ""
        for game in top_ten_buffer:
            message_payload +=  game[0] + FIELD_DELIMITER + str(game[1]) + DATA_DELIMITER 


        message_payload = message_payload[:-1*len(DATA_DELIMITER)]

        super().__init__(USELESS_ID, client_id, MESSAGE_QUERY_TWO_RESULT, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageQueryTwoResult':
        if message.message_type != MESSAGE_QUERY_TWO_RESULT:
            return None
        
        data = message.message_payload.split(DATA_DELIMITER)
        
        top_ten_buffer = []
        if message.message_payload == "":
            return cls(message.client_id, top_ten_buffer)
        
        for game in data:
            game_data = game.split(FIELD_DELIMITER)
            top_ten_buffer.append((game_data[0], int(game_data[1])))


        return cls(message.client_id, top_ten_buffer)
    
class MessageQueryThreeResult(Message):
    def __init__(self, client_id: int, top_five_buffer):
        self.top_five_buffer = top_five_buffer
        
        message_payload = ""
        for review_data in top_five_buffer:
            message_payload +=  review_data[0] + FIELD_DELIMITER + str(review_data[1]) + DATA_DELIMITER 

        message_payload = message_payload[:-1*len(DATA_DELIMITER)]

        super().__init__(USELESS_ID ,client_id, MESSAGE_QUERY_THREE_RESULT, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageQueryThreeResult':
        if message.message_type != MESSAGE_QUERY_THREE_RESULT:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        buffer = []

        if message.message_payload == "":
            return cls(message.client_id, buffer)
        
        for review in data:
            review_data = review.split(FIELD_DELIMITER)
            buffer.append((review_data[0], int(review_data[1])))

        return cls(message.client_id, buffer)

class MessageQueryThreeFileUpdate(Message):
    def __init__(self, message_id, client_id: int, buffer):
        self.buffer = buffer
        
        message_payload = ""
        for review_data in buffer:
            message_payload +=  review_data[0] + FIELD_DELIMITER + str(review_data[1]) + DATA_DELIMITER 


        message_payload = message_payload[:-1*len(DATA_DELIMITER)]

        super().__init__(message_id,client_id, MESSAGE_TYPE_QUERY_THREE_FILE_UPDATE, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageQueryThreeFileUpdate':
        if message.message_type != MESSAGE_TYPE_QUERY_THREE_FILE_UPDATE:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        buffer = []

        print(f"DATA: {data}")

        for review in data:
            review_data = review.split(FIELD_DELIMITER)
            buffer.append((review_data[0], int(review_data[1])))

        return cls(message.message_id,message.client_id, buffer)

class MessageQueryFourFileUpdate(Message):
    def __init__(self, message_id, client_id: int, buffer):
        self.buffer = buffer
        
        message_payload = ""
        for review_data in buffer:
            message_payload +=  review_data[0] + FIELD_DELIMITER + str(review_data[1]) + DATA_DELIMITER 

        message_payload = message_payload[:-1*len(DATA_DELIMITER)]

        super().__init__(message_id,client_id, MESSAGE_TYPE_QUERY_FOUR_FILE_UPDATE, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageQueryFourFileUpdate':
        if message.message_type != MESSAGE_TYPE_QUERY_FOUR_FILE_UPDATE:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        buffer = []

        for review in data:
            review_data = review.split(FIELD_DELIMITER)
            buffer.append((review_data[0], review_data[1]))

        return cls(message.message_id, message.client_id,buffer)

class MessageQueryFourResult(Message):
    def __init__(self, client_id: int, totals):
        self.totals = totals
        
        message_payload = ""
        for total in totals:
            message_payload +=  total[0] + FIELD_DELIMITER + str(total[1]) + DATA_DELIMITER 

        message_payload = message_payload[:-1*len(DATA_DELIMITER)]

        super().__init__(USELESS_ID, client_id,MESSAGE_QUERY_FOUR_RESULT, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageQueryFourResult':
        if message.message_type != MESSAGE_QUERY_FOUR_RESULT:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        buffer = []

        if message.message_payload == "":
            return cls(message.client_id,buffer)

        for review in data:
            review_data = review.split(FIELD_DELIMITER)
            buffer.append((review_data[0], review_data[1]))

        return cls(message.client_id, buffer)

class MessageQueryFiveFileUpdate(Message):
    def __init__(self, message_id, client_id: int, buffer):
        self.buffer = buffer
        
        message_payload = ""
        for review_data in buffer:
            message_payload +=  str(review_data[0]) + FIELD_DELIMITER + str(review_data[1]) + FIELD_DELIMITER + str(review_data[2]) + FIELD_DELIMITER + str(review_data[3]) + DATA_DELIMITER

        message_payload = message_payload[:-1*len(DATA_DELIMITER)]

        super().__init__(message_id, client_id, MESSAGE_TYPE_QUERY_FIVE_FILE_UPDATE, message_payload)
    
    @classmethod
    def from_message(cls,message: Message) -> 'MessageQueryFiveFileUpdate':
        if message.message_type != MESSAGE_TYPE_QUERY_FIVE_FILE_UPDATE:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        buffer = []

        for review in data:
            review_data = review.split(FIELD_DELIMITER)
            buffer.append((review_data[0], review_data[1], review_data[2], review_data[3]))

        return cls(message.message_id,message.client_id,buffer)


class MessageQueryFiveResult(Message):
    # Ahora totals es un diccionario de la sig forma:
    # {"name": [pos, neg, id]}
    '''
    def __init__(self, client_id: int, totals):
        self.totals = totals
        
        message_payload = ""
        for id, name in totals:
            message_payload +=  str(id) + FIELD_DELIMITER + name + DATA_DELIMITER 

        message_payload = message_payload[:-1*len(DATA_DELIMITER)]

        super().__init__(USELESS_ID,client_id, MESSAGE_QUERY_FIVE_RESULT, message_payload)
    '''

    def __init__(self, client_id: int, totals):
        self.totals = totals
        message_payload = ""
        for game_name, game_data in totals.items():
            message_payload += str(game_name) + FIELD_DELIMITER + str(game_data[0]) + FIELD_DELIMITER + str(game_data[1]) + FIELD_DELIMITER + str(game_data[2]) + DATA_DELIMITER
        
        message_payload = message_payload[:-1*len(DATA_DELIMITER)]
        super().__init__(USELESS_ID,client_id, MESSAGE_QUERY_FIVE_RESULT, message_payload)
    
    '''
    @classmethod
    def from_message(cls, message: Message) -> 'MessageQueryFiveResult':
        if message.message_type != MESSAGE_QUERY_FIVE_RESULT:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        buffer = []

        if message.message_payload == "":
            return cls(message.client_id, buffer)
        
        for elem in data:
            id, name = elem.split(FIELD_DELIMITER)
            buffer.append((id, name))

        return cls(message.client_id,buffer)
    '''

    @classmethod
    def from_message(cls, message: Message) -> 'MessageQueryFiveResult':
        if message.message_type != MESSAGE_QUERY_FIVE_RESULT:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        buffer = {}

        if message.message_payload == "":
            return cls(message.client_id, buffer)
        
        for elem in data:
            name, pos, neg, id = elem.split(FIELD_DELIMITER)
            buffer[name] = [int(pos), int(neg), int(id)]

        return cls(message.client_id,buffer)


class MessageQueryGameDatabase(Message):
    def __init__(self, message_id, client_id: int, game_id):
        self.game_id = game_id

        message_payload = str(game_id)
        super().__init__(message_id, client_id, MESSAGE_TYPE_QUERY_DATABASE, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageQueryGameDatabase':
        if message.message_type != MESSAGE_TYPE_QUERY_DATABASE:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        return cls(message.message_id, message.client_id,str(data[0]))

class MessageClientAskResults(Message):
    def __init__(self, client_id: int):
        message_payload = str(client_id)
        super().__init__(USELESS_ID, client_id, MESSAGE_TYPE_CLIENT_ASK_RESULTS, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageClientAskResults':
        if message.message_type != MESSAGE_TYPE_CLIENT_ASK_RESULTS:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        return cls(message.client_id, str(data[0]))


class ResultStatus(Enum):
    PENDING = "Pending"
    FINISHED = "Finished"
    ERROR = "Error"

class MessageResultStatus(Message):
    def __init__(self, client_id, status: ResultStatus):
        message_payload = status.value
        super().__init__(USELESS_ID, client_id, MESSAGE_TYPE_PEDING_RESULTS, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageResultStatus':
        if message.message_type != MESSAGE_TYPE_PEDING_RESULTS:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        return cls(message.client_id, ResultStatus(str(data[0])))

class MessageResultContent(Message):
    def __init__(self, client_id, content):
        message_payload = content
        super().__init__(USELESS_ID, client_id, MESSAGE_TYPE_CONTENT_RESULTS, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageResultContent':
        if message.message_type != MESSAGE_TYPE_CONTENT_RESULTS:
            return None

        data = message.message_payload.split(DATA_DELIMITER)
        return cls(message.client_id, str(data[0]))
    

class MessageInvalidClient(Message):
    def __init__(self, client_id):
        message_payload = "master-invalid-client"
        super().__init__(USELESS_ID, client_id, MESSAGE_MASTER_INVALID_CLIENT, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageInvalidClient':
        if message.message_type != MESSAGE_MASTER_INVALID_CLIENT:
            return None
        
        return cls(message.client_id)
    

class MessageFinishedClient(Message):
    def __init__(self, client_id):
        message_payload = "finished_client"
        super().__init__(USELESS_ID, client_id, MESSAGE_MASTER_FINISHED_CLIENT, message_payload)
    
    @classmethod
    def from_message(cls, message: Message) -> 'MessageFinishedClient':
        if message.message_type != MESSAGE_MASTER_FINISHED_CLIENT:
            return None
        
        return cls(message.client_id)



        
class MessageBatch(Message):
    def __init__(self, client_id, message_id, message_batch: list[Message]):
        self.batch = message_batch
        message_payload = ""

        for msg in message_batch:
            message_payload += USELESS_ID + FIELD_DELIMITER + str(msg.client_id) + FIELD_DELIMITER + msg.message_type + FIELD_DELIMITER + msg.message_payload + BATCH_DELIMITER
        
        message_payload = message_payload[:-1*len(BATCH_DELIMITER)]
        super().__init__(message_id, client_id, MESSAGE_BATCH_TYPE, message_payload)
        
    def get_batch_id(self):
        #F1_M135
        message_id_info = self.message_id.split("_")
        #print(f" message_id_info: {message_id_info}")
        #["F1", "M135"]
        batch_id = message_id_info[1][1:]
        #"135"
        return int(batch_id)

    def __str__(self) -> str:
        rta = ""
        rta += f"BatchMessage: Type: {self.message_type} BatchId: {self.message_id}\n"
        i = 0
        for msg in self.batch:
            rta += f"Message {i}:\n"
            rta += f"{msg.message_payload}\n"
            i += 1
        return rta
        
    @classmethod
    def from_message(cls, message: Message) -> 'MessageBatch':
        if message.message_type != MESSAGE_BATCH_TYPE:
            return None
        
        batch_list_strings = message.message_payload.split(BATCH_DELIMITER)
        batch_list_messages = []

        for message_string in batch_list_strings:
            msg_info = message_string.split(FIELD_DELIMITER)
            msg_id = msg_info[0]
            clt_id = msg_info[1]
            msg_type = msg_info[2]
            msg_payload = msg_info[3]
            
            msg = Message(msg_id, clt_id, msg_type, msg_payload)
            batch_list_messages.append(msg)
        
        return cls(message.get_client_id(), message.get_message_id(), batch_list_messages)