import os
from common.model.game import Game
import logging
logging.basicConfig(level=logging.CRITICAL)
FIELD_DELIMITER = '%$'

def getFileName(client_id, game_id):
    gameData = int(game_id) // 100000 
    return f"client_{str(client_id)}game_{str(gameData)}.txt"

def getIndexName(client_id, game_id):
    index = int(game_id) // 100000 
    return f"client_{str(client_id)}_game_{str(index)}_index.txt"

class DataBase:
    def __init__(self):
        self.list_number_files = []

    def hash_function(self, game_id):
        return int(game_id) % 100000

    def _update_index(self, indexNumberFile, game_id, position):
        # Actualiza el índice en memoria y en el archivo de índice
        with open(indexNumberFile, 'a') as file:
            file.write(f"{game_id};{position}\n")  # Escribir el ID y la posición

    def get_index(self, index_file,game_id):
        try:
            with open(index_file, 'r') as file:
                for line in file:
                    id, position = line.strip().split(';')
                    if id == str(game_id):
                        return int(position)
        except FileNotFoundError:
            pass
        
        return None
    
    def store_game(self, client_id: int, game: Game):
        file_name, index_name = getFileName(client_id, game.id), getIndexName(client_id, game.id)

        if not file_name in self.list_number_files:
            self.list_number_files.append(file_name)

        # Almacena el juego y registra la posición
        with open(file_name, 'a+') as file:
            file.seek(0, os.SEEK_END)
            position = file.tell()  # Obtener posición actual en bytes antes de escribir
            game_entry = (str(game.id) + FIELD_DELIMITER + str(game.name) + FIELD_DELIMITER + str(game.windows) + FIELD_DELIMITER + str(game.mac) + 
                         FIELD_DELIMITER + str(game.linux) + FIELD_DELIMITER + str(game.positive_reviews) + FIELD_DELIMITER + str(game.negative_reviews) + 
                         FIELD_DELIMITER + str(game.categories) + FIELD_DELIMITER +  str(game.genre) + FIELD_DELIMITER + str(game.playTime) + 
                         FIELD_DELIMITER + str(game.release_date) + '\n')
            
            # Formato: ID;Nombre;Género
            file.write(game_entry)
            self._update_index(index_name,game.id, position)
            print(f"Juego guardado! {game_entry}")

    def get_game(self, client_id, game_id):
        # Busca la posición del juego en el índice y lo recupera desde el archivo
        file_name, index_name = getFileName(client_id, game_id), getIndexName(client_id, game_id)

        position = self.get_index(index_name, game_id)

        if (position == None):
            return self.get_game_not_found()

        with open(file_name, 'r') as file:
            file.seek(position)  # Moverse a la pile.seek(position)  #posición del juego
            game_entry = file.readline().strip()  # Leer la línea completa

            if game_entry:
                game_data = game_entry.split(FIELD_DELIMITER)
                return Game(game_data[0], game_data[1], game_data[2], game_data[3], game_data[4],
                            game_data[5], game_data[6], game_data[7], game_data[8], game_data[9],
                            game_data[10])

        return self.get_game_not_found()


    def get_game_not_found(self):
        return Game(-1, "", "False", "False", "False", 0, 0, "", "", 0, "")