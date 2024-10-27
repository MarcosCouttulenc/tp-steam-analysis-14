import logging
logging.basicConfig(level=logging.CRITICAL)
from common.game_worker import GameWorker
from common.model.game import Game
from common.message import Message


class WorkerIndie(GameWorker):
    def validate_game(self, game: Game):
        return game.is_indie()
