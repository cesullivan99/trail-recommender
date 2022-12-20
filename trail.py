# Created By  : Carter Sullivan
# Created Date: 10/4/2022
# version ='1.0'
"""This module contains the Trail class, as well as relevant methods"""


class Trail:
    """
    A class representing a trail

    Attributes:
        name (str): The name of the trail
        difficulty (int): the difficulty of the trail
        distance (int): the length of the trail
        descent (int): the length of the trail's descent
        climb (int): the length of the trail's climb
    Methods:
        __init__(name: str, difficulty: int, distance: int, descent: int)
            Constructs a trail object
    """

    # Constructs the trail object
    def __init__(self, name, difficulty, distance, descent, climb):
        """
        The function takes in the name, difficulty, distance, descent, and climb of a trail and assigns them to the
        corresponding attributes of the trail.

        :param name: the name of the trail
        :param difficulty: a number from 1 to 5
        :param distance: the distance of the trail in miles
        :param descent: the total elevation descent in meters
        :param climb: the total elevation gain in meters
        """

        self.name = name
        self.difficulty = difficulty
        self.distance = distance
        # descent/climb ratio
        self.dc = descent / climb

