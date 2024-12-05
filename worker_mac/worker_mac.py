import logging
logging.basicConfig(level=logging.CRITICAL)
from common.game_worker import GameWorker
from common.model.game import Game
from common.message import Message, MessageQueryOneUpdate
class MACOSWorker(GameWorker):
    def validate_game(self, game: Game):
        return game.mac

    def get_message_to_send(self, message: Message):
        update_message = MessageQueryOneUpdate(message.message_id, message.get_client_id(), "mac")
        return update_message

    def get_new_message_id(self):
        self.actual_seq_number += 1
        return f"MacF{str(self.id)}_M{str(self.actual_seq_number)}"