import logging
logging.basicConfig(level=logging.CRITICAL)
from common.game_worker import GameWorker
from common.model.game import Game
from common.message import Message


class DecadeWorker(GameWorker):
    def validate_game(self, game: Game):
        # date format: "oct 21, 2008". Decade: last two bytes
        date = game.release_date
        decade_release = int(date[-2:])
        if decade_release in range(10, 20):
            return True
        return False

