import requests
from bs4 import BeautifulSoup


# to classify a trail - this is basic, may add more later
class Trail:
    def __init__(self, name, difficulty, rating, distance, descent, climb):
        self.name = name
        self.difficulty = difficulty
        self.rating = rating
        self.distance = distance
        self.descent = descent
        self.climb = climb
