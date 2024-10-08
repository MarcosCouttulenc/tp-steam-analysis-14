import csv

class Game:
    def __init__(self, id ,name,windows,mac,linux,positive_reviews,
                 negative_reviews,categories, genre, playTime, release_date):
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
        self.release_date = release_date



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