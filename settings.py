# This is a function which generates all the global variables necessary for Mobot
# These variables are used by Music.py and SlashMusic.py

def init():
    global queues, env_vars, channels, current, connection, pwd, owner, client
    # Holds all the Music Queues
    queues = {}
    # Holds all the channels used for messaging
    channels = {}
    # Holds toggleable options such as repeat and shuffle for each Guild
    env_vars = {}
    # Holds the current title and url of the current song for each guild
    current = {}
    # Holds the connection to the SQL Database
    connection = None
    # Holds the Global Directory
    pwd = ""
    # Holds the ID of the Bot Owner
    owner = ""
    # Global Client Variable
    client = ""
