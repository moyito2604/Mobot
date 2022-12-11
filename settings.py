#This is a function which generates all of the global variables necessary for Mobot
#These variables are used by Music.py and SlashMusic.py
def init():
    global queues, timers, searches, titles, downloading, indexes, channels, current
    #Holds all of the Music Queues
    queues = {}
    #Holds all of the Titles for the Music Queues
    titles = {}
    #Holds all of the Asyncio Timers for the Music Queues
    timers = {}
    #Holds all of the channels used for messaging
    channels = {}
    #Holds the latest search for each Guild
    searches = {}
    #Holds toggleable options such as repeat and shuffle for each Guild
    downloading = {}
    #Makes sure it skips to the next one if shuffle is on
    indexes = {}
    #Holds the current title and url of the current song for each guild
    current = {}