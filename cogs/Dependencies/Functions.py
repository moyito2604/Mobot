# Functions.py defines several different functions necessary for all the different functions Mobot has
# It includes several functions that retrieve songs, playlists, Quotes, etc.
import asyncio
import time
from random import randint
from nextcord import FFmpegOpusAudio
import yt_dlp
from yt_dlp.utils import DownloadError
import scrapetube
import os
import nextcord
from nextcord import FFmpegPCMAudio
import validators
from validators.utils import ValidationError
import os.path
import settings
import random

# Sets the working directory
pwd = os.path.dirname(os.path.realpath(__file__))


# This function retrieves a techquote from the Funnytechquotes.txt repository of quotes
# It then returns the quote to be used in Mobot when the command is run
def techQuotes():
    files = open(pwd + '/Quotes/' + 'Funnytechquotes.txt', 'r')
    quote = ''
    randomquote = randint(1, 62)
    for counter in range(randomquote):
        quote = files.readline()
    print('\nQuote number ' + str(randomquote) + ' was printed')
    files.close()
    return quote

# The loggerOutputs class defines a logger used for yt_dlp
# This logger is then used to output to STDOUT and STDERR
# It also generates files with yt_dlp logs for individual servers
class loggerOutputs:
    def __init__(self, ctx):
        self.ctx = ctx

    def error(self, msg):
        with open(f'logs/{self.ctx.guild.name}_logs.log', 'a+') as file:
            file.write("Error: " + msg + "\n")
            print("Error: " + msg)

    def warning(self, msg):
        with open(f'logs/{self.ctx.guild.name}_logs.log', 'a+') as file:
            file.write("Warning: " + msg + "\n")
            print("Warning: " + msg)

    def debug(self, msg):
        with open(f'logs/{self.ctx.guild.name}_logs.log', 'a+') as file:
            file.write("Log: " + msg + "\n")
            print(msg)


# RetrieveAudio defines a function which downloads a YouTube video and converts it to an .opus file to be played by
# Mobot
async def retrieveAudio(url: str, path: str, ctx, index):
    # ydl_ops defines a set of options used to run yt_dlp and get the desired output
    ydl_opts = {
        'format': 'bestaudio/best',
        'logger': loggerOutputs(ctx=ctx),
        'outtmpl': path + '/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredquality': '0',
        }],
        'noplaylist': True
    }

    # This then extracts the video and grabs the necessary information
    # It's all done from the folder for each specific server
    # It then returns the audio source, the title, thumbnail, and duration of the video
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            settings.current[ctx.guild.id]["title"] = settings.titles[ctx.guild.id][index]
            settings.current[ctx.guild.id]["url"] = settings.queues[ctx.guild.id][index]['url']
            settings.current[ctx.guild.id]["user"] = settings.queues[ctx.guild.id][index]['user']
            print(f"\n{settings.current[ctx.guild.id]}\n")
            user = settings.queues[ctx.guild.id][index]['user']
            settings.queues[ctx.guild.id].pop(index)
            info = await loop.run_in_executor(None, ydl.extract_info, url)
            settings.titles[ctx.guild.id].pop(index)
            title = info.get('title', None)
            extension = info.get('ext')
            print(f"\n{extension}\n")

        # If there is an error with downloading, it then tries to download the next song
        except DownloadError:
            print("The Song has failed to Download")
            channel = nextcord.utils.get(settings.channels[ctx.guild.id].guild.channels,
                                         id=settings.channels[ctx.guild.id].channel.id)
            await channel.send("The current Track has failed to download. The next Track will now Download")
            return await retrieveAudio(settings.queues[ctx.guild.id][0]['url'], (pwd + '/' + str(ctx.guild.id)), ctx, 0)

    # It then renames the song and gets it ready to be played
    if extension == "webm":
        extension = "opus"
    for file in os.listdir(path):
        if file.endswith(f".{extension}"):
            os.rename(path + '/' + file, path + f"/song.{extension}")
    source = await FFmpegOpusAudio.from_probe(path + f"/song.{extension}")
    times = time.gmtime(info["duration"])
    duration = time.strftime("%H:%M:%S", times)
    return source, title, info["thumbnails"][0]["url"], duration, user


# This function retrieves a playlist from YouTube using scrapetube and pushes the urls to queue
# It also retrieves the titles, duration, and the user who placed each song and pushes it to queue as well
async def retrievePlaylist(url, ctx):
    id = url.lstrip('https://www.youtube.com/playlist?list=')
    loop = asyncio.get_event_loop()
    videos = await loop.run_in_executor(None, scrapetube.get_playlist, id)
    songlist = []
    title = []
    lengths = []
    for video in videos:
        songlist.append('https://www.youtube.com/watch?v=' + video['videoId'])
        title.append(video['title']['runs'][0]['text'])
        times = time.gmtime(int(video['lengthSeconds']))
        lengths.append(time.strftime("%H:%M:%S", times))
    channel = nextcord.utils.get(settings.channels[ctx.guild.id].guild.channels,
                                 id=settings.channels[ctx.guild.id].channel.id)
    print("Playlist retrieved successfully")
    await channel.send('Playlist Retrieved Successfully')
    return songlist, title, lengths


