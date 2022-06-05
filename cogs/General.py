import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import sys
import os
import time
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)) + '/Dependencies/')
import dccommands
import config
import configgen

Token = config.Token
extensions = config.extension
seanToken = config.seanToken

class General(commands.Cog):

    def __init__(self, client):
        print("General Initialized Successfully")
        self.client = client

    @nextcord.slash_command(name="ping", description="Check bots ping!")
    async def pingtest(self, interaction : Interaction):
        embed = nextcord.Embed(title=(f"My ping is {round(self.client.latency* 1000)}ms"))
        await interaction.response.send_message(embed=embed)

    @commands.command(pass_context = True)
    async def ce(self, ctx, extension):
        await ctx.send('The extension has been changed to ' + extension)
        configgen.generateConfiguration(extension, False, Token, seanToken)
        config.extension = extension
        print('Command extension changed to ' + config.extension + ' successfully')
        game = config.extension + 'help'
        activity = nextcord.Game(name=game, type=3)
        await self.client.change_presence(status=nextcord.Status.online, activity=activity)
        os.system('python3 main.py')

    @commands.command(pass_context = True)
    async def deez(self, ctx):
        await ctx.send('Nutz')
        time.sleep(1)
        await ctx.send('GOTTEM!')
        print("Response to deez printed")

    @commands.command(pass_context = True)
    async def tquote(self, ctx):
        await ctx.send(dccommands.techQuotes())
        print("Response to tquote printed")

    @commands.command(pass_context = True)
    async def ding(self, ctx):
        await ctx.send('dong')
        print("Response to ding printed")

    @commands.command(pass_context = True)
    async def help(self, ctx):
        hm = '```***List of Commands you can use***\n\n'
        hm = hm + extensions + 'ding: replies with dong\n'
        hm = hm + extensions + 'deez: replies with nutz\n'
        hm = hm + extensions + 'tquote: Generates a tech quote\n\n'
        hm = hm + '***Music Bot Commands***\n'
        hm = hm + extensions + 'join: joins voice channel\n'
        hm = hm + extensions + 'leave: leaves voice channel\n'
        hm = hm + extensions + 'play: plays music with a youtube link, queues music, and plays music currently paused\n'
        hm = hm + 'This command also allows you to search for a song on youtube\n\n'
        hm = hm + extensions + 'stop: stops playing audio and clears the queue\n'
        hm = hm + extensions + 'skip: skips the current track in queue\n'
        hm = hm + extensions + 'showqueue: shows the songs that are currently in queue\n\n'
        hm = hm + '***Slash Commands***\n'
        hm = hm + '/ping: Displays the bot\'s ping\n\n'
        hm = hm + 'All of these commands are case insensitive\n'
        hm = hm + '```'
        await ctx.send(hm)

def setup(client):
    client.add_cog(General(client))