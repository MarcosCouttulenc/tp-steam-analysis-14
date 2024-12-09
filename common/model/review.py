ACTION_GENRE = "Action"
INDIE_GENRE = "Indie"

class Review:
    def __init__(self, game_id,game_name,review_text,score, genre):
        self.game_id = game_id
        self.game_name = game_name
        self.review_text = review_text
        self.score = score  
        self.game_genre = genre
    
    def set_genre(self, new_genre):
        self.game_genre = new_genre
        
    def is_action(self):
        return (ACTION_GENRE in self.game_genre.split(","))
    
    def is_indie(self):
        return (INDIE_GENRE in self.game_genre.split(","))
    
    def is_positive(self):
        return int(self.score) > 0
    
    def is_negative(self):
        return int(self.score) < 0
    
    def print_review(self):
        print(f"Game: {self.game_name} | Review: {self.review_text} | Score: {self.score} | Genre: {self.game_genre}")
    