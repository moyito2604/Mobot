# cogs.Listeners holds all the listeners needed for Mobot
import nextcord
import Dependencies.Functions as Functions
from Dependencies.Functions import Color
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
        if voice == None:
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
            settings.titles.pop(member.guild.id, None)
            settings.channels.pop(member.guild.id, None)
            settings.current.pop(member.guild.id, None)
            settings.env_vars.pop(member.guild.id, None)
            print('Successfully left the voice Channel')


def setup(client):
    client.add_cog(Listeners(client))
