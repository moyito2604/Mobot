# cogs.Listeners holds all the listeners needed for Mobot
import nextcord
import settings
import shutil
import os
from nextcord.ext import commands


# The cogs.Listeners class defines what the nextcord default listeners will do in certain situations
class Listeners(commands.Cog):

    def __init__(self, client):
        print('Listeners Initialized Successfully')
        self.client = client

    # on_voice_state_update is a nextcord function that detects if there was a change in a voice channel
    # This then checks if all users left the voice chat an removes the bot if there is no one else besides Mobot
    # It then also clears all the global dictionaries from the keys that allowed for Music in a specific server
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice = member.guild.voice_client
        if voice == None:
            return
        if len(voice.channel.members) == 1:
            textchannel = nextcord.utils.get(settings.channels[member.guild.id].guild.channels,
                                             id=settings.channels[member.guild.id].channel.id)
            await textchannel.send('All users have left the voice channel, Mobot will now leave the voice chat')
            await voice.disconnect()
            pwd = os.path.dirname(os.path.realpath(__file__)) + '/Dependencies'
            shutil.rmtree(pwd + '/' + str(member.guild.id))
            print('directory ' + str(member.guild.id) + ' has been deleted')
            await settings.timers[member.guild.id].stop()
            settings.timers.pop(member.guild.id)
            settings.queues.pop(member.guild.id)
            settings.titles.pop(member.guild.id)
            settings.channels.pop(member.guild.id)
            settings.current.pop(member.guild.id)
            print('Successfully left the voice Channel')


def setup(client):
    client.add_cog(Listeners(client))
