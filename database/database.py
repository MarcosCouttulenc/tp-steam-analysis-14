import os
from common.model.game import Game
import logging
logging.basicConfig(level=logging.CRITICAL)
FIELD_DELIMITER = '%$'

def getFileName(game_id):
    gameData = int(game_id) // 100000 
    return f"game_{str(gameData)}.txt"

def getIndexName(game_id):
    index = int(game_id) // 100000 
    return f"game_{str(index)}_index.txt"

class DataBase:
    def __init__(self):
        self.total_games = 0
        self.list_number_files = []
        # Cargar el índice al iniciar la base de datos
        #self._load_index()
        
    # def _load_index(self):
    #     # Carga el archivo de índice si existe
    #     if os.path.exists(self.index_file):
    #         with open(self.index_file, 'r') as file:
    #             for line in file:
    #                 game_id, position = line.strip().split(';')
    #                 self.index[int(game_id)] = int(position)  # ID -> Offset


    def hash_function(self, game_id):
        return int(game_id) % 100000


    def _update_index(self,indexNumberFile, game_id, position):
        # Actualiza el índice en memoria y en el archivo de índice
        #self.index[game_id] = position
        with open(indexNumberFile, 'a') as file:
            file.write(f"{game_id};{position}\n")  # Escribir el ID y la posición

    def get_index(self, index_file,game_id):
        with open(index_file, 'r') as file:
            for line in file:
                id, position = line.strip().split(';')
                if id == str(game_id):
                    return int(position)
        
        return None
    
    def store_game(self, game : Game):
        file_name,index_name = getFileName(game.id),getIndexName(game.id)

        if not file_name in self.list_number_files:
            self.list_number_files.append(file_name)
        # Almacena el juego y registra la posición
        with open(file_name, 'a+') as file:
            file.seek(0, os.SEEK_END)
            position = file.tell()  # Obtener posición actual en bytes antes de escribir
            game_entry = (str(game.id) + FIELD_DELIMITER + str(game.name) + FIELD_DELIMITER + str(game.windows) + FIELD_DELIMITER + str(game.mac) + 
                        FIELD_DELIMITER + str(game.linux) + FIELD_DELIMITER + str(game.positive_reviews) + FIELD_DELIMITER + str(game.negative_reviews) + 
                        FIELD_DELIMITER + str(game.categories) + FIELD_DELIMITER +  str(game.genre) + FIELD_DELIMITER + str(game.playTime) + 
                        FIELD_DELIMITER + str(game.release_date) + '\n'
        )  # Formato: ID;Nombre;Género
            file.write(game_entry)  # Escribir el registro

            #self._update_index(index_name,game.id, position, self.hash_function(game.id))
            self._update_index(index_name,game.id, position)

            self.total_games += 1  # Incrementar el contador de juegos

    def get_game(self, game_id):
        # Busca la posición del juego en el índice y lo recupera desde el archivo
        file_name, index_name = getFileName(game_id), getIndexName(game_id)

        position = self.get_index(index_name,game_id)

        if (position == None):
            return Game(-1, "", "False", "False", "False", 0, 0, "", "", 0, "")
        #position = self.get_index(index_name,game.id, self.hash_function(game.id))

        with open(file_name, 'r') as file:
           #print(f"Estoy en el archivo{file_name} y segun el {index_name} tengo que ir a la posicion {position}: \n\n")
            file.seek(position)  # Moverse a la pile.seek(position)  #posición del juego
            game_entry = file.readline().strip()  # Leer la línea completa
            #print("JUEGO ENCONTRADO: \n\n")
            #print(game_entry)
            if game_entry:
                game_data = game_entry.split(FIELD_DELIMITER)
                return Game(game_data[0], game_data[1], game_data[2], game_data[3], game_data[4],
                            game_data[5], game_data[6], game_data[7], game_data[8], game_data[9],
                            game_data[10])

        return Game(-1, "", "False", "False", "False", 0, 0, "", "", 0, "")

    def load_games(self):
        #imprimir todo lo que tengo almacenado.
        games = []
        #logging.critical(self.list_number_files)
        for file_name in self.list_number_files:
            with open(file_name, 'r') as file:
                #logging.critical(f"Estoy en el archivo {file_name} y tengo estas lineas: \n")
                for line in file:
                    pass
                    #logging.critical(line)
                    #print(line)

        return games