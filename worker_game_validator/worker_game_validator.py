import logging
logging.basicConfig(level=logging.CRITICAL)

from common.game_worker import GameWorker
from common.model.game import Game

class WorkerGameValidator(GameWorker):
    def validate_game(self, game: Game):
        return not game.is_incomplete()
