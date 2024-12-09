import logging
logging.basicConfig(level=logging.CRITICAL)
from common.game_worker import GameWorker
from common.model.game import Game
from common.message import Message, MessageBatch, MessageQueryOneUpdate
class MACOSWorker(GameWorker):
    def validate_game(self, game: Game):
        return game.mac

    def get_message_to_send(self, message: Message):
        #print(f"Antes de msg_batch: {message.get_message_id()}")
        msg_batch = MessageBatch.from_message(message)
        #print(f"Dsp de msg_batch: {msg_batch.get_message_id()}")
        next_batch_list = []

        for msg in msg_batch.batch:
            msg_query_one_update = MessageQueryOneUpdate(msg.message_id, message.get_client_id(), "mac")
            next_batch_list.append(msg_query_one_update)

        new_batch_msg = MessageBatch(msg_batch.get_client_id(), msg_batch.get_message_id(), next_batch_list)
        #print(f"Dsp de new_batch_msg: {new_batch_msg.get_message_id()}")
        
        return new_batch_msg

    def get_new_message_id(self):
        self.actual_seq_number += 1
        return f"MacF{str(self.id)}_M{str(self.actual_seq_number)}"