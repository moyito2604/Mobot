import os
import nextcord
from nextcord.ext import commands
from nextcord import FFmpegPCMAudio
from nextcord import Interaction
from youtubesearchpython import VideosSearch
import sys
import os.path
import yt_dlp
import shutil
import config
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))
import Music
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)) + '/Dependencies/')
import Threaded_timer
import dccommands

extensions = config.extension
ydl_opts = {
'format': 'bestaudio/best',
'postprocessors': [{
    'key':'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '192',
}]
}

class SlashMusic(commands.Cog):

    def __init__(self, client):
        print("SlashMusic Initialized Successfully")
        self.client = client

    @nextcord.slash_command(name = "join", description = "Joins the Bot to a Voice Channel")
    async def join(self, interaction : Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if (interaction.user.voice):
            if voice == None:
                pwd = os.path.dirname(os.path.realpath(__file__))
                if os.path.isdir(pwd + '/' + str(interaction.guild.id)):
                    shutil.rmtree(pwd + '/' + str(interaction.guild.id))
                    print('directory ' + str(interaction.guild.id) + ' has been deleted')
                os.mkdir(pwd+ '/' + str(interaction.guild.id))
                print('directory ' + str(interaction.guild.id) + ' has been created')
                Music.queues[interaction.guild.id] = []
                Music.titles[interaction.guild.id] = []
                Music.downloading[interaction.guild.id] = False
                Music.searches[interaction.guild.id] = ''
                channel = interaction.user.voice.channel
                voice = await channel.connect()
                await interaction.send('Successfully Joined the ' + str(channel) + ' voice channel')
                print('Successfully Joined the ' + str(channel) + ' voice channel')
                Music.timers[interaction.guild.id] = Threaded_timer.RepeatedTimer(1, Music.queue, interaction, self.client)
                Music.timers[interaction.guild.id].stop()
            else:
                await interaction.send("I am already connected")
        else:
            print('User is not in a voice channel')
            await interaction.send("You are not in a voice channel, you must be in a voice channel for me to join")

    @nextcord.slash_command(name = "leave", description = "Leaves the bot from a voice channel")
    async def leave(self, interaction : Interaction):
        pwd = os.path.dirname(os.path.realpath(__file__))
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if (interaction.guild.voice_client):
            await voice.disconnect()
            await interaction.send("Left the voice channel")
        else:
            await interaction.send("I am not in a voice channel")
        shutil.rmtree(pwd + '/' + str(interaction.guild.id))
        print('directory ' + str(interaction.guild.id) + ' has been deleted')
        Music.timers[interaction.guild.id].stop()
        Music.timers.pop(interaction.guild.id)
        Music.queues.pop(interaction.guild.id)
        Music.searches.pop(interaction.guild.id)
        Music.titles.pop(interaction.guild.id)
        print('Successfully left the voice Channel')

    @nextcord.slash_command(name = "play", description = "Allows the bot to play music from a youtube link or search")
    async def play(self, interaction : Interaction, url:str):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        pwd = os.path.dirname(os.path.realpath(__file__))
        if (interaction.user.voice):
            print(url)
            if voice == None:
                if os.path.isdir(pwd + '/' + str(interaction.guild.id)):
                    shutil.rmtree(pwd + '/' + str(interaction.guild.id))
                    print('directory ' + str(interaction.guild.id) + ' has been deleted')
                os.mkdir(pwd+ '/' + str(interaction.guild.id))
                print('directory ' + str(interaction.guild.id) + ' has been created')
                Music.queues[interaction.guild.id] = []
                Music.titles[interaction.guild.id] = []
                Music.downloading[interaction.guild.id] = False
                Music.searches[interaction.guild.id] = ''
                channel = interaction.user.voice.channel
                voice = await channel.connect()
                await interaction.send('Successfully Joined the ' + str(channel) + ' voice channel')
                print('Successfully Joined the ' + str(channel) + ' voice channel')
                Music.timers[interaction.guild.id] = Threaded_timer.RepeatedTimer(1, Music.queue, interaction, self.client)
                Music.timers[interaction.guild.id].stop()
            if 'https://www.youtube.com' in url or 'https://youtu.be' in url:
                Music.queues[interaction.guild.id].append(url)
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False, process=False)
                    title = info.get('title', None)
                    Music.titles[interaction.guild.id].append(title)
                if voice.is_playing() or voice.is_paused() or Music.downloading[interaction.guild.id] == True:
                    if "playlist" in url:
                        await interaction.send('Playlist ***' + title + '*** has been added to the queue')
                    else:
                        await interaction.send('***' + title + '*** has been added to the queue')
                else:
                    await interaction.send('Retrieving from source')
                    if "playlist" in url:
                        await interaction.send('Now playing playlist:\n***' + title + '***')
                        await interaction.send('Please enjoy this music while the playlist is being retrieved.')
                    else:
                        await interaction.send('Now playing:\n***' + title + '***')
                if Music.downloading[interaction.guild.id] == False:
                    Music.timers[interaction.guild.id].start()
            elif url == '1' or url == '2' or url == '3' or url == '4' or url == '5':
                if Music.searches[interaction.guild.id] == '':
                    await interaction.send('There is currently no searched music, please search for a song and try again.')
                else:
                    print('successfully chose a song')
                    if voice.is_playing() or voice.is_paused() or Music.downloading[interaction.guild.id] == True:
                        await interaction.send('Song number ' + url + ' selected:\n***' + Music.searches[interaction.guild.id]['result'][int(url)-1]['title']+'*** has been added to the queue')
                    else:
                        await interaction.send('Song number ' + url + ' selected:\nNow Playing:\n***' + Music.searches[interaction.guild.id]['result'][int(url)-1]['title']+'***')
                    Music.queues[interaction.guild.id].append(Music.searches[interaction.guild.id]['result'][int(url)-1]['link'])
                    Music.titles[interaction.guild.id].append(Music.searches[interaction.guild.id]['result'][int(url)-1]['title'])
                    Music.searches[interaction.guild.id] = ''
                    if Music.downloading[interaction.guild.id] == False:
                        Music.timers[interaction.guild.id].start()
            else:
                vidsearch = VideosSearch(url, limit = 5)
                Music.searches[interaction.guild.id] = vidsearch.result()
                await interaction.send('Please select a song from the following results:\nSyntax:\n' + extensions + 'play 3\n' + '1: ***' + Music.searches[interaction.guild.id]['result'][0]['title']+'***\n'
                '2: ***' + Music.searches[interaction.guild.id]['result'][1]['title']+'***\n'+
                '3: ***' + Music.searches[interaction.guild.id]['result'][2]['title']+'***\n'+
                '4: ***' + Music.searches[interaction.guild.id]['result'][3]['title']+'***\n'+
                '5: ***' + Music.searches[interaction.guild.id]['result'][4]['title']+'***\n')
        else:
            await interaction.send("You are not in a voice channel, you must be in a voice channel for me to join")

    @nextcord.slash_command(name="unpause", description="allows the user to unpause any music currently paused")
    async def unpause(self, interaction : Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice.is_paused():
            voice.resume()
            await interaction.send("Music is playing")
        else:
            await interaction.send("There is no paused audio in the voice channel.")


    @nextcord.slash_command(name = "pause", description = "pauses any music currently playing in the voice channel")
    async def pause(self, interaction : Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice.is_playing():
            voice.pause()
            await interaction.send("Music has been paused")
        else:
            await interaction.send("There is no audio playing in the voice channel.")

    @nextcord.slash_command(name = "stop", description = "stops the music in a voice channel and clears the queue")
    async def stop(self, interaction : Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice.is_playing() or voice.is_paused():
            Music.queues[interaction.guild.id].clear()
            Music.titles[interaction.guild.id].clear()
            voice.stop()
            await interaction.send("Music has been stopped and queue has been cleared")
            print("Music has been stopped and queue has been cleared")
            os.system('rm ' + str(interaction.guild.id) + '/*.mp3')
            os.system('rm ' + str(interaction.guild.id) + '/*.webm')
            Music.timers[interaction.guild.id].stop()
        else:
            await interaction.send("There is no audio to stop.")

    @nextcord.slash_command(name = "skip", description = "skips the current song")
    async def skip(self, interaction : Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice.is_playing() or voice.is_paused():
            voice.stop()
            await interaction.send("Song has been skipped")
            print("\nSong has been skipped\n")
            if Music.queues[interaction.guild.id]:
                if "youtube" in Music.queues[interaction.guild.id][0]:
                    title = Music.titles[interaction.guild.id][0]
                    if "playlist" in Music.queues[interaction.guild.id][0]:
                        await interaction.send('Now playing playlist:\n***' + title + '***')
                        await interaction.send('Please enjoy this music while the playlist is being retrieved.')
                    else:
                        await interaction.send('Now playing:\n***' + title + '***')
                elif "song" in Music.queues[interaction.guild.id][0]:
                    await interaction.send('Now playing the next item in your playlist')
            else:
                await interaction.send("Your queue is empty")
        else:
            await interaction.send("There is no music to skip.")

    @nextcord.slash_command(name = "showqueue", description = "allows the user to view the current queue")
    async def showqueue(self, interaction : Interaction):
        queued = ''
        counter = 0
        for title in Music.titles[interaction.guild.id]:
            queued = queued + str(counter+1) + ': ***' + Music.titles[interaction.guild.id][counter] + '***\n'
            counter = counter + 1
        if queued == '':
            await interaction.send('There are no songs currently on queue')
        else:
            await interaction.send('Songs currently on queue:\n' + queued)


def setup(client):
    client.add_cog(SlashMusic(client))