# Checkurl is a function that ensures that the given URL is a valid url
def checkurl(url_string: str):
    result = validators.url(url_string)

    if isinstance(result, ValidationError):
        return False

    return result


# The queue function is what runs the entire music bot.
# This function is used to periodically check if a song is ready to be loaded up into the voice chat for playing
async def queue(ctx, client):
    # First it sets the working directory and checks if the bot is playing a song
    pwd = os.path.dirname(os.path.realpath(__file__))
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if (voice.is_playing() or voice.is_paused()):
        pass
    else:

        # It then checks if there is an active queue for an individual server
        if settings.queues[ctx.guild.id]:
            if settings.queues[ctx.guild.id][0]['url'].startswith('song'):
                source = FFmpegPCMAudio(pwd + '/' + str(ctx.guild.id) + '/' + settings.queues[ctx.guild.id][0])

            # It then sets up everything for the next song to play properly
            # It clears the guild directory and sets downloading to true
            else:
                settings.downloading[ctx.guild.id][0] = True

                # It then checks if shuffle is turned on and grabs the index for the next shuffle
                if settings.downloading[ctx.guild.id][2] and (not settings.indexes[ctx.guild.id]):
                    if len(settings.queues[ctx.guild.id]) > 1:
                        if settings.downloading[ctx.guild.id][1]:
                            index = random.randint(1, (len(settings.queues[ctx.guild.id]) - 1)) - 1
                        else:
                            index = random.randint(1, len(settings.queues[ctx.guild.id])) - 1
                    else:
                        index = 0
                else:
                    index = 0
                    settings.indexes[ctx.guild.id] = False

                # It then checks if the next item is a playlist and retrieves every item in the playlist
                url = settings.queues[ctx.guild.id][index]['url']
                if "playlist" in url and ("youtube" in url or "youtu.be" in url):
                    songlist, title, durations = await retrievePlaylist(settings.queues[ctx.guild.id][index]['url'], ctx)
                    voice.stop()
                    users = settings.queues[ctx.guild.id][index]['user']
                    settings.queues[ctx.guild.id].pop(index)
                    counter = 0
                    curqueue = settings.queues[ctx.guild.id]
                    settings.queues[ctx.guild.id] = []
                    for item in songlist:
                        settings.queues[ctx.guild.id].append({})
                        settings.queues[ctx.guild.id][-1]['url'] = item
                        settings.queues[ctx.guild.id][-1]['user'] = users
                        settings.queues[ctx.guild.id][-1]['duration'] = durations[counter]
                        counter += 1
                    settings.queues[ctx.guild.id] = settings.queues[ctx.guild.id] + curqueue
                    settings.titles[ctx.guild.id].pop(index)
                    settings.titles[ctx.guild.id] = title + settings.titles[ctx.guild.id]

                # After that it then retrieves the next audio and if it is set to repeating, it places the song back
                # to the end of the queue It then plays the next song and sets downloading to false
                else:
                    if settings.downloading[ctx.guild.id][1]:
                        settings.titles[ctx.guild.id].append(settings.titles[ctx.guild.id][index])
                        settings.queues[ctx.guild.id].append(settings.queues[ctx.guild.id][index])
                    source, title, thumbnail, duration, user = await retrieveAudio(
                        settings.queues[ctx.guild.id][index]['url'], (pwd + '/' + str(ctx.guild.id)), ctx, index)
                    textchannel = nextcord.utils.get(settings.channels[ctx.guild.id].guild.channels,
                                                     id=settings.channels[ctx.guild.id].channel.id)
                    embed = nextcord.Embed(title="Now playing:", description=title)
                    embed.add_field(name="Added By:", value=user, inline=False)
                    embed.set_footer(text=f"Duration: {duration}")
                    embed.set_thumbnail(url=thumbnail)
                    await textchannel.send(mention_author=True, embed=embed)
                    # Reminder, ARRAY POPPING FOR TITLES AND QUEUES IS IN retrieveAudio()
                    if settings.downloading[ctx.guild.id][3]:
                        # loop = asyncio.get_event_loop()
                        print("normalized")
                        # raw = await loop.run_in_executor(None, AudioSegment.from_file, f"{pwd}/{ctx.guild.id}/song.opus", codec = "opus")
                        # raw = AudioSegment.from_file(f"{pwd}/{ctx.guild.id}/song.opus", codec = "opus")
                        # normalized = effects.normalize(raw, headroom=10)
                        # normalized = await loop.run_in_executor(None, effects.normalize, raw, headroom=10)
                        # os.system('rm ' + str(ctx.guild.id) + '/*.opus')
                        # normalized.export(f"{pwd}/{ctx.guild.id}/song.opus", format="opus")
                        # await loop.run_in_executor(None, normalized.export, f"{pwd}/{ctx.guild.id}/song.opus", format="opus")
                        # source = FFmpegOpusAudio(f"{pwd}/{ctx.guild.id}/song.opus")
                    player = voice.play(source)
            settings.downloading[ctx.guild.id][0] = False

        # If there is not an active queue, it cleans up and pauses the timer
        else:
            await settings.timers[ctx.guild.id].pause()
            print('No queued items')
