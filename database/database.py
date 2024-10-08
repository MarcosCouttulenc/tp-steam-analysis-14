import csv

class gameDataBase:
    def __init__(self):
        pass

    def _get_file_name(self, gameID):
        file_number = gameID // 100000
        return f'games_{file_number}.csv'
    
    def storeGame(self,game):
        file_name = self._get_file_name(game.id)
        with open(file_name, 'a+') as file:
            writer = csv.writer(file)
            writer.writerow([game.id, game.name, game.windows, game.mac, game.linux, game.positive_reviews, game.negative_reviews, game.categories, game.genre, game.playTime, game.release_date])

    
    def get_game(self, gameID):
        file_name = self._get_file_name(gameID)
        with open(file_name, 'r') as file:
            #falta implementar el metodo de busqueda por indice
            reader = csv.reader(file)
            for row in reader:
                if row[0] == gameID:
                    return row
        return None