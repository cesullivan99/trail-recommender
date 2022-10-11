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
3. *build_region_index*, which takes the name of a region as input and builds an index of "trail" vectors from that region. This index will be built with the ["annoy"](https://github.com/spotify/annoy/blob/master/README.rst) library, which esentially uses spotify's approach to build an index that scales well as *n* increases. This will be helpful if users want to search larger regions like British Columbia, which contains >100,000 trails.
4. *find_similar trails*, which takes a user's favorite home trail and the region they wish to search as input, then returns the five (approximately) closest trails in the user's specified region using cosine similarity.

## Pseudo code for logic/algorithmic flow

    parse command line for user's favorite home trail url and url of region that they'd like to travel to
    store user's favorite home trail as a new "trail" object
    initial an "annoy index"
    for each page of trails in the specified region:
        for each trail on the page:
            create a new trail object
            add this object to the annoy index
    use the annoy index to find the 5 (or more) trails in the specified region that are most similar to the user's favorite home trail by cosine similarity
    retrieve the urls of these trails, package them in a nice format, and return them to the user
  

## Major data structures

TODO

## Testing plan

TODO
