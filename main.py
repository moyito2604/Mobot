# Main executable file for the Mobot Multipurpose bot
# This file brings in the configuration file or generates it and sets up the bots to be used

# imports necessary to run the program
import argparse
import Dependencies.Functions as Functions
import nextcord
from nextcord.ext import commands
from nextcord.errors import LoginFailure
import jsonbuilder
import os.path
import settings
import mysql.connector
from mysql.connector import Error

os.system('clear')

# Provides colors for outputs
color = Functions.Color

parser = argparse.ArgumentParser()
parser.add_argument('--token', type=str, required=False)
args = parser.parse_args()
# This block of code generates a configuration file if it doesn't exist and imports it for use throughout the program
config = jsonbuilder.importConfiguration()

Token = config.get("Token", "None")

# Defines the Intents necessary for the bot to communicate with the discord API
# Also allows the bot to have the permissions needed to run all of its functions
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True

client = commands.Bot(command_prefix='m!', intents=intents, help_command=None, case_insensitive=True)

# This initializes all global variables needed for Mobot
settings.init()

# This sets the working directory for this section of the program
settings.pwd = os.path.dirname(os.path.realpath(__file__))

# Sets the ID of the Owner and proxy of the bot
settings.owner = config.get("OwnerID", "None")
settings.proxy = config.get("Proxy", "None")

# This grabs any environment variables from something such as docker
dockerstat = os.environ.get('dockerstatus', False)

# This conditional first checks if it is in a docker container
# If not, it then checks if it recieved a token through commandline arguments
if dockerstat:
    print("Docker Container Detected, Using environment variables instead")
    Token = os.environ.get('token', "TOKEN")
    settings.owner = os.environ.get('ownerid', "ID")
    settings.proxy = os.environ.get('proxy', "None")
# This allows for the token through be inputted through command line arguments with syntax --token TOKEN
elif args.token is not None:
    os.system('clear')
    config['Token'] = args.token
    Token = args.token

# It then regenerates the config.json file with updated information
config['Token'] = config.get("Token", "None")
config['OwnerID'] = config.get("OwnerID", "None")
config['Proxy'] = config.get("Proxy", "None")
jsonbuilder.exportConfiguration(config)

# Grabs Environment Variables for
SQLHost = os.environ.get('MYSQL_HOST', None)
database = os.environ.get('MYSQL_DATABASE', None)
dbuser = os.environ.get('MYSQL_USER', None)
dbpassword = os.environ.get('MYSQL_PASSWORD', None)
port = os.environ.get('MYSQL_PORT', 3306)

# Initializes the MySQL connection
SQLconnect = True
try:
    connection = mysql.connector.connect(host=SQLHost,
                                         database=database,
                                         user=dbuser,
                                         password=dbpassword,
                                         port=port)
    settings.connection = connection
except Error as e:
    print("Error while connecting to MySQL", e)
    SQLconnect = False

if SQLconnect:
    print("Connected to MySQL Server Version", settings.connection.get_server_info())

extensions = []

# From here, all the cogs used in this bot are loaded in and added to the bots features so that they are usable later
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        if filename == "Halls.py" and not SQLconnect:
            print("Database connection failed, Halls are disabled")
        elif filename == "Admin.py" and not SQLconnect:
            print("Database connection failed, Admin Commands are disabled")
        else:
            extensions.append("cogs." + filename[:-3])

if __name__ == '__main__':
    for extension in extensions:
        client.load_extension(extension)

try:
    settings.client = client
    client.run(Token)
except LoginFailure as error:
    if dockerstat:
        print("Invalid Token, please try running the container with a different token")
    else:
        print("Bot Login Error:", error, "Please input a proper token through the --token flag")
