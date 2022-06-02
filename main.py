from calendar import c
import os
from turtle import down
import nextcord
from nextcord.ext import commands
from nextcord import FFmpegPCMAudio
from youtubesearchpython import VideosSearch
import sys
import time
import dccommands
import configgen
import os.path
import yt_dlp
import shutil
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)) + '/Dependencies/')
import Threaded_timer
os.system("clear")

queues = {}
timers = {}
searches = {}
titles = {}
downloading = {}
pwd = os.path.dirname(os.path.realpath(__file__))

configgen.generateConfiguration('m!', True, 'TOKEN', 'TOKEN')
import config
Token = config.Token
extensions = config.extension
seanToken = config.seanToken

intents = nextcord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=extensions, intents=intents, help_command=None, case_insensitive=True)

if Token == 'TOKEN':
    sys.exit("Please put your Bot's Token in the config.py file")

@client.event
async def on_ready():
    game = config.extension + 'help'
    activity = nextcord.Game(name=game, type=3)
    await client.change_presence(status=nextcord.Status.online, activity=activity)
    print('We have logged in as {0.user}\n'.format(client))

@client.command(pass_context = True)
async def ce(ctx, extension):
    await ctx.send('The extension has been changed to ' + extension)
    configgen.generateConfiguration(extension, False, Token, seanToken)
    config.extension = extension
    print('Command extension changed to ' + config.extension + ' successfully')
    game = config.extension + 'help'
    activity = nextcord.Game(name=game, type=3)
    await client.change_presence(status=nextcord.Status.online, activity=activity)
    os.system('python3 main.py')

@client.command(pass_context = True)
async def deez(ctx):
    await ctx.send('Nutz')
    time.sleep(1)
    await ctx.send('GOTTEM!')
    print("Response to deez printed")

@client.command(pass_context = True)
async def tquote(ctx):
    await ctx.send(dccommands.techQuotes())
    print("Response to tquote printed")

@client.command(pass_context = True)
async def ding(ctx):
    await ctx.send('dong')
    print("Response to ding printed")

@client.command(pass_context = True)
async def help(ctx):
    hm = '```***List of Commands you can use***\n\n'
    hm = hm + extensions + 'ce: use to change the command extension using syntax'
    hm = hm + '\t\t' + extensions + 'ce \'extension\'\n' 
    hm = hm + extensions + 'ding: replies with dong\n'
    hm = hm + extensions + 'deez: replies with nutz\n'
    hm = hm + extensions + 'tquote: Generates a tech quote\n\n'
    hm = hm + '***Music Bot Commands***\n'
    hm = hm + extensions + 'join: joins voice channel\n'
    hm = hm + extensions + 'leave: leaves voice channel\n'
    hm = hm + extensions + 'play: plays music with a youtube link, queues music, and plays music currently paused\n'
    hm = hm + 'This command also allows you to search for a song on youtube\n\n'
    hm = hm + extensions + 'stop: stops playing audio and clears the queue\n'
    hm = hm + extensions + 'skip: skips the current track in queue\n'
    hm = hm + extensions + 'showqueue: shows the songs that are currently in queue\n\n'
    hm = hm + 'All of these commands are case insensitive\n'
    hm = hm + '```'
    await ctx.send(hm)

@client.command(pass_context = True)
async def join(ctx):
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if (ctx.author.voice):
        if voice == None:
            if os.path.isdir(pwd + '/' + str(ctx.guild.id)):
                shutil.rmtree(pwd + '/' + str(ctx.guild.id))
                print('directory ' + str(ctx.guild.id) + ' has been deleted')
            os.mkdir(pwd+ '/' + str(ctx.guild.id))
            print('directory ' + str(ctx.guild.id) + ' has been created')
            queues[ctx.guild.id] = []
            titles[ctx.guild.id] = []
            downloading[ctx.guild.id] = False
            searches[ctx.guild.id] = ''
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
            await ctx.send('Successfully Joined the ' + str(channel) + ' voice channel')
            print('Successfully Joined the ' + str(channel) + ' voice channel')
            timers[ctx.guild.id] = Threaded_timer.RepeatedTimer(1, queue, ctx)
            timers[ctx.guild.id].stop()
        else:
            await ctx.send("I am already connected")
    else:
        print('User is not in a voice channel')
        await ctx.send("You are not in a voice channel, you must be in a voice channel for me to join")

