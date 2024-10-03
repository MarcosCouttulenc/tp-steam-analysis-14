from common.model.game import Game
from common.model.review import Review

MESSAGE_TYPE_GAME_DATA = "game"
MESSAGE_TYPE_REVIEW_DATA = "review"

MESSAGE_TYPE_SERVER_WELCOME_CLIENT = "server-welcome-client"

'''
Todos los mensajes estan conformados por un tipo y un payload,
el tipo es para indicar que forma o contenido va a tener el payload
y luego el payload es la informacion del mensaje.

Un mensaje va a estar serializado como:
tipo|dato1|dato2| ... |datoN , en la primera posicion vamos a tener siempre el tipo
'''
class Message:
    def __init__(self, message_type, message_payload):
        self.message_type = message_type
        self.message_payload = message_payload

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

        message_payload = str(game.id) + "|" + game.name
        super().__init__(MESSAGE_TYPE_GAME_DATA, message_payload)

    def __str__(self) -> str:
        return super().__str__()

    @classmethod
    def from_message(cls, message: Message) -> 'MessageGameInfo':
        if message.message_type != MESSAGE_TYPE_GAME_DATA:
            return None

        data = message.message_payload.split('|')
        game = Game(data[0], data[1])
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
