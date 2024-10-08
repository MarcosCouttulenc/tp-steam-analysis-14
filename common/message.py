from common.model.game import Game
from common.model.review import Review

MESSAGE_TYPE_GAME_DATA = "game"
MESSAGE_TYPE_REVIEW_DATA = "review"
MESSAGE_TYPE_END_OF_DATASET = "end-of-dataset"
MESSAGE_TYPE_QUERY_ONE_UPDATE = "query-one-update"

MESSAGE_TYPE_SERVER_WELCOME_CLIENT = "server-welcome-client"
FALSE_STRING = "False"
TRUE_STRING = "True"

'''
Todos los mensajes estan conformados por un tipo y un payload,
el tipo es para indicar que forma o contenido va a tener el payload
y luego el payload es la informacion del mensaje.

Un mensaje va a estar serializado como:
tipo|dato1|dato2| ... |datoN , en la primera posicion vamos a tener siempre el tipo
'''

def string_to_boolean(string_variable):
    ##print(f"\n\n ESTA LLEGANDO: {string_variable}\n\n")
    if string_variable == TRUE_STRING:
        return True
    elif string_variable == FALSE_STRING:
        return False
    else:
        raise Exception("Variable booleana incorrecta")
class Message:
    def __init__(self, message_type, message_payload):
        self.message_type = message_type
        self.message_payload = message_payload
        #print(message_type)
        #print(message_payload)

    def is_game(self) -> bool:
        return (self.message_type == MESSAGE_TYPE_GAME_DATA)

    def is_review(self) -> bool:
        return (self.message_type == MESSAGE_TYPE_REVIEW_DATA)

    def __str__(self) -> str:
        return f"type: {self.message_type} | payload: {self.message_payload}"


'''
Mensaje para enviar informacion sobre un juego.
'''
class MessageGameInfo(Message):
    def __init__(self, game: Game):
        self.game = game

        message_payload = (str(game.id) + "|" + str(game.name) + "|" + str(game.windows) + "|" + str(game.mac) + 
                        "|" + str(game.linux) + "|" + str(game.positive_reviews) + "|" + str(game.negative_reviews) + 
                        "|" + str(game.categories) + "|" +  str(game.genre) + "|" + str(game.playTime) + "|" + str(game.release_date)
        )

        super().__init__(MESSAGE_TYPE_GAME_DATA, message_payload)

        # print("\n\n imprimo el payload\n ")
        # print(self.message_type)
        # print("\n\nfin del payload\n")
    
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

        data = message.message_payload.split('|')
        game = Game(data[0], data[1], string_to_boolean(data[2]), string_to_boolean(data[3]), string_to_boolean(data[4]), int(data[5]), int(data[6]), data[7], data[8], int(data[9]), data[10])
        return cls(game)


'''
Mensaje para enviar informacion sobre una review.
'''
class MessageReviewInfo(Message):
    def __init__(self, review: Review):
        self.review = review

        message_payload = str(review.game_id) + "|" + review.review
        super().__init__(MESSAGE_TYPE_REVIEW_DATA, message_payload)

    def __str__(self) -> str:
        return super().__str__()

    @classmethod
    def from_message(cls, message: Message) -> 'MessageReviewInfo':
        if message.message_type != MESSAGE_TYPE_REVIEW_DATA:
            return None

        data = message.message_payload.split('|')
        review = Review(data[0], data[1])
        return cls(review)


'''
Mensaje de bienvenida a un nuevo cliente cuando se conecta al servidor
'''
class MessageWelcomeClient(Message):
    def __init__(self, client_id, listen_result_query_port):
        self.client_id = client_id
        self.listen_result_query_port = listen_result_query_port

        message_payload = str(client_id) + "|" + str(listen_result_query_port)
        super().__init__(MESSAGE_TYPE_SERVER_WELCOME_CLIENT, message_payload)

    def __str__(self) -> str:
        return super().__str__()

    @classmethod
    def from_message(cls, message: Message) -> 'MessageWelcomeClient':
        if message.message_type != MESSAGE_TYPE_SERVER_WELCOME_CLIENT:
            return None

        data = message.message_payload.split('|')
        return cls(data[0], data[1])

'''
Mensaje que envia el cliente cuando termina de enviar el dataset
'''
class MessageEndOfDataset(Message):
    def __init__(self, status):
        self.status = status

        message_payload = status
        super().__init__(MESSAGE_TYPE_END_OF_DATASET, message_payload)

    def __str__(self) -> str:
        return super().__str__()

    @classmethod
    def from_message(cls, message: Message) -> 'MessageEndOfDataset':
        if message.message_type != MESSAGE_TYPE_END_OF_DATASET:
            return None

        data = message.message_payload.split('|')
        return cls(data[0])


class MessageQueryOneUpdate(Message):
    def __init__(self, op_system_supported):
        self.op_system_supported = op_system_supported
        
        super().__init__(MESSAGE_TYPE_QUERY_ONE_UPDATE, op_system_supported)
    
    def __str__(self) -> str:
        return super().__str__()

    @classmethod
    def from_message(cls, message: Message) -> 'MessageQueryOneUpdate':
        if message.message_type != MESSAGE_TYPE_QUERY_ONE_UPDATE:
            return None

        # El payload de este tipo de mensaje solo contiene el sistema operativo soportado
        return cls(message.message_payload)
    
