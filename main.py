#Main executable file for the Mewbot Multipurpose bot
#This file brings in the configuration file or generates it and sets up the bots to be used

#imports necessary to run the program
import argparse
import importlib
import os
import nextcord
from nextcord.ext import commands
import configgen
import os.path
import settings
os.system('clear')

parser = argparse.ArgumentParser()
parser.add_argument('--token', type = str, required=False)
args = parser.parse_args()
#This block of code generates a configuration file if it doesn't exist and imports it for use throughout the program
configgen.generateConfiguration('m!', True, 'TOKEN', 'TOKEN')
import config
Token = config.Token
extensions = config.extension
seanToken = config.seanToken

#This allows for the token through be inputted through command line arguments with syntax --token TOKEN
if args.token != None:
    configgen.generateConfiguration('m!', False, args.token, seanToken)
    importlib.reload(config)
    Token = config.Token
    extensions = config.extension
    seanToken = config.seanToken

#Defines the Intents necessary for the bot to communicate with the discord API
#Also allows the bot to have the permissions needed to run all of its functions
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix=extensions, intents=intents, help_command=None, case_insensitive=True)

#When the configuration file is generate for the first time, it sets the token to 'TOKEN'
#This allows the user to define the bot token through stdin
#Once the token is properly inputted, it deletes and regenerates the configuration file to include the new token for later use
while len(Token) != 70:
    print("Invalid Bot Token, please input your Bot Token below")
    bottoken = input()
    os.system('clear')
    os.remove("config.py")
    configgen.generateConfiguration('m!', False, bottoken, seanToken)
    importlib.reload(config)
    Token = config.Token
    extensions = config.extension
    seanToken = config.seanToken

#This sets the working directory for this section of the program
pwd = os.path.dirname(os.path.realpath(__file__))

#The nextcord on_ready function is used to prepare several things in the discord bot
#It generates Guild.txt which contains the information of the servers the bot is in
#It also sets the presence of the bot to playing the help command and notifies the user of when the bot has logged in and is ready to deploy to servers
@client.event
async def on_ready():
    game = config.extension + 'help'
    activity = nextcord.Game(name=game, type=3)
    if os.path.exists("Guilds.txt"):
        os.remove("Guilds.txt")
    files = open("Guilds.txt", "w")
    if not os.path.isdir('logs'):
        os.mkdir('logs')
    for info in client.guilds:
        files.write(f"{info.id}\t\tMembers:{info.member_count}\t\t{info.name}\t\t\t{info.owner}\t\tid:{info.owner.id}\n")
    files.close()    
    await client.change_presence(status=nextcord.Status.online, activity=activity)
    print('We have logged in as {0.user}\n'.format(client))

#The on_guild_join nextcord function is called when someone joins the server
#This then regenerates the Guild.txt file with refreshed information on the servers stats
@client.event
async def on_guild_join(guild):
    print(f"The bot has joined the Guild \"{guild.name}\"")
    if os.path.exists("Guilds.txt"):
        os.remove("Guilds.txt")
    files = open("Guilds.txt", "w")
    for info in client.guilds:
        files.write(f"{info.id}\t\tMembers:{info.member_count}\t\t{info.name}\t\t\t{info.owner}\t\tid:{info.owner.id}\n")
    files.close()

#The on_guild_remove nextcord function is called when someone leaves the server
#This then regenerates the Guild.tet file with refreshed info on the servers stats
@client.event
async def on_guild_remove(guild):
    print(f"The bot has left the Guild \"{guild.name}\"")
    if os.path.exists("Guilds.txt"):
        os.remove("Guilds.txt")
    files = open("Guilds.txt", "w")
    for info in client.guilds:
        files.write(f"{info.id}\t\tMembers:{info.member_count}\t\t{info.name}\t\t\t{info.owner}\t\tid:{info.owner.id}\n")
    files.close()

#The on_guild_update function runs when something regarding the server as a whole is changed.
#Guild.txt is once again regenerated after this.
@client.event
async def on_guild_update(before, after):
    print(f"Guild \"{before.name}\" has changed the name to \"{after.name}\"")
    if os.path.exists("Guilds.txt"):
        os.remove("Guilds.txt")
    files = open("Guilds.txt", "w")
    for info in client.guilds:
        files.write(f"{info.id}\t\tMembers:{info.member_count}\t\t{info.name}\t\t\t{info.owner}\t\tid:{info.owner.id}\n")
    files.close()

#This initializes all global variables needed for mewbot
settings.init()

extensions = []

#From here, all of the cogs used in this bot are loaded in and added to the bots features so that they are usable later
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        extensions.append("cogs." + filename[:-3])

if __name__ == '__main__':
    for extension in extensions:
        client.load_extension(extension)

client.run(Token)