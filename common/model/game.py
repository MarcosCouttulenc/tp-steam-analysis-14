import csv

class Game:
    def __init__(self, id, name,linux,windows,mac,positive_reviews,
                 negative_reviews,playTime,categories, genre,):
        self.id = id
        self.name = name
        self.positive_reviews = positive_reviews
        self.negative_reviews = negative_reviews
        self.linux = linux
        self.windows = windows
        self.mac = mac
        self.categories = categories
        self.genre = genre
        self.playTime = playTime



    # def storeGame(self, game):
    #     with open('BDDGames.csv', 'a+') as file:
    #         writer = csv.writer(file)
    #         writer.writerow([self.id, self.name])

    # def loadGames(self):
    #     games = []
    #     with open('BDDGames.csv', 'r') as file:
    #         reader = csv.reader(file)
    #         for row in reader:
    #             games.append(row[0], row[1])
    #     return games