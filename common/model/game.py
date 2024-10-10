ACTION_GENRE = "Action"
INDIE_GENRE = "Indie"
INCOMPLETE = ""

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

    def is_incomplete(self) -> bool:
        values = [self.id, self.name, self.positive_reviews, self.negative_reviews, self.linux, self.windows, self.mac, self.genre, self.playTime, self.release_date]
        for value in values:
            if value == INCOMPLETE:
                return True
        return False



    def is_indie(self) -> bool:
        return INDIE_GENRE in self.genre.split(",")
    
    def is_action(self) -> bool:
        return ACTION_GENRE in self.genre.split(",")
    
    def pretty_str(self):
        rta = f"[id: {self.id}]\n"
        rta += f"[name: {self.name}]\n"
        rta += f"[windows: {str(self.windows)}]\n"
        rta += f"[mac: {str(self.mac)}]\n"
        rta += f"[linux: {str(self.linux)}]\n"
        rta += f"[positive_reviews: {self.positive_reviews}]\n"
        rta += f"[negative_reviews: {self.negative_reviews}]\n"
        rta += f"[categories: {self.categories}]\n"
        rta += f"[genre: {self.genre}]\n"
        rta += f"[playtime: {self.playTime}]\n"
        rta += f"[release_date: {self.release_date}]\n"
        return rta