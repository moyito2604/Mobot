# Main executable file for the Mobot Multipurpose bot
# This file brings in the configuration file or generates it and sets up the bots to be used

# imports necessary to run the program
import argparse
import asyncio
import cogs.Dependencies.Functions as Functions
import os
import nextcord
from nextcord.ext import commands
from nextcord.errors import LoginFailure
import configgen
import os.path
import settings
import mysql.connector
from mysql.connector import Error

os.system('clear')

parser = argparse.ArgumentParser()
parser.add_argument('--token', type=str, required=False)
args = parser.parse_args()
# This block of code generates a configuration file if it doesn't exist and imports it for use throughout the program
configgen.generateConfiguration(True, 'TOKEN')
import config

Token = config.Token

# Defines the Intents necessary for the bot to communicate with the discord API
# Also allows the bot to have the permissions needed to run all of its functions
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True

client = commands.Bot(command_prefix='m!', intents=intents, help_command=None, case_insensitive=True)

# This grabs any environment variables from something such as docker
dockerstat = os.environ.get('dockerstatus', False)

# This conditional first checks if it is in a docker container
# If not, it then checks if it recieved a token through commandline arguments
if dockerstat:
    print("Docker Container Detected, Using environment variables instead")
    newtoken = os.environ.get('token', "TOKEN")
    Token = newtoken
# This allows for the token through be inputted through command line arguments with syntax --token TOKEN
elif args.token != None:
    os.system('clear')
    configgen.generateConfiguration(False, args.token)
    Token = args.token

# This sets the working directory for this section of the program
pwd = os.path.dirname(os.path.realpath(__file__))

# This initializes all global variables needed for Mobot
settings.init()

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


# This function simplifies the creation of Guild.txt for the multiple instances that it may be created
# If a database exists, then it places the information in a database
async def guildSave():
    if SQLconnect:
        cursor = settings.connection.cursor(dictionary=True, buffered=True)
        cursor.execute(f"SELECT * FROM Guild_Info")
        table = cursor.fetchall()
        for guild in client.guilds:
            cursor.execute(f"SELECT * FROM Guild_Info WHERE Guild_id = {guild.id}")
            record = cursor.fetchall()
            if record:
                cursor.execute(f"""UPDATE Guild_Info SET
                               Guild_name = "{guild.name}",
                               Members = {guild.member_count},
                               Owner = '{guild.owner}',
                               Owner_id = '{guild.owner.id}' WHERE
                               Guild_id = '{guild.id}'""")
            else:
                cursor.execute(f"""INSERT INTO Guild_Info
                                (Guild_id, Guild_name, Members, Owner, Owner_id) VALUES
                                ('{guild.id}', "{guild.name}", {guild.member_count}, '{guild.owner}', '{guild.owner.id}')""")
        settings.connection.commit()
        cursor.close()
    else:
        if os.path.exists("Guilds.txt"):
            os.remove("Guilds.txt")
        files = open("Guilds.txt", "w")
        for info in client.guilds:
            files.write(
                f"{info.id}\t\tMembers:{info.member_count}\t\t{info.name}\t\t\t{info.owner}\t\tid:{info.owner.id}\n")
        files.close()


# The nextcord on_ready function is used to prepare several things in the discord bot It generates Guild.txt which
# contains the information of the servers the bot is in It also sets the presence of the bot to playing the help
# command and notifies the user of when the bot has logged in and is ready to deploy to servers
@client.event
async def on_ready():
    game = '/help'
    activity = nextcord.Game(name=game, type=3)
    if not os.path.isdir('logs'):
        os.mkdir('logs')
    if SQLconnect:
        for guild in client.guilds:
            try:
                cursor = settings.connection.cursor(dictionary=True, buffered=True)
                cursor.execute(f"""CREATE TABLE {guild.id}_Halls (
                        Channel varchar(50) NOT NULL,
                        Emote varchar(100) NOT NULL,
                        Amount int NOT NULL,
                        Hall varchar(50) NOT NULL,
                        Hall_Emote varchar(100) NOT NULL)""")
                settings.connection.commit()
                cursor.close()
            except Error:
                pass
        try:
            cursor = settings.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(f"""CREATE TABLE Guild_Info (
                    Guild_id varchar(50) NOT NULL,
                    Guild_name varchar(100) NOT NULL,
                    Members int NOT NULL,
                    Owner varchar(50) NOT NULL,
                    Owner_id varchar(50) NOT NULL)""")
        except Error:
            pass
        settings.connection.commit()
        cursor.close()
        try:
            cursor = settings.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(f"""CREATE TABLE Admin_Roles (
                    Guild_id varchar(50) NOT NULL,
                    Role varchar(50) NOT NULL)""")
            settings.connection.commit()
            cursor.close()
        except Error:
            pass
    await guildSave()
    await client.change_presence(status=nextcord.Status.online, activity=activity)
    print('We have logged in as {0.user}\n'.format(client))
    if SQLconnect:
        while True:
            for guild in client.guilds:
                settings.connection.commit()
                cursor = settings.connection.cursor(dictionary=True, buffered=True)
                cursor.execute(f"""SELECT * FROM {guild.id}_Halls""")
                records = cursor.fetchall()
                for record in records:
                    await Functions.historycheck(guild, record['Channel'], record['Hall'], record['Amount'],
                                                 record['Emote'], record['Hall_Emote'])
            print("Halls Check Finished")
            await asyncio.sleep(60 * 60)


# The on_guild_join nextcord function is called when someone joins the server
# This then regenerates the Guild.txt file with refreshed information on the servers stats
@client.event
async def on_guild_join(guild):
    print(f"The bot has joined the Guild \"{guild.name}\"")
    await guildSave()


# The on_guild_remove nextcord function is called when someone leaves the server
# This then regenerates the Guild.txt file with refreshed info on the servers stats
@client.event
async def on_guild_remove(guild):
    print(f"The bot has left the Guild \"{guild.name}\"")
    await guildSave()


# The on_guild_update function runs when something regarding the server as a whole is changed.
# Guild.txt is once again regenerated after this.
@client.event
async def on_guild_update(before, after):
    print(f"Guild \"{before.name}\" has changed the name to \"{after.name}\"")
    await guildSave()


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
    client.run(Token)
except LoginFailure as error:
    if dockerstat:
        print("Invalid Token, please try running the container with a different token")
    else:
        print("Bot Login Error:", error, "Please input a proper token through the --token flag")
