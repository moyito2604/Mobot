import os
import nextcord
from nextcord.ext import commands
from nextcord import FFmpegPCMAudio
from youtubesearchpython import VideosSearch
from youtubesearchpython import PlaylistsSearch
import sys
import os.path
import yt_dlp
import shutil
import config
import settings
import random
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

class Music(commands.Cog):

    def __init__(self, client):
        print("Music Initialized Successfully")
        self.client = client

    @commands.command(pass_context = True)
    async def join(self, ctx):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if (ctx.author.voice):
            if voice == None:
                pwd = os.path.dirname(os.path.realpath(__file__))
                if os.path.isdir(pwd + '/' + str(ctx.guild.id)):
                    shutil.rmtree(pwd + '/' + str(ctx.guild.id))
                    print('directory ' + str(ctx.guild.id) + ' has been deleted')
                os.mkdir(pwd+ '/' + str(ctx.guild.id))
                print('directory ' + str(ctx.guild.id) + ' has been created')
                settings.queues[ctx.guild.id] = []
                settings.titles[ctx.guild.id] = []
                settings.downloading[ctx.guild.id] = [False, False, False]
                settings.searches[ctx.guild.id] = ['', '']
                settings.indexes[ctx.guild.id] = False
                channel = ctx.message.author.voice.channel
                voice = await channel.connect()
                await ctx.send('Successfully Joined the ' + str(channel) + ' voice channel')
                print('Successfully Joined the ' + str(channel) + ' voice channel')
                settings.timers[ctx.guild.id] = Threaded_timer.RepeatedTimer(1, queue, ctx, self.client)
                settings.timers[ctx.guild.id].stop()
                settings.channels[ctx.guild.id] = nextcord.utils.get(ctx.guild.channels, id=ctx.channel.id)
            else:
                await ctx.send("I am already connected")
        else:
            print('User is not in a voice channel')
            await ctx.send("You are not in a voice channel, you must be in a voice channel for me to join")

    @commands.command(pass_context = True)
    async def leave(self, ctx):
        pwd = os.path.dirname(os.path.realpath(__file__))
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if (ctx.voice_client):
            await voice.disconnect()
            await ctx.send("Left the voice channel")
        else:
            await ctx.send("I am not in a voice channel")
        shutil.rmtree(pwd + '/' + str(ctx.guild.id))
        print('directory ' + str(ctx.guild.id) + ' has been deleted')
        settings.timers[ctx.guild.id].stop()
        settings.timers.pop(ctx.guild.id)
        settings.queues.pop(ctx.guild.id)
        settings.searches.pop(ctx.guild.id)
        settings.titles.pop(ctx.guild.id)
        settings.channels.pop(ctx.guild.id)
        print('Successfully left the voice Channel')

    @commands.command(pass_context = True)
    async def play(self, ctx, *, url:str):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        pwd = os.path.dirname(os.path.realpath(__file__))
        if (ctx.author.voice):
            print(url)
            if voice == None:
                if os.path.isdir(pwd + '/' + str(ctx.guild.id)):
                    shutil.rmtree(pwd + '/' + str(ctx.guild.id))
                    print('directory ' + str(ctx.guild.id) + ' has been deleted')
                os.mkdir(pwd+ '/' + str(ctx.guild.id))
                print('directory ' + str(ctx.guild.id) + ' has been created')
                settings.queues[ctx.guild.id] = []
                settings.titles[ctx.guild.id] = []
                settings.downloading[ctx.guild.id] = [False, False, False]
                settings.searches[ctx.guild.id] = ['', '']
                settings.indexes[ctx.guild.id] = False
                channel = ctx.message.author.voice.channel
                voice = await channel.connect()
                await ctx.send('Successfully Joined the ' + str(channel) + ' voice channel')
                print('Successfully Joined the ' + str(channel) + ' voice channel')
                settings.timers[ctx.guild.id] = Threaded_timer.RepeatedTimer(1, queue, ctx, self.client)
                settings.timers[ctx.guild.id].stop()
                settings.channels[ctx.guild.id] = nextcord.utils.get(ctx.guild.channels, id=ctx.channel.id)
        if voice != None:
            if 'https://www.youtube.com' in url or 'https://youtu.be' in url or 'https://youtube.com' in url:
                settings.queues[ctx.guild.id].append(url)
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False, process=False)
                    title = info.get('title', None)
                    settings.titles[ctx.guild.id].append(title)
                if voice.is_playing() or voice.is_paused() or settings.downloading[ctx.guild.id][0] == True:
                    if "playlist" in url:
                        await ctx.send('Playlist ***' + title + '*** has been added to the queue')
                    else:
                        await ctx.send('***' + title + '*** has been added to the queue')
                else:
                    await ctx.send('Retrieving from source')
                    if "playlist" in url:
                        await ctx.send('Now playing playlist:\n***' + title + '***')
                        await ctx.send('Please enjoy this music while the playlist is being retrieved.')
                    else:
                        await ctx.send('Now playing:\n***' + title + '***')
                if settings.downloading[ctx.guild.id][0] == False:
                    settings.timers[ctx.guild.id].start()
            elif url == '1' or url == '2' or url == '3' or url == '4' or url == '5':
                if settings.searches[ctx.guild.id][0] == '':
                    await ctx.send('There is currently no searched music, please search for a song and try again.')
                else:
                    print('successfully chose a song')
                    if voice.is_playing() or voice.is_paused() or settings.downloading[ctx.guild.id][0] == True:
                        if settings.searches[ctx.guild.id][1] == None:
                            await ctx.send('Song number ' + url + ' selected:\n***' + settings.searches[ctx.guild.id][0]['result'][int(url)-1]['title']+'*** has been added to the queue')
                        else:
                            await settings.searches[ctx.guild.id][1].edit('Song number ' + url + ' selected:\n***' + settings.searches[ctx.guild.id][0]['result'][int(url)-1]['title']+'*** has been added to the queue')
                    else:
                        if settings.searches[ctx.guild.id][1] == None:
                            await ctx.send('Song number ' + url + ' selected:\nNow Playing:\n***' + settings.searches[ctx.guild.id][0]['result'][int(url)-1]['title']+'***')
                        else:
                            await settings.searches[ctx.guild.id][1].edit('Song number ' + url + ' selected:\nNow Playing:\n***' + settings.searches[ctx.guild.id][0]['result'][int(url)-1]['title']+'***')
                    settings.queues[ctx.guild.id].append(settings.searches[ctx.guild.id][0]['result'][int(url)-1]['link'])
                    settings.titles[ctx.guild.id].append(settings.searches[ctx.guild.id][0]['result'][int(url)-1]['title'])
                    settings.searches[ctx.guild.id][0] = ''
                    settings.searches[ctx.guild.id][1] = ''
                    if settings.downloading[ctx.guild.id][0] == False:
                        settings.timers[ctx.guild.id].start()
            else:
                vidsearch = VideosSearch(url, limit = 5)
                settings.searches[ctx.guild.id][0] = vidsearch.result()
                msg = await ctx.send('Please select a song from the following results:\nSyntax:\n' + extensions + 'play 3\n' + '1: ***' + settings.searches[ctx.guild.id][0]['result'][0]['title']+'***\n'
                '2: ***' + settings.searches[ctx.guild.id][0]['result'][1]['title']+'***\n'+
                '3: ***' + settings.searches[ctx.guild.id][0]['result'][2]['title']+'***\n'+
                '4: ***' + settings.searches[ctx.guild.id][0]['result'][3]['title']+'***\n'+
                '5: ***' + settings.searches[ctx.guild.id][0]['result'][4]['title']+'***\n')
                settings.searches[ctx.guild.id][1] = msg
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel for me to join")

    @play.error
    async def unpause(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice == None:
                await ctx.send("I am not in a voice channel")
            else:
                if voice.is_paused():
                    voice.resume()
                    await ctx.send("Music is playing")
                else:
                    await ctx.send("There is no paused audio in the voice channel.")


    @commands.command(pass_context = True)
    async def pause(self, ctx):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send("I am not in a voice channel")
        else:
            if voice.is_playing():
                voice.pause()
                await ctx.send("Music has been paused")
            else:
                await ctx.send("There is no audio playing in the voice channel.")

    @commands.command(pass_context = True)
    async def stop(self, ctx):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send("I am not in a voice channel")
        else:
            if voice.is_playing() or voice.is_paused():
                settings.queues[ctx.guild.id] = []
                settings.titles[ctx.guild.id] = []
                voice.stop()
                await ctx.send("Music has been stopped and queue has been cleared")
                print("Music has been stopped and queue has been cleared")
                os.system('rm ' + str(ctx.guild.id) + '/*.opus')
                os.system('rm ' + str(ctx.guild.id) + '/*.webm')
                settings.timers[ctx.guild.id].stop()
            else:
                await ctx.send("There is no audio to stop.")

    @commands.command(pass_context = True)
    async def skip(self, ctx, amount:int):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send("I am not in a voice channel")
        else:
            if voice.is_playing() or voice.is_paused() and (amount <= len(settings.queues[ctx.guild.id]) and amount > 0):
                await ctx.send(f"{amount} songs have been skipped")
                print("\nSong has been skipped\n")
                for counter in range(1, amount):
                    if settings.downloading[ctx.guild.id][1]:
                        settings.queues[ctx.guild.id].append(settings.queues[ctx.guild.id][0])
                        settings.titles[ctx.guild.id].append(settings.titles[ctx.guild.id][0])
                    settings.queues[ctx.guild.id].pop(0)
                    settings.titles[ctx.guild.id].pop(0)
                if settings.queues[ctx.guild.id]:
                    settings.indexes[ctx.guild.id] = True
                    if "youtube" in settings.queues[ctx.guild.id][0]:
                        title = settings.titles[ctx.guild.id][0]
                        if "playlist" in settings.queues[ctx.guild.id][0]:
                            await ctx.send('Now playing playlist:\n***' + title + '***')
                            await ctx.send('Please enjoy this music while the playlist is being retrieved.')
                        else:
                            await ctx.send('Now playing:\n***' + title + '***')
                    elif "song" in settings.queues[ctx.guild.id][0]:
                        await ctx.send('Now playing the next item in your playlist')
                else:
                    await ctx.send("Your queue is empty")
                voice.stop()
            elif amount > len(settings.queues[ctx.guild.id]) and amount <= 0:
                await ctx.send("Please input a valid amount of songs to skip")
            else:
                await ctx.send("There is no music to skip.")
    
    @skip.error
    async def skips(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice == None:
                await ctx.send("I am not in a voice channel")
            else:
                if voice.is_playing() or voice.is_paused():
                    await ctx.send("Song has been skipped")
                    print("\nSong has been skipped\n")
                    if settings.queues[ctx.guild.id]:
                        settings.indexes[ctx.guild.id] = True
                        if "youtube" in settings.queues[ctx.guild.id][0]:
                            title = settings.titles[ctx.guild.id][0]
                            if "playlist" in settings.queues[ctx.guild.id][0]:
                                await ctx.send('Now playing playlist:\n***' + title + '***')
                                await ctx.send('Please enjoy this music while the playlist is being retrieved.')
                            else:
                                await ctx.send('Now playing:\n***' + title + '***')
                        elif "song" in settings.queues[ctx.guild.id][0]:
                            await ctx.send('Now playing the next item in your playlist')
                    else:
                        await ctx.send("Your queue is empty")
                    voice.stop()
                else:
                    await ctx.send("There is no music to skip.")

    @commands.command(pass_context = True)
    async def song(self, ctx, *, song: str):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice != None:
            vidsearch = VideosSearch(song, limit = 1)
            settings.searches[ctx.guild.id][0] = vidsearch.result()
            if voice.is_playing() or voice.is_paused() or settings.downloading[ctx.guild.id][0] == True:
                await ctx.send('***' + settings.searches[ctx.guild.id][0]['result'][0]['title']+'\n*** has been added to the queue')
            else:
                await ctx.send('Now Playing:\n***' + settings.searches[ctx.guild.id][0]['result'][0]['title']+'***')            
            settings.queues[ctx.guild.id].append(settings.searches[ctx.guild.id][0]['result'][0]['link'])
            settings.titles[ctx.guild.id].append(settings.searches[ctx.guild.id][0]['result'][0]['title'])
            settings.searches[ctx.guild.id][0] = ''
            if settings.downloading[ctx.guild.id][0] == False:
                settings.timers[ctx.guild.id].start()
        else:
            await ctx.send('I am not in a voice channel')
    
    @commands.command(pass_context = True)
    async def playlist(self, ctx, *, playlist: str):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice != None:
            if playlist == '1' or playlist == '2' or playlist == '3' or playlist == '4' or playlist == '5':
                if settings.searches[ctx.guild.id][0] == '':
                    await ctx.send('There is currently no searched music, please search for a playlist and try again.')
                else:
                    print('successfully chose a playlist')
                    if voice.is_playing() or voice.is_paused() or settings.downloading[ctx.guild.id][0] == True:
                        if settings.searches[ctx.guild.id][1] == None:
                            await ctx.send('Playlist number ' + playlist + ' selected:\n***' + settings.searches[ctx.guild.id][0]['result'][int(playlist)-1]['title']+'*** has been added to the queue')
                        else:
                            await settings.searches[ctx.guild.id][1].edit('playlist number ' + playlist + ' selected:\n***' + settings.searches[ctx.guild.id][0]['result'][int(playlist)-1]['title']+'*** has been added to the queue')
                    else:
                        if settings.searches[ctx.guild.id][1] == None:
                            await ctx.send('Playlist number ' + playlist + ' selected:\nNow Playing:\n***' + settings.searches[ctx.guild.id][0]['result'][int(playlist)-1]['title']+'***')
                            await ctx.send('Please enjoy this music while the playlist is being retrieved.')
                        else:
                            await settings.searches[ctx.guild.id][1].edit('playlist number ' + playlist + ' selected:\nNow Playing:\n***' + settings.searches[ctx.guild.id][0]['result'][int(playlist)-1]['title']+'***')
                            await ctx.send('Please enjoy this music while the playlist is being retrieved.')
                    settings.queues[ctx.guild.id].append(settings.searches[ctx.guild.id][0]['result'][int(playlist)-1]['link'])
                    settings.titles[ctx.guild.id].append(settings.searches[ctx.guild.id][0]['result'][int(playlist)-1]['title'])
                    settings.searches[ctx.guild.id][0] = ''
                    settings.searches[ctx.guild.id][1] = ''
                    if settings.downloading[ctx.guild.id][0] == False:
                        settings.timers[ctx.guild.id].start()
            else:
                vidsearch = PlaylistsSearch(playlist, limit = 5)
                settings.searches[ctx.guild.id][0] = vidsearch.result()
                msg = await ctx.send('Please select a playlist from the following results:\nSyntax:\n' + extensions + 'play 3\n1: ***' + settings.searches[ctx.guild.id][0]['result'][0]['title'] + 
                '*** \tSize: ' + settings.searches[ctx.guild.id][0]['result'][0]['videoCount'] + '\n'+
                f'2: ***' + settings.searches[ctx.guild.id][0]['result'][1]['title'] + '*** \tSize:' + settings.searches[ctx.guild.id][0]['result'][1]['videoCount'] + '\n'+
                f'3: ***' + settings.searches[ctx.guild.id][0]['result'][2]['title'] + '*** \tSize:' + settings.searches[ctx.guild.id][0]['result'][2]['videoCount'] + '\n'+
                f'4: ***' + settings.searches[ctx.guild.id][0]['result'][3]['title'] + '*** \tSize:' + settings.searches[ctx.guild.id][0]['result'][3]['videoCount'] + '\n'+
                f'5: ***' + settings.searches[ctx.guild.id][0]['result'][4]['title'] + '*** \tSize:' + settings.searches[ctx.guild.id][0]['result'][4]['videoCount'] + '\n')
                settings.searches[ctx.guild.id][1] = msg
        else:
            await ctx.send('I am not in a voice channel')
    
    @commands.command(pass_context = True)
    async def qplaylist(self, ctx, *, playlist: str):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice != None:
            vidsearch = PlaylistsSearch(playlist, limit = 1)
            settings.searches[ctx.guild.id][0] = vidsearch.result()
            if voice.is_playing() or voice.is_paused() or settings.downloading[ctx.guild.id][0] == True:
                await ctx.send('***' + settings.searches[ctx.guild.id][0]['result'][0]['title']+'\n*** has been added to the queue')
            else:
                await ctx.send('Now Playing Playlist:\n***' + settings.searches[ctx.guild.id][0]['result'][0]['title']+'*** \nSize: '+ settings.searches[ctx.guild.id][0]['result'][0]['videoCount'])            
            settings.queues[ctx.guild.id].append(settings.searches[ctx.guild.id][0]['result'][0]['link'])
            settings.titles[ctx.guild.id].append(settings.searches[ctx.guild.id][0]['result'][0]['title'])
            settings.searches[ctx.guild.id][0] = ''
            if settings.downloading[ctx.guild.id][0] == False:
                settings.timers[ctx.guild.id].start()
        else:
            await ctx.send('I am not in a voice channel')

    @commands.command(pass_context = True)
    async def showqueue(self, ctx):
        queued = ''
        counter = 0
        if ctx.guild.id in settings.titles:
            for title in settings.titles[ctx.guild.id]:
                queued = queued + str(counter+1) + ': ***' + settings.titles[ctx.guild.id][counter] + '***\n'
                counter = counter + 1
            if queued == '':
                await ctx.send('There are no songs currently on queue')
            else:
                if len(queued) > 1970:
                    await ctx.send('The queue is currently too long to print')
                    queued = ''
                    for counter in range(0, 10):
                        queued = queued + str(counter+1) + ': ***' + settings.titles[ctx.guild.id][counter] + '***\n'
                    await ctx.send('The next 10 songs in queue will be printed instead:\n' + queued)
                else:
                    await ctx.send('Songs currently on queue:\n' + queued)
        else:
            await ctx.send('There is no active queue for this server')

    @commands.command(pass_context = True)
    async def repeat(self, ctx):
        if ctx.guild.id in settings.downloading:
            if settings.downloading[ctx.guild.id][1]:
                settings.downloading[ctx.guild.id][1] = False
                await ctx.send('Repeating has been turned off')
            else:
                settings.downloading[ctx.guild.id][1] = True
                await ctx.send('Repeating has been turned on')
        else:
            await ctx.send('I am not in a voice channel')

    @commands.command(pass_context = True)
    async def shuffle(self, ctx):
        if ctx.guild.id in settings.downloading:
            if settings.downloading[ctx.guild.id][2]:
                settings.downloading[ctx.guild.id][2] = False
                await ctx.send('Shuffling has been turned off')
            else:
                settings.downloading[ctx.guild.id][2] = True
                await ctx.send('Shuffling has been turned on')
        else:
            await ctx.send('I am not in a voice channel')
    
    @commands.command(pass_context = True)
    async def status(self, ctx):
        if ctx.guild.id in settings.downloading:
            if settings.downloading[ctx.guild.id][1]:
                await ctx.send('Repeating is turned on')
            else:
                await ctx.send('Repeating is turned off')
            if settings.downloading[ctx.guild.id][2]:
                await ctx.send('Shuffling is turned on')
            else:
                await ctx.send('Shuffling is turned off')
        else:
            await ctx.send('I am not in a voice channel')

    @commands.command(pass_context = True)
    async def remove(self, ctx, song:int):
        if ctx.guild.id in settings.queues:
            if song <= len(settings.queues[ctx.guild.id]) and song > 0:
                await ctx.send(f"***{settings.titles[ctx.guild.id][song-1]}***\nhas been removed from the queue")
                settings.queues[ctx.guild.id].pop(song-1)
                settings.titles[ctx.guild.id].pop(song-1)
            else:
                await ctx.send("Invalid choice of song removal")
        else:
            await ctx.send('There is no active queue')

    @commands.command(pass_context = True)
    async def save(self, ctx):
        if ctx.guild.id in settings.queues:
            settings.saveq[ctx.guild.id] = settings.queues[ctx.guild.id]
            settings.saved[ctx.guild.id] = settings.downloading[ctx.guild.id]
            settings.saved[ctx.guild.id][0] = False
            settings.savet[ctx.guild.id] = settings.titles[ctx.guild.id]
            msg = f"{len(settings.savet[ctx.guild.id])} songs have been saved\n"
            if settings.saved[ctx.guild.id][1] == True:
                msg = msg + "Repeating was left on"
            else:
                msg = msg + "Repeating was left off"
            await ctx.send(msg)
            print(settings.saveq)
        else:
            await ctx.send('I am not in a voice channel')

    @commands.command(pass_context = True)
    async def load(self, ctx):
        print(settings.saveq)
        if ctx.guild.id in settings.saveq:
            voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
            voice.stop()
            settings.queues[ctx.guild.id] = settings.saveq[ctx.guild.id]
            settings.downloading[ctx.guild.id] = settings.saved[ctx.guild.id]
            settings.titles[ctx.guild.id] = settings.savet[ctx.guild.id]
            msg = f"{len(settings.titles[ctx.guild.id])} songs have been recovered\n"
            if settings.downloading[ctx.guild.id][1] == True:
                msg = msg + "Repeating is on"
            else:
                msg = msg + "Repeating is off"
            await ctx.send(msg)
            settings.timers[ctx.guild.id].start()
        else:
            await ctx.send('I am not in a voice channel')

    @commands.command(pass_context = True)
    async def temp(self, ctx):
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        voice.stop()

def setup(client):
    client.add_cog(Music(client))

def queue(ctx, client):
    pwd = os.path.dirname(os.path.realpath(__file__))
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if (voice.is_playing() or voice.is_paused()):
        pass
    else:
        settings.channels[ctx.guild.id] = nextcord.utils.get(ctx.guild.channels, id=ctx.channel.id)
        settings.timers[ctx.guild.id].stop()
        if settings.queues[ctx.guild.id]:
            if settings.queues[ctx.guild.id][0].startswith('song'):
                source = FFmpegPCMAudio(pwd+'/'+str(ctx.guild.id)+'/'+settings.queues[ctx.guild.id][0])
            else:
                settings.downloading[ctx.guild.id][0] = True
                if settings.downloading[ctx.guild.id][2] and (not settings.indexes[ctx.guild.id]):
                    if len(settings.queues[ctx.guild.id]) > 1:
                        if settings.downloading[ctx.guild.id][1]:
                            index = random.randint(1, (len(settings.queues[ctx.guild.id])-1)) - 1
                        else:
                            index = random.randint(1, len(settings.queues[ctx.guild.id])) - 1
                    else:
                        index = 0
                else:
                    index = 0
                    settings.indexes[ctx.guild.id] = False
                if "playlist" in settings.queues[ctx.guild.id][index]:
                    os.system('rm ' + pwd+'/'+str(ctx.guild.id) + '/*.opus')
                    os.system('rm ' + pwd+'/'+str(ctx.guild.id) + '/*.webm')
                    source = FFmpegPCMAudio(pwd + '/Dependencies/' + 'Elevator_Music.mp3')
                    player = voice.play(source)
                    songlist, title = dccommands.retrievePlaylist(settings.queues[ctx.guild.id][index])
                    voice.stop()
                    settings.queues[ctx.guild.id].pop(index)
                    settings.queues[ctx.guild.id] = songlist+settings.queues[ctx.guild.id]
                    settings.titles[ctx.guild.id].pop(index)
                    settings.titles[ctx.guild.id] = title+settings.titles[ctx.guild.id]
                else:
                    os.system('rm ' + str(ctx.guild.id) + '/*.opus')
                    source, title = dccommands.retrieveAudio(settings.queues[ctx.guild.id][index], (pwd+'/'+str(ctx.guild.id)))
                    if settings.downloading[ctx.guild.id][1]:
                        settings.titles[ctx.guild.id].append(settings.titles[ctx.guild.id][index])
                        settings.queues[ctx.guild.id].append(settings.queues[ctx.guild.id][index])
                    settings.titles[ctx.guild.id].pop(index)
                    player = voice.play(source)
                    settings.queues[ctx.guild.id].pop(index)
            settings.timers[ctx.guild.id].start()
            settings.downloading[ctx.guild.id][0] = False
        else:
            os.system('rm ' + pwd+'/'+str(ctx.guild.id) + '/*.opus')
            os.system('rm ' + pwd+'/'+str(ctx.guild.id) + '/*.webm')
            print('No queued items')
