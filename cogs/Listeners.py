import nextcord
import settings
import shutil
import os
from nextcord.ext import commands

class Listeners(commands.Cog):

    def __init__(self, client):
        print('Listeners Initialized Successfully')
        self.client = client

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice = member.guild.voice_client
        if voice == None:
            return
        if len(voice.channel.members) == 1:
            await voice.disconnect()
            pwd = os.path.dirname(os.path.realpath(__file__))
            shutil.rmtree(pwd + '/' + str(member.guild.id))
            print('directory ' + str(member.guild.id) + ' has been deleted')
            await settings.timers[member.guild.id].stop()
            settings.timers.pop(member.guild.id)
            settings.queues.pop(member.guild.id)
            settings.searches.pop(member.guild.id)
            settings.titles.pop(member.guild.id)
            print('Successfully left the voice Channel')

def setup(client):
    client.add_cog(Listeners(client))