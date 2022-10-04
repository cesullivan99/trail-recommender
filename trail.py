# Created By  : Carter Sullivan
# Created Date: 10/4/2022
# version ='1.0'
# ---------------------------------------------------------------------------
"""This module built to deal with the trail class, and provide related functionality"""
# ---------------------------------------------------------------------------


# to classify a trail - this is basic, will likely add more later
class Trail:
    def __init__(self, name, difficulty, rating, distance, descent, climb):
        self.name = name
        self.difficulty = difficulty
        self.rating = rating
        self.distance = distance
        self.descent = descent
        self.climb = climb
