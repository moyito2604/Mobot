import os
import nextcord
from nextcord.ext import commands
import configgen
import os.path
import settings

def clear():
   # for windows
    if os.name == "nt":
        os.system('cls')
   # for mac and linux
    else:
        os.system('clear')

clear()

configgen.generateConfiguration('m!', True, 'TOKEN', 'TOKEN')
import config
Token = config.Token
extensions = config.extension
seanToken = config.seanToken

intents = nextcord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=extensions, intents=intents, help_command=None, case_insensitive=True)

if Token == 'TOKEN':
    print("No Bot Token Found, please input your Bot Token below")
    bottoken = input()
    clear()
    os.remove("config.py")
    configgen.generateConfiguration('m!', True, bottoken, seanToken)
    Token = bottoken
    

pwd = os.path.dirname(os.path.realpath(__file__))

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

@client.event
async def on_guild_join(guild):
    print(f"The bot has joined the Guild \"{guild.name}\"")
    if os.path.exists("Guilds.txt"):
        os.remove("Guilds.txt")
    files = open("Guilds.txt", "w")
    for info in client.guilds:
        files.write(f"{info.id}\t\tMembers:{info.member_count}\t\t{info.name}\t\t\t{info.owner}\t\tid:{info.owner.id}\n")
    files.close()

@client.event
async def on_guild_remove(guild):
    print(f"The bot has left the Guild \"{guild.name}\"")
    if os.path.exists("Guilds.txt"):
        os.remove("Guilds.txt")
    files = open("Guilds.txt", "w")
    for info in client.guilds:
        files.write(f"{info.id}\t\tMembers:{info.member_count}\t\t{info.name}\t\t\t{info.owner}\t\tid:{info.owner.id}\n")
    files.close()

@client.event
async def on_guild_update(before, after):
    print(f"Guild \"{before.name}\" has changed the name to \"{after.name}\"")
    if os.path.exists("Guilds.txt"):
        os.remove("Guilds.txt")
    files = open("Guilds.txt", "w")
    for info in client.guilds:
        files.write(f"{info.id}\t\tMembers:{info.member_count}\t\t{info.name}\t\t\t{info.owner}\t\tid:{info.owner.id}\n")
    files.close()

settings.init()

extensions = []

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        extensions.append("cogs." + filename[:-3])

if __name__ == '__main__':
    for extension in extensions:
        client.load_extension(extension)

client.run(Token)