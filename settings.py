#This is a function which generates all of the global variables necessary for Mobot
#These variables are used by Music.py and SlashMusic.py
def init():
    global queues, timers, searches, titles, downloading, indexes, channels
    queues = {}
    timers = {}
    searches = {}
    titles = {}
    downloading = {}
    channels = {}
    indexes = {}