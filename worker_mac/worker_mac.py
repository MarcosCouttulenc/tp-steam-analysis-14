import logging
logging.basicConfig(level=logging.CRITICAL)
from common.game_worker import GameWorker
from common.model.game import Game
from common.message import Message

PAYLOAD = "mac"
MESSAGE_TYPE_QUERY_ONE_UPDATE = "query-one-update"

class MACOSWorker(GameWorker):
    def validate_game(self, game: Game):
        return game.mac

    def get_message_to_send(self, message):
        update_message = Message(MESSAGE_TYPE_QUERY_ONE_UPDATE, PAYLOAD)
        return update_message