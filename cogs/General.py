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

cm = extensions + 'ding: replies with dong\n'
cm = cm + extensions + 'deez: replies with nutz\n'
cm = cm + extensions + 'tquote: Generates a tech quote\n'
cm = cm + 'All commands with an extension are case insensitive\n'
mc = extensions + 'join: joins voice channel\n'
mc = mc + extensions + 'leave: leaves voice channel\n'
mc = mc + extensions + 'play: plays music with a youtube link, queues music, and plays music currently paused\n'
mc = mc + '***This command also allows you to search for a song on youtube***\n\n'
mc = mc + extensions + 'stop: stops playing audio and clears the queue\n'
mc = mc + extensions + 'skip: skips the current track in queue\n'
mc = mc + extensions + 'showqueue: shows the songs that are currently in queue\n'
mc = mc + extensions + 'repeat: Allows you to toggle the queue repeat\n'
mc = mc + extensions + 'remove: Allows the user to remove a single item from queue\n\n'
sl = '/ping: Displays the bot\'s ping\n'
sl = sl + '/unpause: plays any paused music in the bot\n'
sl = sl + '***All of the Music commands have slash versions as well***'
helpembed = nextcord.Embed(title="List of Commands you can use", description=cm)
helpembed.add_field(name="Music Bot Commands", value=mc, inline=False)
helpembed.add_field(name="Slash Commands", value=sl, inline = False)

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

    @commands.command(name = "help", pass_context = True)
    async def helps(self, ctx):
        await ctx.send(embed=helpembed)

    @nextcord.slash_command(name = "help", description="Prints out helpful commands and options!")
    async def help(self, interaction : Interaction):
        await interaction.send(embed=helpembed)

def setup(client):
    client.add_cog(General(client))