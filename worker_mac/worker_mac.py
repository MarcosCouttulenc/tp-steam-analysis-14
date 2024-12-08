import logging
logging.basicConfig(level=logging.CRITICAL)
from common.game_worker import GameWorker
from common.model.game import Game
from common.message import Message, MessageBatch, MessageQueryOneUpdate
class MACOSWorker(GameWorker):
    def validate_game(self, game: Game):
        return game.mac

    def get_message_to_send(self, message: Message):
        msg_batch = MessageBatch.from_message(message)
        next_batch_list = []

        for message in msg_batch.batch:
            msg_query_one_update = MessageQueryOneUpdate(message.message_id, message.get_client_id(), "mac")
            next_batch_list.append(msg_query_one_update)

        new_batch_msg = MessageBatch(msg_batch.get_client_id(), self.get_new_message_id(), next_batch_list)
        return new_batch_msg

    def get_new_message_id(self):
        self.actual_seq_number += 1
        return f"MacF{str(self.id)}_M{str(self.actual_seq_number)}"