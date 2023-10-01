# This is a function which generates all the global variables necessary for Mobot
# These variables are used by Music.py and SlashMusic.py
def init():
    global queues, timers, titles, downloading, indexes, channels, current, connection
    # Holds all the Music Queues
    queues = {}
    # Holds all the Titles for the Music Queues
    titles = {}
    # Holds all the Asyncio Timers for the Music Queues
    timers = {}
    # Holds all the channels used for messaging
    channels = {}
    # Holds toggleable options such as repeat and shuffle for each Guild
    downloading = {}
    # Makes sure it skips to the next one if shuffle is on
    indexes = {}
    # Holds the current title and url of the current song for each guild
    current = {}
    # Holds the connection to the SQL Database
    connection = None
