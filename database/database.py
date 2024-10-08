import os
from common.model.game import Game

def getFileName(game_id):
    gameData = game_id // 100000 
    return f"game_{gameData}.txt"

def getIndexName(game_id):
    index = game_id // 100000 
    return f"game_{index}_index.txt"
class GameDatabaseWithIndex:
    def __init__(self, data_file="games_data.txt", index_file="games_index.txt"):
        self.data_file = data_file
        self.index_file = index_file
        self.index = {}

        # Cargar el índice al iniciar la base de datos
        self._load_index()
        
    # def _load_index(self):
    #     # Carga el archivo de índice si existe
    #     if os.path.exists(self.index_file):
    #         with open(self.index_file, 'r') as file:
    #             for line in file:
    #                 game_id, position = line.strip().split(';')
    #                 self.index[int(game_id)] = int(position)  # ID -> Offset

    def _update_index(self,indexNumberFile, game_id, position):
        # Actualiza el índice en memoria y en el archivo de índice
        #self.index[game_id] = position
        with open(indexNumberFile, 'a') as file:
            file.write(f"{game_id};{position}\n")  # Escribir el ID y la posición

    def get_index(self, index_file,game_id):
        with open(index_file, 'r') as file:
            for line in file:
                game_id, position = line.strip().split(';')
                self.index[int(game_id)] = int(position)
        
    def store_game(self, game : Game):
        file_name = getFileName(game.id)
        # Almacena el juego y registra la posición
        with open(file_name, 'a+') as file:
            file.seek(0, os.SEEK_END)
            position = file.tell()  # Obtener posición actual en bytes antes de escribir
            game_entry = (str(game.id) + "|" + str(game.name) + "|" + str(game.windows) + "|" + str(game.mac) + 
                        "|" + str(game.linux) + "|" + str(game.positive_reviews) + "|" + str(game.negative_reviews) + 
                        "|" + str(game.categories) + "|" +  str(game.genre) + "|" + str(game.playTime) + "|" + str(game.release_date)
        )  # Formato: ID;Nombre;Género
            file.write(game_entry)  # Escribir el registro
            self._update_index(file_name,game.id, position)

    def get_game(self, game):
        # Busca la posición del juego en el índice y lo recupera desde el archivo
        file_name, index_name = getFileName(game.id), getIndexName(game.id)
        position = self.get_index(index_name,game.id)
        with open(file_name, 'r') as file:
            file.seek(position)  # Moverse a la pile.seek(position)  #posición del juego
            game_entry = file.readline().strip()  # Leer la línea completa
            if game_entry:
                return game_entry.split('|')  # Retornar como lista [ID, Nombre, Género]

        return None  # Si no encuentra el registro

