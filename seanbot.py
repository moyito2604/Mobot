import nextcord
import sys
import os
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)) + '/Cogs/Dependencies/')
import dccommands
import config
os.system("clear")

seanToken = config.seanToken

seanclient = nextcord.Client()

@seanclient.event
async def on_ready():
    game = 'sean'
    activity = nextcord.Game(name=game, type=3)
    await seanclient.change_presence(status=nextcord.Status.online, activity=activity)
    print('We have logged in as {0.user}\n'.format(seanclient))

@seanclient.event
async def on_message(message):
    if message.author == seanclient.user:
        return
    
    if message.content.lower() == ('sean'):
        await message.channel.send(dccommands.seanQuotes())
        print("Response to sean printed")

    elif message.content.lower() == ('seam'):
        await message.channel.send(dccommands.oneSeam())
        print("Response to seam printed")
    
seanclient.run(seanToken)
