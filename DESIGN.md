# Trail Recommender
## Design Spec

An outline of the trail recommender's design. Note that this document is modeled off of the Dartmouth College COSC50 lab 3 design spec.

## User interface

Eventually, I will provide the trail recommender with an aesthetically pleasing UI (this will be done with a tool like PySimpleGUI). For the time being,
however, it will simply take user input with basic Python I/O.

## Inputs and outputs

*Input:* The user will input
 * the name of their favorite home trail
 * the name of a region that they're interested in traveling to

*Output:* 

  * a list of Trailforks.com urls of the five trails in the specified region that are most similar to the user's favorite home trail
  
  Note: For the time being, this output will be formatted as a series of links, but when the GUI interface is created for the trail recommender, the output   will be presented in a more aesthetically pleasing manner.

## Functional decomposition into modules

1. *main*, which initializes other modules and takes user input
2. *trail_new*, which initializes a new "trail" object
3. *build_region_index*, which takes the name of a region as input and builds an index of "trail" vectors from that region. This index will be built with the ["annoy"](https://github.com/spotify/annoy/blob/master/README.rst) library, which esentially uses Spotify's approach to build an index that scales well as *n* increases. This will be helpful if users want to search larger regions like British Columbia, which contains >100,000 trails. To get the raw data into the index, Scrapy will be used to scrape Trailforks.com.
4. *find_similar_trails*, which takes a user's favorite home trail and the region they wish to search as input, then returns the five (approximately) closest trails in the user's specified region using cosine similarity.

## Pseudo code for logic/algorithmic flow

    parse command line for user's favorite home trail url and url of region that they'd like to travel to
    check for validity of user input
    store user's favorite home trail as a new "trail" object (this entails scraping that trail's data from Trailforks.com)
    initialize an "annoy index"
    for each Trailforks.com page of trails in the specified region:
        for each trail on the page:
            create a new trail object
            add this object to the annoy index
    use the annoy index to find the 5 (or more) trails in the specified region that are most similar to the user's favorite home trail by cosine similarity
    retrieve the urls of these trails, package them in a nice format, and return them to the user

## Major data structures

### Trail Object
   * Trail Name
   * Trail Difficulty
   * Climb/Descent ratio

## Testing plan

First, I'll write the *trail_new* method to create a trail object from trailforks using Scrapy. I'll then test it on several Trailforks trails, as well as several errant inputs, to ensure it works. Next, I'll write *build_region_index*, and create an index from a small region. I'll print all items in the index, and manually check that they're correct. I'll do this for multiple regions, ensuring that the index is built properly. After this, I'll build and test *find_similar_trails*, first performing a "sanity check" with very small regions and then moving on to larger regions. After completing these tasks, I may add more features to the trail object (i.e. a vectorized representation of trail description text) and expand the user interface.
