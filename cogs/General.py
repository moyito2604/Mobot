# cogs.General allows for some commands for use in for Mobot
import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import os
import time
import cogs.Dependencies.dccommands as dccommands
import config
import configgen

# Loads up tokens for later use
Token = config.Token
extensions = config.extension
seanToken = config.seanToken

# These are all strings intended to be used for the help command for Mobot
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
mc = mc + extensions + 'shuffle: Allows the user to toggle the queue to shuffle\n'
mc = mc + extensions + 'status: Shows if repeating and shuffling is turned on or off\n'
mc = mc + extensions + 'remove: Allows the user to remove a single item from queue\n'
mc = mc + extensions + 'save: Allows a user to save a queue\n'
mc = mc + extensions + 'load: Allows a user to load a the saved queue\n'
mc = mc + extensions + 'song: Searches and adds a song to the queue without selection\n'
mc = mc + extensions + 'playlist: Searches for playlists and allows the user to select a playlist to add to the queue\n'
mc = mc + extensions + 'qplaylist: Searches and adds a playlist to the queue without selection\n\n'
sl = '/ping: Displays the bot\'s ping\n'
sl = sl + '***All of the Music commands have slash versions as well***'

# It also generates the nextcord embed for the help command as well
helpembed = nextcord.Embed(title="List of Commands you can use", description=cm)
helpembed.add_field(name="Music Bot Commands", value=mc, inline=False)
helpembed.add_field(name="Slash Commands", value=sl, inline=False)


# This class defines what the cogs.General will be able to do
class General(commands.Cog):

    def __init__(self, client):
        print("General Initialized Successfully")
        self.client = client

    # Ping test defines the ping command which allows a user to view the latency of the connection to Mobot
    @nextcord.slash_command(name="ping", description="Check bots ping!")
    async def pingtest(self, interaction: Interaction):
        embed = nextcord.Embed(title=(f"My ping is {round(self.client.latency * 1000)}ms"))
        await interaction.response.send_message(embed=embed)

    # Allows the user to change the global default extension to Mobot
    # Mostly useless now this is hidden from the help menu and breaks the bot whenever it is use.
    # DO NOT USE THIS COMMAND
    @commands.command(pass_context=True)
    async def ce(self, ctx, extension):
        await ctx.send('The extension has been changed to ' + extension)
        configgen.generateConfiguration(extension, False, Token, seanToken)
        config.extension = extension
        print('Command extension changed to ' + config.extension + ' successfully')
        game = config.extension + 'help'
        activity = nextcord.Game(name=game, type=3)
        await self.client.change_presence(status=nextcord.Status.online, activity=activity)
        os.system('python3 main.py')

    # Simple self-explanatory command
    @commands.command(pass_context=True)
    async def deez(self, ctx):
        await ctx.send('Nutz')
        time.sleep(1)
        await ctx.send('GOTTEM!')
        print("Response to deez printed")

    # This generates a techquote from a small database of techquotes under Dependencies/Quotes/Funnytechquotes.txt
    # Compiled quotes are from a variety of sources, most of them coming from Linus Torvalds
    @commands.command(pass_context=True)
    async def tquote(self, ctx):
        await ctx.send(dccommands.techQuotes())
        print("Response to tquote printed")

    # ding command responds with dong
    # also pretty self-explanatory
    @commands.command(pass_context=True)
    async def ding(self, ctx):
        await ctx.send('dong')
        print("Response to ding printed")

    # the helps function prints the help command using a message command
    # It utilizes the nextcord embed generated earlier
    @commands.command(name="help", pass_context=True)
    async def helps(self, ctx):
        await ctx.send(embed=helpembed)

    # The help function prints the help command using a slash command instead of a message command
    # Also utilizes the nextcord embed generated earlier
    @nextcord.slash_command(name="help", description="Prints out helpful commands and options!")
    async def help(self, interaction: Interaction):
        await interaction.send(embed=helpembed)


def setup(client):
    client.add_cog(General(client))