@client.command(pass_context = True)
async def leave(ctx):
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if (ctx.voice_client):
        await voice.disconnect()
        await ctx.send("Left the voice channel")
    else:
        await ctx.send("I am not in a voice channel")
    shutil.rmtree(pwd + '/' + str(ctx.guild.id))
    print('directory ' + str(ctx.guild.id) + ' has been deleted')
    timers[ctx.guild.id].stop()
    timers.pop(ctx.guild.id)
    queues.pop(ctx.guild.id)
    searches.pop(ctx.guild.id)
    titles.pop(ctx.guild.id)
    print('Successfully left the voice Channel')

ydl_opts = {
'format': 'bestaudio/best',
'postprocessors': [{
    'key':'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '192',
}]
}

@client.command(pass_context = True)
async def play(ctx, *, url:str):
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if (ctx.author.voice):
        print(url)
        if voice == None:
            if os.path.isdir(pwd + '/' + str(ctx.guild.id)):
                shutil.rmtree(pwd + '/' + str(ctx.guild.id))
                print('directory ' + str(ctx.guild.id) + ' has been deleted')
            os.mkdir(pwd+ '/' + str(ctx.guild.id))
            print('directory ' + str(ctx.guild.id) + ' has been created')
            queues[ctx.guild.id] = []
            titles[ctx.guild.id] = []
            downloading[ctx.guild.id] = False
            searches[ctx.guild.id] = ''
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
            await ctx.send('Successfully Joined the ' + str(channel) + ' voice channel')
            print('Successfully Joined the ' + str(channel) + ' voice channel')
            timers[ctx.guild.id] = Threaded_timer.RepeatedTimer(1, queue, ctx)
            timers[ctx.guild.id].stop()
        if 'https://www.youtube.com' in url or 'https://youtu.be' in url:
            queues[ctx.guild.id].append(url)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False, process=False)
                title = info.get('title', None)
                titles[ctx.guild.id].append(title)
            if voice.is_playing() or voice.is_paused() or downloading[ctx.guild.id] == True:
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
            if downloading[ctx.guild.id] == False:
                timers[ctx.guild.id].start()
        elif url == '1' or url == '2' or url == '3' or url == '4' or url == '5':
            if searches[ctx.guild.id] == '':
                await ctx.send('There is currently no searched music, please search for a song and try again.')
            else:
                print('successfully chose a song')
                if voice.is_playing() or voice.is_paused() or downloading[ctx.guild.id] == True:
                    await ctx.send('Song number ' + url + ' selected:\n***' + searches[ctx.guild.id]['result'][int(url)-1]['title']+'*** has been added to the queue')
                else:
                    await ctx.send('Song number ' + url + ' selected:\nNow Playing:\n***' + searches[ctx.guild.id]['result'][int(url)-1]['title']+'***')
                queues[ctx.guild.id].append(searches[ctx.guild.id]['result'][int(url)-1]['link'])
                titles[ctx.guild.id].append(searches[ctx.guild.id]['result'][int(url)-1]['title'])
                searches[ctx.guild.id] = ''
                if downloading[ctx.guild.id] == False:
                    timers[ctx.guild.id].start()
        else:
            vidsearch = VideosSearch(url, limit = 5)
            searches[ctx.guild.id] = vidsearch.result()
            await ctx.send('Please select a song from the following results:\nSyntax:\n' + extensions + 'play 3\n' + '1: ***' + searches[ctx.guild.id]['result'][0]['title']+'***\n'
            '2: ***' + searches[ctx.guild.id]['result'][1]['title']+'***\n'+
            '3: ***' + searches[ctx.guild.id]['result'][2]['title']+'***\n'+
            '4: ***' + searches[ctx.guild.id]['result'][3]['title']+'***\n'+
            '5: ***' + searches[ctx.guild.id]['result'][4]['title']+'***\n')
    else:
        await ctx.send("You are not in a voice channel, you must be in a voice channel for me to join")

