import os
from nextcord import SlashOption
import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from youtubesearchpython import VideosSearch
from youtubesearchpython import PlaylistsSearch
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
                settings.downloading[interaction.guild.id] = [False, False, False]
                settings.searches[interaction.guild.id] = ['', '']
                settings.indexes[interaction.guild.id] = False
                channel = interaction.user.voice.channel
                voice = await channel.connect()
                await interaction.send('Successfully Joined the ' + str(channel) + ' voice channel')
                print('Successfully Joined the ' + str(channel) + ' voice channel')
                settings.timers[interaction.guild.id] = Threaded_timer.RepeatedTimer(1, Music.queue, interaction, self.client)
                settings.channels[interaction.guild.id] = interaction
                if os.path.exists(f'logs/{interaction.guild.id}_logs.log'):
                    os.remove(f'logs/{interaction.guild.id}_logs.log')
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
        await settings.timers[interaction.guild.id].stop()
        settings.timers.pop(interaction.guild.id)
        settings.queues.pop(interaction.guild.id)
        settings.searches.pop(interaction.guild.id)
        settings.titles.pop(interaction.guild.id)
        settings.channels.pop(interaction.guild.id)
        print('Successfully left the voice Channel')

    @nextcord.slash_command(name = "play", description = "Allows the bot to play music from a youtube link or search")
    async def play(self, interaction : Interaction, url:str=' '):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if url != ' ':
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
                    settings.downloading[interaction.guild.id] = [False, False, False]
                    settings.searches[interaction.guild.id] = ['', '']
                    settings.indexes[interaction.guild.id] = False
                    channel = interaction.user.voice.channel
                    voice = await channel.connect()
                    await interaction.send('Successfully Joined the ' + str(channel) + ' voice channel')
                    print('Successfully Joined the ' + str(channel) + ' voice channel')
                    settings.timers[interaction.guild.id] = Threaded_timer.RepeatedTimer(1, Music.queue, interaction, self.client)
                    settings.channels[interaction.guild.id] = interaction
                    if os.path.exists(f'logs/{interaction.guild.id}_logs.log'):
                        os.remove(f'logs/{interaction.guild.id}_logs.log')
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
                        else:
                            await interaction.send('Now playing:\n***' + title + '***')
                    if settings.downloading[interaction.guild.id][0] == False:
                        await settings.timers[interaction.guild.id].start()
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
                            await settings.timers[interaction.guild.id].start()
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
        else:
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
                await settings.timers[interaction.guild.id].pause()
            else:
                await interaction.send("There is no audio to stop.")

    @nextcord.slash_command(name = "skip", description = "skips the current song")
    async def skip(self, interaction : Interaction, amount:int=1):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice == None:
            await interaction.send("I am not in a voice channel")
        else:
            if voice.is_playing() or voice.is_paused() and (amount <= len(settings.queues[interaction.guild.id]) and amount > 0):
                await interaction.send(f"{amount} songs have been skipped")
                print("\nSong has been skipped\n")
                for counter in range(1, amount):
                    if settings.downloading[interaction.guild.id][1]:
                        settings.queues[interaction.guild.id].append(settings.queues[interaction.guild.id][0])
                        settings.titles[interaction.guild.id].append(settings.titles[interaction.guild.id][0])
                    settings.queues[interaction.guild.id].pop(0)
                    settings.titles[interaction.guild.id].pop(0)
                if settings.queues[interaction.guild.id]:
                    settings.indexes[interaction.guild.id] = True
                    if "youtube" in settings.queues[interaction.guild.id][0]:
                        title = settings.titles[interaction.guild.id][0]
                        if "playlist" in settings.queues[interaction.guild.id][0]:
                            await interaction.send('Now playing playlist:\n***' + title + '***')
                        else:
                            await interaction.send('Now playing:\n***' + title + '***')
                    elif "song" in settings.queues[interaction.guild.id][0]:
                        await interaction.send('Now playing the next item in your playlist')
                else:
                    await interaction.send("Your queue is empty")
                voice.stop()
            elif amount > len(settings.queues[interaction.guild.id]) and amount <= 0:
                await interaction.send("Please input a valid amount of songs to skip")
            else:
                await interaction.send("There is no music to skip.")

    @nextcord.slash_command(name = "song", description = "allows the user to search for a song and add it to the queue")
    async def song(self, interaction: Interaction, song: str):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice != None:
            vidsearch = VideosSearch(song, limit = 1)
            settings.searches[interaction.guild.id][0] = vidsearch.result()
            if voice.is_playing() or voice.is_paused() or settings.downloading[interaction.guild.id][0] == True:
                await interaction.response.send_message('***' + settings.searches[interaction.guild.id][0]['result'][0]['title']+'\n*** has been added to the queue')
            else:
                await interaction.response.send_message('Song Selected')            
            settings.queues[interaction.guild.id].append(settings.searches[interaction.guild.id][0]['result'][0]['link'])
            settings.titles[interaction.guild.id].append(settings.searches[interaction.guild.id][0]['result'][0]['title'])
            settings.searches[interaction.guild.id][0] = ''
            if settings.downloading[interaction.guild.id][0] == False:
                await settings.timers[interaction.guild.id].start()
        else:
            await interaction.response.send_message('I am not in a voice channel')

    @nextcord.slash_command(name = "playlist", description = "allows a user to search for and select a playlist and add it to the queue")
    async def playlist(self, interaction : Interaction, playlist: str):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice != None:
            if playlist == '1' or playlist == '2' or playlist == '3' or playlist == '4' or playlist == '5':
                if settings.searches[interaction.guild.id][0] == '':
                    await interaction.send('There is currently no searched music, please search for a playlist and try again.')
                else:
                    print('successfully chose a playlist')
                    if voice.is_playing() or voice.is_paused() or settings.downloading[interaction.guild.id][0] == True:
                        if settings.searches[interaction.guild.id][1] == None:
                            await interaction.send('Playlist number ' + playlist + ' selected:\n***' + settings.searches[interaction.guild.id][0]['result'][int(playlist)-1]['title']+'*** has been added to the queue')
                        else:
                            await settings.searches[interaction.guild.id][1].edit('Playlist number ' + playlist + ' selected:\n***' + settings.searches[interaction.guild.id][0]['result'][int(playlist)-1]['title']+'*** has been added to the queue')
                    else:
                        if settings.searches[interaction.guild.id][1] == None:
                            await interaction.send('Playlist number ' + playlist + ' selected:\nNow Playing:\n***' + settings.searches[interaction.guild.id][0]['result'][int(playlist)-1]['title']+'***')
                        else:
                            await settings.searches[interaction.guild.id][1].edit('Playlist number ' + playlist + ' selected:\nNow Playing:\n***' + settings.searches[interaction.guild.id][0]['result'][int(playlist)-1]['title']+'***')
                    settings.queues[interaction.guild.id].append(settings.searches[interaction.guild.id][0]['result'][int(playlist)-1]['link'])
                    settings.titles[interaction.guild.id].append(settings.searches[interaction.guild.id][0]['result'][int(playlist)-1]['title'])
                    settings.searches[interaction.guild.id][0] = ''
                    settings.searches[interaction.guild.id][1] = ''
                    if settings.downloading[interaction.guild.id][0] == False:
                        await settings.timers[interaction.guild.id].start()
            else:
                vidsearch = PlaylistsSearch(playlist, limit = 5)
                settings.searches[interaction.guild.id][0] = vidsearch.result()
                msg = await interaction.send('Please select a playlist from the following results:\nSyntax:\n' + extensions + 'play 3\n1: ***' + settings.searches[interaction.guild.id][0]['result'][0]['title'] + 
                '*** \tSize: ' + settings.searches[interaction.guild.id][0]['result'][0]['videoCount'] + '\n'+
                f'2: ***' + settings.searches[interaction.guild.id][0]['result'][1]['title'] + '*** \tSize:' + settings.searches[interaction.guild.id][0]['result'][1]['videoCount'] + '\n'+
                f'3: ***' + settings.searches[interaction.guild.id][0]['result'][2]['title'] + '*** \tSize:' + settings.searches[interaction.guild.id][0]['result'][2]['videoCount'] + '\n'+
                f'4: ***' + settings.searches[interaction.guild.id][0]['result'][3]['title'] + '*** \tSize:' + settings.searches[interaction.guild.id][0]['result'][3]['videoCount'] + '\n'+
                f'5: ***' + settings.searches[interaction.guild.id][0]['result'][4]['title'] + '*** \tSize:' + settings.searches[interaction.guild.id][0]['result'][4]['videoCount'] + '\n')
                settings.searches[interaction.guild.id][1] = msg
        else:
            await interaction.send('I am not in a voice channel')
    
    @nextcord.slash_command(name = "qplaylist", description = "allows the user to search and add a playlist to the queue quickly")
    async def qplaylist(self, interaction : Interaction, playlist: str):
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice != None:
            vidsearch = PlaylistsSearch(playlist, limit = 1)
            settings.searches[interaction.guild.id][0] = vidsearch.result()
            if voice.is_playing() or voice.is_paused() or settings.downloading[interaction.guild.id][0] == True:
                await interaction.response.send_message('***' + settings.searches[interaction.guild.id][0]['result'][0]['title']+'\n*** has been added to the queue')
            else:
                await interaction.response.send_message('Now Playing Playlist:\n***' + settings.searches[interaction.guild.id][0]['result'][0]['title']+'*** \nSize: '+ settings.searches[interaction.guild.id][0]['result'][0]['videoCount'])            
            settings.queues[interaction.guild.id].append(settings.searches[interaction.guild.id][0]['result'][0]['link'])
            settings.titles[interaction.guild.id].append(settings.searches[interaction.guild.id][0]['result'][0]['title'])
            settings.searches[interaction.guild.id][0] = ''
            if settings.downloading[interaction.guild.id][0] == False:
                await settings.timers[interaction.guild.id].start()
        else:
            await interaction.response.send_message('I am not in a voice channel')

    @nextcord.slash_command(name = "showqueue", description = "allows the user to view the current queue")
    async def showqueue(self, interaction: Interaction, msg = SlashOption(name="printing",
    description="Allows the user to send to either print queue to DM or channel", 
    choices={"DM":"dm", "Channel":"channel"})):
        queued = ''
        counter = 0
        if interaction.guild.id in settings.titles:
            for title in settings.titles[interaction.guild.id]:
                queued = queued + str(counter+1) + ': ***' + title + '***\n'
                counter+=1
            if queued == '':
                await interaction.send('There are no songs currently on queue')
            else:
                if len(queued) > 1970:
                    await interaction.send('The queue is currently too long to print')
                    queued = ''
                    if msg.lower() == 'dm':
                        await interaction.send('The queue has been sent to DM')
                        queued = '***Queue***\n\n\n\nSongs currently on queue:\n'
                        reset = 0
                        counter = 0
                        for title in settings.titles[interaction.guild.id]:
                            if reset == 20:
                                reset = 0
                                await interaction.user.send(queued)
                                queued = ''
                            queued = queued + str(counter+1) + ': ***' + title + '***\n'
                            reset += 1
                            counter += 1
                        if queued != '':
                            await interaction.user.send(queued)
                    else:    
                        for counter in range(0, 10):
                            queued = queued + str(counter+1) + ': ***' + settings.titles[interaction.guild.id][counter] + '***\n'
                        await interaction.send('The next 10 songs in queue will be printed instead:\n' + queued)
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

    @nextcord.slash_command(name = "shuffle", description = "allows user to shuffle the queue")
    async def shuffle(self, interaction: Interaction):
        if interaction.guild.id in settings.downloading:
            if settings.downloading[interaction.guild.id][2]:
                settings.downloading[interaction.guild.id][2] = False
                await interaction.send('Shuffling has been turned off')
            else:
                settings.downloading[interaction.guild.id][2] = True
                await interaction.send('Shuffling has been turned on')
        else:
            await interaction.send('I am not in a voice channel')

    @nextcord.slash_command(name = "status", description = "show the user if repeating and shuffle is turned on or off")
    async def status(self, interaction: Interaction):
        if interaction.guild.id in settings.downloading:
            if settings.downloading[interaction.guild.id][1]:
                await interaction.send('Repeating is turned on')
            else:
                await interaction.send('Repeating is turned off')
            if settings.downloading[interaction.guild.id][2]:
                await interaction.send('Shuffling is turned on')
            else:
                await interaction.send('Shuffling is turned off')
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

def setup(client):
    client.add_cog(SlashMusic(client))
