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
    #the number of different trailforks.com pages with trails from this region, assuming 100 per page
    num_trail_pages = math.ceil(num_trails/100)

    #we pass in None for the df so that a df will be created
    df = scrape_trail_table(url, None)

    # repeat the above process for all pages of trails in the region
    for i in range(1, num_trail_pages):
        #sleep for 5 seconds so we don't annoy trailforks.com :)
        time.sleep(5)
        # URL of the relevant page
        curr_url = "https://www.trailforks.com/region/" + region_name + "/trails/" + "?activitytype=1&page=" + str(i+1)
        scrape_trail_table(curr_url, df)
    print(df)
    return df

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

def load_region_index(region_name):
    # This will be the name of the csv containing the region's data, if  it exists
    region_file = (region_name + "-trails.csv").lower()
    #Will eventually contain the region's trail data
    df = None
    #If we don't already have the file with the region's trail data
    if not exists(region_file):
        # Build a dataframe from the region
        df = build_region_df(region_name)
        # Write the region file to a csv
        #todo: uncomment the below!
        df.to_csv(region_file)
    else:
        df = pd.read_csv(region_file)
    print("the cols of the loaded dataframe are: ")
    print(df.columns)
    print("rows 1, 2, and 3:")
    print(df.loc[0, :])
    print(df.loc[1, :])
    print(df.loc[2, :])




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

    #In the case that a df doeesn't already exist, we create one
    if df is None:
        # Will hold all headers in the trail table
        headers = []

        # For each header in the table, add it to our list of headers
        for head in table.find_all('th'):
            title = head.text.strip()
            headers.append(title)
        #manually setting this value becasue trailforks.com doesn't do it
        headers[2] = "difficulty"
        df = pd.DataFrame(columns=headers)


    # Start at index 1 to avoid including header names, go through each row in the table
    # This code referenced from https://www.youtube.com/watch?v=PY2I4UIZk48
    for row in table.find_all('tr')[1:]:
        data = row.find_all('td')
        #Extracting the portion of data with the trail difficulty
        difficulty_portion = data[2]
        #getting the trail difficulty as a string
        diff_string = difficulty_portion.span['title']
        diff_int = diff_as_int(diff_string)
        row_data = [td.text.strip() for td in data]
        print("row_data before " + str(row_data))
        #manually set the difficulty
        row_data[2] = str(diff_int)
        print("row_data after " + str(row_data))
        length = len(df)
        # Add the data from this row to the table
        df.loc[length] = row_data
    #drop columns that we don't want from the dataframe
    df.drop(['', 'riding area', 'rating'], axis=1, inplace=True)
    print(df)
    return df



