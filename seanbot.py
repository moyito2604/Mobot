# This is the source code for seanbot
# This is completely separate code from Mobot and is not intended for use by anyone

import nextcord
import os
from nextcord.ext import commands
import cogs.Dependencies.dccommands as dccommands
import config

os.system("clear")

seanToken = config.seanToken
intent = nextcord.Intents.default()
intent.message_content = True
seanclient = commands.Bot(command_prefix='!', intents=intent)


# Sets the presence of seanbot to 'sean'
@seanclient.event
async def on_ready():
    game = 'sean'
    activity = nextcord.Game(name=game, type=3)
    await seanclient.change_presence(status=nextcord.Status.online, activity=activity)
    print('We have logged in as {0.user}\n'.format(seanclient))


# Returns a single sean quote
@seanclient.event
async def on_message(message):
    if message.author == seanclient.user:
        return

    if message.content.lower() == 'sean':
        await message.channel.send(dccommands.seanQuotes())
        print("Response to sean printed")

    elif message.content.lower() == 'seam':
        await message.channel.send(dccommands.oneSeam())
        print("Response to seam printed")


seanclient.run(seanToken)
