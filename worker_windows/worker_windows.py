import logging
logging.basicConfig(level=logging.CRITICAL)
from common.game_worker import GameWorker
from common.model.game import Game
from common.message import Message, MessageQueryOneUpdate

class WINDOWSWorker(GameWorker):
    def validate_game(self, game: Game):
        return game.windows

    def get_message_to_send(self, message: Message):
        update_message = MessageQueryOneUpdate(message.message_id, message.get_client_id(), "windows")
        return update_message