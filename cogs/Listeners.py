# cogs.Listeners holds all the listeners needed for Mobot
import nextcord
import Dependencies.Functions as Functions
from Dependencies.Functions import Color
from Dependencies.SQLFunc import guildSave, checkConn, blocklistcheck
from Dependencies.Error import ReconnectError
from mysql.connector import Error
import settings
import shutil
from nextcord.ext import commands
from nextcord.errors import Forbidden
import os


# The cogs.Listeners class defines what the nextcord default listeners will do in certain situations
class Listeners(commands.Cog):

    def __init__(self, client):
        print('Listeners Initialized Successfully')
        self.client = client

    # on_voice_state_update is a nextcord function that detects if there was a change in a voice channel
    # This then checks if all users left the voice chat a removes the bot if there is no one else besides Mobot
    # It then also clears all the global dictionaries from the keys that allowed for Music in a specific server
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice = member.guild.voice_client
        if voice is None:
            return
        if len(voice.channel.members) == 1:
            textchannel = nextcord.utils.get(settings.channels[member.guild.id].guild.channels,
                                             id=settings.channels[member.guild.id].channel.id)
            try:
                await textchannel.send(f"All users have left the voice channel, {self.client.user.name} will now "
                                       f"leave the voice chat")
                print(
                    f"Successfully left the {Color.PURPLE}{Color.BOLD}{str(textchannel.name)}{Color.END} voice "
                    f"channel in the server {Color.BLUE}{Color.BOLD}{textchannel.guild.name}{Color.END}")
            except Forbidden:
                print(
                    f"Could not access channel, Successfully left the {Color.PURPLE}{Color.BOLD}{str(textchannel.name)}"
                    f"{Color.END} voice channel in the server "
                    f"{Color.BLUE}{Color.BOLD}{textchannel.guild.name}{Color.END}")
            await voice.disconnect()
            currdir = settings.pwd + '/Dependencies/'
            if os.path.isdir(currdir + '/' + str(member.guild.id)):
                shutil.rmtree(currdir + '/' + str(member.guild.id))
            print('directory ' + str(member.guild.id) + ' has been deleted')
            await Functions.stopTimer(member.guild.id)
            settings.queues.pop(member.guild.id, None)
            settings.channels.pop(member.guild.id, None)
            settings.current.pop(member.guild.id, None)
            settings.env_vars.pop(member.guild.id, None)
            print('Successfully left the voice Channel')

    # The nextcord on_ready function is used to prepare several things in the discord bot It generates Guild.txt which
    # contains the information of the servers the bot is in It also sets the presence of the bot to playing the help
    # command and notifies the user of when the bot has logged in and is ready to deploy to servers
    @commands.Cog.listener()
    async def on_ready(self):
        game = '/help'
        activity = nextcord.Game(name=game, type=3)
        if not os.path.isdir('logs'):
            os.mkdir('logs')

        # Checks if there is an SQL connection still active
        try:
            await checkConn()
            try:
                cursor = settings.connection.cursor(dictionary=True, buffered=True)
                cursor.execute(f"""CREATE TABLE Admin_Roles (
                        Guild_id varchar(50) NOT NULL,
                        Role varchar(50) NOT NULL)""")
                settings.connection.commit()
                cursor.close()
            except Error:
                pass
            try:
                cursor = settings.connection.cursor(dictionary=True, buffered=True)
                cursor.execute(f"""CREATE TABLE Blocklist (
                        Guild_id varchar(50) NOT NULL)""")
                settings.connection.commit()
                cursor.close()
            except Error:
                pass
            await guildSave()
        except ReconnectError:
            pass

        # Grabs the architecture the container is being run on
        arch = os.environ.get("ARCH", None)
        version = os.environ.get("VERSION", None)
        await self.client.change_presence(status=nextcord.Status.online, activity=activity)
        if arch and version:
            print(f"We have logged in as {self.client.user} on {arch} (Version {version})\n")
        elif arch and not version:
            print(f"We have logged in as {self.client.user} on {arch}\n")
        elif not arch and version:
            print(f"We have logged in as {self.client.user} (Version {version})\n")
        else:
            print(f"We have logged in as {self.client.user}\n")

        # The on_guild_join nextcord function is called when someone joins the server
        # This then regenerates the Guild.txt file with refreshed information on the servers stats
        @commands.Cog.listener()
        async def on_guild_join(guild):
            print(f"The bot has joined the Guild \"{guild.name}\"")
            await blocklistcheck(guild)
            await guildSave()

        # The on_guild_remove nextcord function is called when someone leaves the server
        # This then regenerates the Guild.txt file with refreshed info on the servers stats
        @commands.Cog.listener()
        async def on_guild_remove(guild):
            print(f"The bot has left the Guild \"{guild.name}\"")
            await guildSave()

        # The on_guild_update function runs when something regarding the server as a whole is changed.
        # Guild.txt is once again regenerated after this.
        @commands.Cog.listener()
        async def on_guild_update(before, after):
            print(f"Guild \"{before.name}\" has changed the name to \"{after.name}\"")
            await guildSave()


def setup(client):
    client.add_cog(Listeners(client))