@play.error
async def unpause(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            voice.resume()
            await ctx.send("Music is playing")
        else:
            await ctx.send("There is no paused audio in the voice channel.")


@client.command(pass_context = True)
async def pause(ctx):
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send("Music has been paused")
    else:
        await ctx.send("There is no audio playing in the voice channel.")

@client.command(pass_context = True)
async def stop(ctx):
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing() or voice.is_paused():
        queues[ctx.guild.id].clear()
        titles[ctx.guild.id].clear()
        voice.stop()
        await ctx.send("Music has been stopped and queue has been cleared")
        print("Music has been stopped and queue has been cleared")
        os.system('rm ' + str(ctx.guild.id) + '/*.mp3')
        os.system('rm ' + str(ctx.guild.id) + '/*.webm')
        timers[ctx.guild.id].stop()
    else:
        await ctx.send("There is no audio to stop.")

@client.command(pass_context = True)
async def skip(ctx):
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing() or voice.is_paused():
        voice.stop()
        await ctx.send("Song has been skipped")
        print("\nSong has been skipped\n")
        if queues[ctx.guild.id]:
            if "youtube" in queues[ctx.guild.id][0]:
                title = titles[ctx.guild.id][0]
                if "playlist" in queues[ctx.guild.id][0]:
                    await ctx.send('Now playing playlist:\n***' + title + '***')
                    await ctx.send('Please enjoy this music while the playlist is being retrieved.')
                else:
                    await ctx.send('Now playing:\n***' + title + '***')
            elif "song" in queues[ctx.guild.id][0]:
                await ctx.send('Now playing the next item in your playlist')
        else:
            await ctx.send("Your queue is empty")
    else:
        await ctx.send("There is no music to skip.")

@client.command(pass_context = True)
async def showqueue(ctx):
    queued = ''
    counter = 0
    for title in titles[ctx.guild.id]:
        queued = queued + str(counter+1) + ': ***' + titles[ctx.guild.id][counter] + '***\n'
        counter = counter + 1
    if queued == '':
        await ctx.send('There are no songs currently on queue')
    else:
        await ctx.send('Songs currently on queue:\n' + queued)

def queue(ctx):
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if (voice.is_playing() or voice.is_paused()):
        pass
    else:
        timers[ctx.guild.id].stop()
        if queues[ctx.guild.id]:
            if queues[ctx.guild.id][0].startswith('song'):
                source = FFmpegPCMAudio(pwd+'/'+str(ctx.guild.id)+'/'+queues[ctx.guild.id][0])
            else:
                downloading[ctx.guild.id] = True
                titles[ctx.guild.id].pop(0)
                if "playlist" in queues[ctx.guild.id][0]:
                    os.system('rm ' + str(ctx.guild.id) + '/*.mp3')
                    os.system('rm ' + str(ctx.guild.id) + '/*.webm')
                    source = FFmpegPCMAudio(pwd + '/Dependencies/' + 'Elevator_Music.mp3')
                    player = voice.play(source)
                    songlist, title = dccommands.retrievePlaylist(queues[ctx.guild.id][0], ctx.guild.id)
                    voice.stop()
                    queues[ctx.guild.id].pop(0)
                    queues[ctx.guild.id] = songlist+queues[ctx.guild.id]
                    source = FFmpegPCMAudio(pwd+'/'+str(ctx.guild.id)+'/'+queues[ctx.guild.id][0])
                else:
                    os.system('rm ' + str(ctx.guild.id) + '/*.mp3')
                    source, title = dccommands.retrieveAudio(queues[ctx.guild.id][0], ctx.guild.id)
            player = voice.play(source)
            queues[ctx.guild.id].pop(0)
            timers[ctx.guild.id].start()
            downloading[ctx.guild.id] = False
        else:
            os.system('rm ' + str(ctx.guild.id) + '/*.mp3')
            os.system('rm ' + str(ctx.guild.id) + '/*.webm')
            print('No queued items')

client.run(Token)
