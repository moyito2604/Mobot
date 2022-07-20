#This is a function which generates all of the global variables necessary for mewbot
#These variables are used by Music.py and SlashMusic.py
def init():
    global queues, timers, searches, titles, downloading, saveq, savet, saved, indexes, channels
    queues = {}
    timers = {}
    searches = {}
    titles = {}
    downloading = {}
    saveq = {}
    savet = {}
    saved = {}
    channels = {}
    indexes = {}