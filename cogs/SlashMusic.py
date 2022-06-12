from code import interact
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
import settings
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
                settings.queues[interaction.guild.id] = []
                settings.titles[interaction.guild.id] = []
                settings.downloading[interaction.guild.id] = [False, False]
                settings.searches[interaction.guild.id] = ['', '']
                channel = interaction.user.voice.channel
                voice = await channel.connect()
                await interaction.send('Successfully Joined the ' + str(channel) + ' voice channel')
                print('Successfully Joined the ' + str(channel) + ' voice channel')
                settings.timers[interaction.guild.id] = Threaded_timer.RepeatedTimer(1, Music.queue, interaction, self.client)
                settings.timers[interaction.guild.id].stop()
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
        settings.timers[interaction.guild.id].stop()
        settings.timers.pop(interaction.guild.id)
        settings.queues.pop(interaction.guild.id)
        settings.searches.pop(interaction.guild.id)
        settings.titles.pop(interaction.guild.id)
        print('Successfully left the voice Channel')

    @nextcord.slash_command(name = "play", description = "Allows the bot to play music from a youtube link or search")
    async def play(self, interaction : Interaction, url:str):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if (interaction.user.voice):
            if voice == None:
                pwd = os.path.dirname(os.path.realpath(__file__))
                if os.path.isdir(pwd + '/' + str(interaction.guild.id)):
                    shutil.rmtree(pwd + '/' + str(interaction.guild.id))
                    print('directory ' + str(interaction.guild.id) + ' has been deleted')
                os.mkdir(pwd+ '/' + str(interaction.guild.id))
                print('directory ' + str(interaction.guild.id) + ' has been created')
                settings.queues[interaction.guild.id] = []
                settings.titles[interaction.guild.id] = []
                settings.downloading[interaction.guild.id] = [False, False]
                settings.searches[interaction.guild.id] = ['', '']
                channel = interaction.user.voice.channel
                voice = await channel.connect()
                await interaction.send('Successfully Joined the ' + str(channel) + ' voice channel')
                print('Successfully Joined the ' + str(channel) + ' voice channel')
                settings.timers[interaction.guild.id] = Threaded_timer.RepeatedTimer(1, Music.queue, interaction, self.client)
                settings.timers[interaction.guild.id].stop()
        if voice != None:
            if 'https://www.youtube.com' in url or 'https://youtu.be' in url or 'https://youtube.com' in url:
                settings.queues[interaction.guild.id].append(url)
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False, process=False)
                    title = info.get('title', None)
                    settings.titles[interaction.guild.id].append(title)
                if voice.is_playing() or voice.is_paused() or settings.downloading[interaction.guild.id][0] == True:
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
                if settings.downloading[interaction.guild.id][0] == False:
                    settings.timers[interaction.guild.id].start()
            elif url == '1' or url == '2' or url == '3' or url == '4' or url == '5':
                if settings.searches[interaction.guild.id][0] == '':
                    await interaction.send('There is currently no searched music, please search for a song and try again.')
                else:
                    print('successfully chose a song')
                    if voice.is_playing() or voice.is_paused() or settings.downloading[interaction.guild.id][0] == True:
                        msgs = 'Song number ' + url + ' selected:\n***' + settings.searches[interaction.guild.id][0]['result'][int(url)-1]['title']+'*** has been added to the queue'
                        await interaction.send(msgs, ephemeral=True)
                    else:
                        msgs = 'Song number ' + url + ' selected:\nNow Playing:\n***' + settings.searches[interaction.guild.id][0]['result'][int(url)-1]['title']+'***'
                        await interaction.send(msgs, ephemeral=True)
                    settings.queues[interaction.guild.id].append(settings.searches[interaction.guild.id][0]['result'][int(url)-1]['link'])
                    settings.titles[interaction.guild.id].append(settings.searches[interaction.guild.id][0]['result'][int(url)-1]['title'])
                    settings.searches[interaction.guild.id][0] = ''
                    settings.searches[interaction.guild.id][1] = ''
                    if settings.downloading[interaction.guild.id][0] == False:
                        settings.timers[interaction.guild.id].start()
            else:
                vidsearch = VideosSearch(url, limit = 5)
                settings.searches[interaction.guild.id][0] = vidsearch.result()
                msg = await interaction.send('Please select a song from the following results:\nSyntax:\n' + extensions + 'play 3\n' + '1: ***' + settings.searches[interaction.guild.id][0]['result'][0]['title']+'***\n'
                '2: ***' + settings.searches[interaction.guild.id][0]['result'][1]['title']+'***\n'+
                '3: ***' + settings.searches[interaction.guild.id][0]['result'][2]['title']+'***\n'+
                '4: ***' + settings.searches[interaction.guild.id][0]['result'][3]['title']+'***\n'+
                '5: ***' + settings.searches[interaction.guild.id][0]['result'][4]['title']+'***\n')
                settings.searches[interaction.guild.id][1] = msg
        else:
            await interaction.send("You are not in a voice channel, you must be in a voice channel for me to join")

    @nextcord.slash_command(name="unpause", description="allows the user to unpause any music currently paused")
    async def unpause(self, interaction : Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice == None:
            await interaction.send("I am not in a voice channel")
        else:
            if voice.is_paused():
                voice.resume()
                await interaction.send("Music is playing")
            else:
                await interaction.send("There is no paused audio in the voice channel.")


    @nextcord.slash_command(name = "pause", description = "pauses any music currently playing in the voice channel")
    async def pause(self, interaction : Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice == None:
            await interaction.send("I am not in a voice channel")
        else:
            if voice.is_playing():
                voice.pause()
                await interaction.send("Music has been paused")
            else:
                await interaction.send("There is no audio playing in the voice channel.")

    @nextcord.slash_command(name = "stop", description = "stops the music in a voice channel and clears the queue")
    async def stop(self, interaction : Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice == None:
            await interaction.send("I am not in a voice channel")
        else:
            if voice.is_playing() or voice.is_paused():
                settings.queues[interaction.guild.id] = []
                settings.titles[interaction.guild.id] = []
                voice.stop()
                await interaction.send("Music has been stopped and queue has been cleared")
                print("Music has been stopped and queue has been cleared")
                os.system('rm ' + str(interaction.guild.id) + '/*.opus')
                os.system('rm ' + str(interaction.guild.id) + '/*.webm')
                settings.timers[interaction.guild.id].stop()
            else:
                await interaction.send("There is no audio to stop.")

    @nextcord.slash_command(name = "skip", description = "skips the current song")
    async def skip(self, interaction : Interaction):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice == None:
            await interaction.send("I am not in a voice channel")
        else:  
            if voice.is_playing() or voice.is_paused():
                voice.stop()
                await interaction.send("Song has been skipped")
                print("\nSong has been skipped\n")
                if settings.queues[interaction.guild.id]:
                    if "youtube" in settings.queues[interaction.guild.id][0]:
                        title = settings.titles[interaction.guild.id][0]
                        if "playlist" in settings.queues[interaction.guild.id][0]:
                            await interaction.send('Now playing playlist:\n***' + title + '***')
                            await interaction.send('Please enjoy this music while the playlist is being retrieved.')
                        else:
                            await interaction.send('Now playing:\n***' + title + '***')
                    elif "song" in settings.queues[interaction.guild.id][0]:
                        await interaction.send('Now playing the next item in your playlist')
                else:
                    await interaction.send("Your queue is empty")
            else:
                await interaction.send("There is no music to skip.")

    @nextcord.slash_command(name = "showqueue", description = "allows the user to view the current queue")
    async def showqueue(self, interaction : Interaction):
        queued = ''
        counter = 0
        if interaction.guild.id in settings.titles:
            for title in settings.titles[interaction.guild.id]:
                queued = queued + str(counter+1) + ': ***' + settings.titles[interaction.guild.id][counter] + '***\n'
                counter = counter + 1
            if queued == '':
                await interaction.send('There are no songs currently on queue')
            else:
                await interaction.send('Songs currently on queue:\n' + queued)
        else:
            await interaction.send('There is no active queue for this server')
    
    @nextcord.slash_command(name = "repeat", description = "allows user to repeat the queue")
    async def repeat(self, interaction: Interaction):
        if interaction.guild.id in settings.downloading:
            if settings.downloading[interaction.guild.id][1]:
                settings.downloading[interaction.guild.id][1] = False
                await interaction.send('Repeating has been turned off')
            else:
                settings.downloading[interaction.guild.id][1] = True
                await interaction.send('Repeating has been turned on')
        else:
            await interaction.send('I am not in a voice channel')

    @nextcord.slash_command(name = "remove", description = "allows a user to remove one item from queue")
    async def remove(self, interaction: Interaction, song:int):
        if interaction.guild.id in settings.queues:
            if song <= len(settings.queues[interaction.guild.id]) and song > 0:
                await interaction.send(f"***{settings.titles[interaction.guild.id][song-1]}***\nhas been removed from the queue")
                settings.queues[interaction.guild.id].pop(song-1)
                settings.titles[interaction.guild.id].pop(song-1)
            else:
                await interaction.send("Invalid choice of song removal")
        else:
            await interaction.send('There is no active queue')

    @nextcord.slash_command(name = "save", description = "saves the current settings and queue to use later")
    async def save(self, interaction: Interaction):
        if interaction.guild.id in settings.queues:
            settings.saveq[interaction.guild.id] = settings.queues[interaction.guild.id]
            settings.saved[interaction.guild.id] = settings.downloading[interaction.guild.id]
            settings.saved[interaction.guild.id][0] = False
            settings.savet[interaction.guild.id] = settings.titles[interaction.guild.id]
            msg = f"{len(settings.savet[interaction.guild.id])} songs have been saved\n"
            if settings.saved[interaction.guild.id][1] == True:
                msg = msg + "Repeating was left on"
            else:
                msg = msg + "Repeating was left off"
            await interaction.send(msg)
            print(settings.saveq)
        else:
            await interaction.send('I am not in a voice channel')

    @nextcord.slash_command(name = "load", description = "loads previously saved settings")
    async def load(self, interaction: Interaction):
        print(settings.saveq)        
        if interaction.guild.id in settings.saveq:
            voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
            voice.stop()
            settings.queues[interaction.guild.id] = settings.saveq[interaction.guild.id]
            settings.downloading[interaction.guild.id] = settings.saved[interaction.guild.id]
            settings.titles[interaction.guild.id] = settings.savet[interaction.guild.id]
            msg = f"{len(settings.titles[interaction.guild.id])} songs have been recovered\n"
            if settings.downloading[interaction.guild.id][1] == True:
                msg = msg + "Repeating is on"
            else:
                msg = msg + "Repeating is off"
            await interaction.send(msg)
            settings.timers[interaction.guild.id].start()
        else:
            await interaction.send('I am not in a voice channel')

def setup(client):
    client.add_cog(SlashMusic(client))
