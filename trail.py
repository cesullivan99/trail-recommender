# Created By  : Carter Sullivan
# Created Date: 10/4/2022
# version ='1.0'
"""This module contains the Trail class, as well as relevant methods"""
from bs4 import BeautifulSoup
import requests
from annoy import AnnoyIndex
import pandas as pd
import math
import time
from os.path import exists


class Trail:
    """
    A class representing a trail

    Attributes:
        title (str): The name of the trail
        difficulty (int): The difficulty of the trail, an integer between 1 and 9
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
    def __init__(self, title, difficulty, distance, descent, climb):
        """
        The function takes in the name, distance, descent, and climb of a trail and assigns them to the
        corresponding attributes of the trail.

        :param title: the name of the trail
        :param difficulty: the difficulty of the trail, a integer between 1 and 9
        :param distance: the distance of the trail in miles
        :param descent: the total elevation descent in meters
        :param climb: the total elevation gain in meters
        """

        self.title = title
        self.difficulty = difficulty
        self.distance = distance
        self.descent = descent
        self.climb = climb

    def __str__(self):
        """
        The function returns a string representation of the trail object

        :return: a string representation of the trail
        """
        title_str = "Trail name: " + self.title
        difficulty_str = "Difficulty: " + str(self.difficulty)
        distance_str = "Distance: " + str(self.distance)
        descent_str = "Descent: " + str(self.descent)
        climb_str = "Climb: " + str(self.climb)
        stringy = title_str + '\n' + difficulty_str + '\n' + distance_str + '\n' + descent_str + '\n' + climb_str + '\n'
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

    # Find the part of the soup concerning trail difficulty
    diff = soup.find(class_="title-type larger diffratingvoteLink")
    # find the string concerning trail difficulty
    diff_string = diff.span['title']
    # convert trail difficulty to an integer
    diff_int = diff_as_int(diff_string)

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

    # initializing attributes to 0
    distance_num, climb_num, descent_num = 0, 0, 0

    if "Distance" in attributes:
        # Distance in feet
        distance_num = dist_in_ft(attributes["Distance"])
    if "Climb" in attributes:
        # Climb in feet
        climb_num = dist_in_ft(attributes["Climb"])
    if "Descent" in attributes:
        # Descent in feet
        descent_num = dist_in_ft(attributes["Descent"])

    trail_obj = Trail(title=trail_name, difficulty=diff_int, distance=distance_num, descent=descent_num,
                      climb=climb_num)
    print(trail_obj)
    return trail_obj


def load_region_index(region_name):
    # This will be the name of the csv containing the region's data, if  it exists
    region_file = (region_name + "-trails.csv").lower()
    # Will eventually contain the region's trail data
    df = None
    # If we don't already have the file with the region's trail data
    if not exists(region_file):
        # Build a dataframe from the region
        df = build_region_df(region_name)
        # Write the region file to a csv
        df.to_csv(region_file)
    else:
        df = pd.read_csv(region_file)
    print("the loaded dataframe is: ")
    print(df)
    # Convert the df to numpy arrays
    array = df[['difficulty', 'distance', 'descent', 'climb']].to_numpy()
    print(array)


def build_region_df(region_name):
    """
    A function that takes in the name of a region and saves the trail data of that region to a pandas dataframe.
    This dataframe is returned.

    :param region_name: the name of the region
    :return: the dataframe containing data for the region's trails
    """
    # URL of the region page on Trailforks.com
    url = "https://www.trailforks.com/region/" + region_name + "/trails/"

    # this equals the number of trails in the given region (we find this so we know how many pages of trails to loop through in the following code)
    num_trails = num_trails_in_rgn(url)
    # the number of different trailforks.com pages with trails from this region, assuming 100 per page
    num_trail_pages = math.ceil(num_trails / 100)

    # we pass in None for the df so that a df will be created
    df = scrape_trail_table(url, None)

    # repeat the above process for all pages of trails in the region
    for i in range(1, num_trail_pages):
        # sleep for 5 seconds so we don't annoy trailforks.com :)
        time.sleep(5)
        # URL of the relevant page
        curr_url = "https://www.trailforks.com/region/" + region_name + "/trails/" + "?activitytype=1&page=" + str(
            i + 1)
        scrape_trail_table(curr_url, df)
    # drop columns that we don't want from the dataframe
    df.drop(['', 'riding area', 'rating'], axis=1, inplace=True)
    #Convert all distances in the df to distances in feet
    column_names = ['distance', 'descent', 'climb']
    #convert all distances to integer distances in feet
    df[column_names] = df[column_names].applymap(dist_in_ft)
    return df


def scrape_trail_table(url, df=None):
    """
    This function takes in a url and a dataframe object and scrapes the data from the url's trail table into the given dataframe.
    The modified dataframe is returned.
    Note that the given url must lead to a trailforks.com page containing a table of trails.
    Also, note that a url can be passed in without a dataframe. In this case, a dataframe will be created and returned.

    :param url: the url to a page of trails on trailforks.com
    :param df: The dataframe
    """
    # Send a GET request to the page
    response = requests.get(url)

    # create a new soup with lxml library
    soup = BeautifulSoup(response.text, 'lxml')

    # Find the trail table in this soup
    table = soup.find(id="trails_table")

    # In the case that a df doeesn't already exist, we create one
    if df is None:
        # Will hold all headers in the trail table
        headers = []

        # For each header in the table, add it to our list of headers
        for head in table.find_all('th'):
            title = head.text.strip()
            headers.append(title)
        # manually setting this value becasue trailforks.com doesn't do it
        headers[2] = "difficulty"
        df = pd.DataFrame(columns=headers)

    # Start at index 1 to avoid including header names, go through each row in the table
    # This code referenced from https://www.youtube.com/watch?v=PY2I4UIZk48
    for row in table.find_all('tr')[1:]:
        data = row.find_all('td')
        # Extracting the portion of data with the trail difficulty
        difficulty_portion = data[2]
        # getting the trail difficulty as a string
        diff_string = difficulty_portion.span['title']
        diff_int = diff_as_int(diff_string)
        row_data = [td.text.strip() for td in data]
        # manually set the difficulty
        row_data[2] = diff_int
        length = len(df)
        # Add the data from this row to the table
        df.loc[length] = row_data
    return df


# Helper functions below

def dist_in_ft(num_str):
    """
    This function takes in a string representing a distance (in feet or miles) and converts it to an integer number of feet.

    :param num_str: The string representing the distance
    """
    # remove commas, which may mess with the numbers here
    num_str = num_str.replace(",", "")
    # if the input represented in miles, convert it to feet
    if "miles" in num_str or "mile" in num_str:
        return_val = int(5280 * float(num_str.split()[0]))
        #print("we return " + str(return_val))
        return return_val
    # if input is in feet, just convert it to an integer
    elif "ft" in num_str:
        return_val = int(num_str.split()[0])
        #print("we return " + str(return_val))
        return return_val


def num_trails_in_rgn(region_url):
    """
    > This function takes the url of a trailforks.com region and returns the number of trails in that region.

    :param region_url: the url of the region you want to get the number of trails for
    """

    response = requests.get(region_url)
    # Parse the page's HTML
    name_soup = BeautifulSoup(response.text, 'html.parser')
    # this equals the number of trails in the given region (we find this so we know how many pages of trails to loop through in the following code)
    num_trails = int(name_soup.find("div", class_="resultTotal").strong.string)
    print("there are " + str(num_trails) + " trails in the region.")
    return num_trails


def diff_as_int(diff_string):
    """
    It takes a string representing a trail difficulty, then return an int representing that difficulty as an integer

    :param diff_string: The string that contains the difficulty of the trail
    """
    if diff_string == "Access Road/Trail":
        return 1
    elif diff_string == "Secondary Access Road/Trail":
        return 2
    elif diff_string == "Easiest / White Circle":
        return 3
    elif diff_string == "Easy / Green Circle":
        return 4
    elif diff_string == "Intermediate / Blue Square":
        return 5
    elif diff_string == "Very Difficult / Black Diamond":
        return 6
    elif diff_string == "Extremely Difficult / Dbl Black Diamond":
        return 7
    elif diff_string == "Extremely dangerous, pros only!":
        return 8
    elif diff_string == "Chairlifts & gondolas":
        return 9
