# Created By  : Carter Sullivan
# Created Date: 10/4/2022
# version ='1.0'
"""This module contains the Trail class, as well as relevant methods"""
from bs4 import BeautifulSoup
import requests
from annoy import AnnoyIndex
import pandas as pd


class Trail:
    """
    A class representing a trail

    Attributes:
        name (str): The name of the trail
        distance (int): the length of the trail
        descent (int): the length of the trail's descent
        climb (int): the length of the trail's climb
    Methods:
        __init__(name: str, difficulty: int, distance: int, descent: int)
            Constructs a trail object
        __str__:
            Prints a string representation of the trail
    """

    # Constructs the trail object
    def __init__(self, name, distance, descent, climb):
        """
        The function takes in the name, distance, descent, and climb of a trail and assigns them to the
        corresponding attributes of the trail.

        :param name: the name of the trail
        :param distance: the distance of the trail in miles
        :param descent: the total elevation descent in meters
        :param climb: the total elevation gain in meters
        """

        self.name = name
        self.distance = distance
        # descent/climb ratio
        self.dc = descent / climb

    def __str__(self):
        """
        The function returns the name of the trail

        :return: the name of the trail
        """
        stringy = "Trail name: " + self.name + '\n' + "Distance: " + str(
            self.distance) + '\n' + "Descent/climb ratio: " + str(self.dc)
        return stringy


def trail_new(trail_name):
    """
    A function that takes in the name of a trail and returns a trail object. It does this by scraping details regarding
    the trail from trailforks.com.

    :param trail_name: the name of the trail
    :return: the trail object
    """

    # URL of the trail page on trailforks.com
    url = 'https://www.trailforks.com/trails/' + trail_name

    # Request the page's HTML from trailforks.com
    response = requests.get(url)

    # Parse the page's HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # find the block of basic trail stats that we want
    stats = soup.find(id="basicTrailStats")

    # separate out each individual attribute (distance, climb, descent, etc.) of trail stats
    condensed_stats = stats.find_all("div", class_="col-3")

    # remove the tags surrounding attributes
    condensed_stats = [stat.contents for stat in condensed_stats]

    # create a dictionary of our attributes
    attributes = {}
    for i in range(len(condensed_stats)):
        curr = condensed_stats[i]
        # the name of the attribute
        att = curr[3].string
        # the value of the attribute
        stat = curr[1].string
        # add to the dictionary
        attributes[att] = stat

    if "Distance" in attributes:
        # Distance in feet
        distance_num = dist_in_ft(attributes["Distance"])
    if "Climb" in attributes:
        # Climb in feet
        climb_num = dist_in_ft(attributes["Climb"])
    if "Descent" in attributes:
        # Descent in feet
        descent_num = dist_in_ft(attributes["Descent"])

    trail_obj = Trail(name=trail_name, distance=distance_num, descent=descent_num, climb=climb_num)
    return trail_obj


def build_region_index(region_name):
    """
    A function that takes in the name of a region and returns a AnnoyIndex object

    :param region_name: the name of the region
    :return: the AnnoyIndex object
    """
    # URL of the region page on Trailforks.com
    url = "https://www.trailforks.com/region/" + region_name + "/trails/"
    # Send a GET request to the page
    response = requests.get(url)

    # Parse the page's HTML
    name_soup = BeautifulSoup(response.text, 'html.parser')
    # this equals the number of trails in the given region (we find this so we know how many pages of trails to loop through in the following code)
    num_trails = int(name_soup.find("div", class_="resultTotal").strong.string)

    # dimension of a trail object
    # At the moment, there are 3 instance variables per object, so this value is 3
    trail_dim = 3

    # create an AnnoyIndex object to store each trail in the region as a trail object
    # It is angular because we'll be using cosine distance
    idx = AnnoyIndex(trail_dim, 'angular')

    # create a new soup with lxml library
    soup = BeautifulSoup(response.text, 'lxml')

    # Find the trail table in this soup
    table = soup.find(id="trails_table")

    #Will hold all headers in the trail table
    headers = []

    # For each header in the table, add it to our list of headers
    for head in table.find_all('th'):
        title = head.text.strip()
        headers.append(title)
    print(headers)

    df = pd.DataFrame(columns=headers)

    # Start at index 1 to avoid including header names, go through each row in the table
    # This code referenced from https://www.youtube.com/watch?v=PY2I4UIZk48
    for row in table.find_all('tr')[1:]:
        data = row.find_all('td')
        row_data = [td.text.strip() for td in data]
        length = len(df)
        # Add the data from this row to the table
        df.loc[length] = row_data
    print(df)


def dist_in_ft(num_str):
    """
    This function takes in a string representing a distance (in feet or miles) and converts it to an integer number of feet.

    :param num_str: The string representing the distance
    """
    # remove commas, which may mess with the numbers here
    num_str = num_str.replace(",", "")
    # if the input represented in miles, convert it to feet
    if "miles" in num_str:
        return int(5280 * float(num_str.split()[0]))
    # if input is in feet, just convert it to an integer
    elif "ft" in num_str:
        return int(num_str.split()[0])
