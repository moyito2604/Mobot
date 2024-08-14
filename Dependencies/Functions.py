# Functions.py defines several different functions necessary for all the different functions Mobot has
# It includes several functions that retrieve songs, playlists, Quotes, etc.
import asyncio
from contextlib import suppress
from Dependencies.Error import AudioDownloadError
from Dependencies.Error import internalErrorEmbed
import time
from random import randint
import jsonbuilder
from nextcord import FFmpegOpusAudio
from nextcord.errors import Forbidden
import yt_dlp
from yt_dlp.utils import DownloadError
import scrapetube
import os
import nextcord
import validators
from validators.utils import ValidationError
import os.path
import settings


# This provides colors for output in terminal
class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# This function retrieves a techquote from the Funnytechquotes.txt repository of quotes
# It then returns the quote to be used in Mobot when the command is run
def techQuotes():
    # Sets the working directory
    currdir = settings.pwd + '/Dependencies/'
    files = open(currdir + '/Quotes/' + 'Funnytechquotes.txt', 'r')
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
        with (open(f'logs/{self.ctx.guild.name}_logs.log', 'a+') as file):
            file.write("Error: " + msg + "\n")
            settings.env_vars[self.ctx.guild.id]['log'] = settings.env_vars[self.ctx.guild.id][
                                                              'log'] + f"Error: {msg}\n"

    def warning(self, msg):
        with open(f'logs/{self.ctx.guild.name}_logs.log', 'a+') as file:
            file.write("Warning: " + msg + "\n")
            settings.env_vars[self.ctx.guild.id]['log'] = settings.env_vars[self.ctx.guild.id][
                                                              'log'] + f"Warning: {msg}\n"

    def debug(self, msg):
        with open(f'logs/{self.ctx.guild.name}_logs.log', 'a+') as file:
            file.write("Log: " + msg + "\n")


# RetrieveAudio defines a function which downloads a YouTube video and converts it to an .opus file to be played by
# Mobot
async def retrieveAudio(url: str, path: str, ctx, filename: str = "song", pop: bool = True):
    # Sets the working directory
    settings.env_vars[ctx.guild.id]['log'] = ''
    # ydl_ops defines a set of options used to run yt_dlp and get the desired output
    ydl_opts = {
        'format': 'bestaudio/best',
        'logger': loggerOutputs(ctx=ctx),
        'outtmpl': path + f"/{filename}.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredquality': '0',
        }],
        'noplaylist': True
    }

    if settings.proxy != "None":
        ydl_opts['proxy'] = settings.proxy

    # This then extracts the video and grabs the necessary information
    # It's all done from the folder for each specific server
    # It then returns the audio source, the title, thumbnail, and duration of the video
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            settings.current[ctx.guild.id] = settings.queues[ctx.guild.id][0]
            user = settings.queues[ctx.guild.id][0]['user']
            name = settings.queues[ctx.guild.id][0]['name']
            avatar = settings.queues[ctx.guild.id][0]['avatar']

            # Ensures that the item is popped only when it needs to be
            if pop:
                settings.queues[ctx.guild.id].pop(0)
            info = await loop.run_in_executor(None, ydl.extract_info, url)
            title = info.get('title', None)
            # extension = info.get('ext')

        # If there is an error with downloading, it then sends an error message
        except DownloadError:
            channel = nextcord.utils.get(settings.channels[ctx.guild.id].guild.channels,
                                         id=settings.channels[ctx.guild.id].channel.id)
            embed = await internalErrorEmbed("Failed to Download Track", settings.env_vars[ctx.guild.id]['log'],
                                             ctx, notify=True)
            await channel.send(embed=embed)
            raise AudioDownloadError(f"Failed to Download Track in Guild \"{ctx.guild.name}\"")

    # # It then renames the song and gets it ready to be played
    # # This gives a list of extensions and how they are processed
    # if extension == "webm":
    #     extension = "opus"
    # elif extension == "mp4":
    #     extension = "m4a"
    #

    song = "song.opus"
    for file in os.listdir(path):
        if "song" in file:
            song = file

    source = FFmpegOpusAudio(f"{path}/{song}")

    times = "N/A"
    if "duration" in info:
        times = time.gmtime(info["duration"])
        duration = time.strftime("%H:%M:%S", times)
    else:
        duration = times

    thumbnail = ""
    if "thumbnails" in info:
        thumbnail = info["thumbnails"][0]["url"]

    return {'source': source, 'title': title, 'thumbnail': thumbnail, 'duration': duration,
            'user': user, 'name': name, 'avatar': avatar}


# This function retrieves a playlist from YouTube using scrapetube and pushes the urls to queue
# It also retrieves the titles, duration, and the user who placed each song and pushes it to queue as well
async def retrievePlaylist(url, titles, ctx):
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
    print(f"Playlist {Color.RED}{Color.BOLD}{titles}{Color.END} Extracted Successfully for {Color.BLUE}{Color.BOLD}"
          f"{ctx.guild.name}{Color.END}")
    return songlist, title, lengths


def loadPlaylist(songlist, title, lengths, ctx):
    temp = []
    for counter, item in enumerate(songlist):
        temp.append({})
        temp[-1]['url'] = item
        temp[-1]['user'] = settings.queues[ctx.guild.id][0]['user']
        temp[-1]['duration'] = lengths[counter]
        temp[-1]['name'] = settings.queues[ctx.guild.id][0]['name']
        temp[-1]['avatar'] = settings.queues[ctx.guild.id][0]['avatar']
        temp[-1]['title'] = title[counter]
    settings.queues[ctx.guild.id].pop(0)
    curqueue = settings.queues[ctx.guild.id]
    settings.queues[ctx.guild.id] = []
    settings.queues[ctx.guild.id] = temp + curqueue


# Checkurl is a function that ensures that the given URL is a valid url
def checkurl(url_string: str):
    result = validators.url(url_string)

    if isinstance(result, ValidationError):
        return False

    return result


# Stops the timer specifically for the server id provided
async def stopTimer(guild):
    # First it ensures that the timer exists and cancels it, where then it suppresses the cancelled error and awaits the
    # Task to its completion
    if settings.env_vars[guild].get("Timer", None):
        settings.env_vars[guild]["Timer"].cancel()
        with suppress(asyncio.CancelledError):
            await settings.env_vars[guild]["Timer"]


# This function takes in a time in colon format to format it to 00:00:00 format
def timetostr(timestring: str):
    timelist = timestring.rsplit(":")
    seconds = None
    minutes = None
    hours = None
    try:
        seconds = timelist.pop()
        minutes = timelist.pop()
        hours = timelist.pop()
    except IndexError:
        if seconds is None: seconds = "0"
        if minutes is None: minutes = "0"
        if hours is None: hours = "0"
    return "%02d:%02d:%02d" % (int(hours), int(minutes), int(seconds))


# The queue function is what runs the entire music bot.
# This function is used to periodically check if a song is ready to be loaded up into the voice chat for playing
async def queue(ctx, client):
    currdir = settings.pwd + '/Dependencies/'

    # First it sets the working directory and checks if the bot is playing a song
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)

    # If there is a song currently playing or is paused, it attempts to preload the next song
    if voice.is_playing() or voice.is_paused():

        # Temporarily Pauses Timer
        settings.env_vars[ctx.guild.id]["Active"] = False

        # Imports the preloaded song's information
        item = jsonbuilder.importJson(f"{currdir}{str(ctx.guild.id)}/preload.json")

        # Then it makes sure there is a next queue item
        if len(settings.queues[ctx.guild.id]) > 0:

            # It then checks if the next item is a playlist and attempts to preload it
            url = settings.queues[ctx.guild.id][0]['url']
            if "playlist" in url and ("youtube" in url or "youtu.be" in url):
                songlist, title, durations = await retrievePlaylist(settings.queues[ctx.guild.id][0]['url'],
                                       settings.queues[ctx.guild.id][0]['title'], ctx)
                loadPlaylist(songlist, title, durations, ctx)
            elif item and (item.get("title", None) == settings.queues[ctx.guild.id][0]["title"]):
                pass
            else:

                # Once it ensures there is a next queue item, it preloads it and exports the information to a Json
                settings.env_vars[ctx.guild.id]["Downloading"] = True
                song = await retrieveAudio(settings.queues[ctx.guild.id][0]['url'], (currdir + str(ctx.guild.id)), ctx,
                                           "preload", False)
                del song["source"]
                jsonbuilder.exportJson(song, f"{currdir}{str(ctx.guild.id)}/preload.json")
                print(f"Song {Color.RED}{Color.BOLD}{song["title"]}{Color.END} has been preloaded for "
                      f"{Color.BLUE}{Color.BOLD}{ctx.guild.name}{Color.END}")

        settings.env_vars[ctx.guild.id]["Downloading"] = False

        # Reinitialized Timer
        settings.env_vars[ctx.guild.id]["Active"] = True

    else:

        # Temporarily Pauses Timer
        settings.env_vars[ctx.guild.id]["Active"] = False

        # It then checks if there is an active queue for an individual server
        if settings.queues[ctx.guild.id]:

            # It then sets up everything for the next song to play properly
            # It clears the guild directory and sets downloading to true
            settings.env_vars[ctx.guild.id]["Downloading"] = True

            # It then checks if the next item is a playlist and retrieves every item in the playlist
            url = settings.queues[ctx.guild.id][0]['url']
            if "playlist" in url and ("youtube" in url or "youtu.be" in url):
                songlist, title, durations = await retrievePlaylist(settings.queues[ctx.guild.id][0]['url'],
                                                                    settings.queues[ctx.guild.id][0]['title'], ctx)
                loadPlaylist(songlist, title, durations, ctx)

            # After that it then retrieves the next audio and if it is set to repeating, it places the song back
            # to the end of the queue It then plays the next song and sets downloading to false
            else:
                if settings.env_vars[ctx.guild.id]["Repeat"]:
                    settings.queues[ctx.guild.id].append(settings.queues[ctx.guild.id][0])

                # Ensures that track can be downloaded, if not, it fails and prints a message
                try:
                    song = {}

                    # Checks if there is a preloaded song and if it is the same as the next item in queue, it sets it up
                    # for discord to play it
                    if "preload.json" in os.listdir(currdir + str(ctx.guild.id)):
                        song = jsonbuilder.importJson(currdir + str(ctx.guild.id) + "/preload.json")
                    if song.get("title", None) == settings.queues[ctx.guild.id][0]["title"]:

                        # It then removes the preloaded song's information, and it renames the file to song.extension
                        os.remove(currdir + str(ctx.guild.id) + "/preload.json")
                        extension = ".opus"
                        for file in os.listdir(currdir + str(ctx.guild.id)):
                            if "preload" in file:
                                extension = os.path.splitext(f"{currdir + str(ctx.guild.id)}/{file}")[1]
                                os.rename(f"{currdir + str(ctx.guild.id)}/{file}", f"{currdir + str(ctx.guild.id)}"
                                                                                   f"/song{extension}")
                        song["source"] = FFmpegOpusAudio(f"{currdir + str(ctx.guild.id)}/song{extension}")

                        # Finally, it pops the item from the queue
                        settings.queues[ctx.guild.id].pop(0)
                    else:
                        song = await retrieveAudio(settings.queues[ctx.guild.id][0]['url'],
                                                   (currdir + str(ctx.guild.id)), ctx)
                    textchannel = nextcord.utils.get(settings.channels[ctx.guild.id].guild.channels,
                                                     id=settings.channels[ctx.guild.id].channel.id)
                    embed = nextcord.Embed(title="Now playing:", description=song['title'])
                    embed.set_author(name=song['name'], icon_url=song['avatar'])
                    embed.set_footer(text=f"Duration: {song['duration']}")
                    embed.set_thumbnail(url=song['thumbnail'])
                    print(f"Song {Color.RED}{Color.BOLD}{song['title']}{Color.END} is playing in "
                          f"{Color.BLUE}{Color.BOLD}{ctx.guild.name}{Color.END}")
                    try:
                        await textchannel.send(mention_author=True, embed=embed)
                    except Forbidden:
                        print(f"Unable to print message in {Color.BLUE}{Color.BOLD}{ctx.guild.name}{Color.END}, "
                              f"playing song {Color.RED}{Color.BOLD}{song['title']}{Color.END}")
                    # Reminder, ARRAY POPPING FOR TITLES AND QUEUES IS IN retrieveAudio()
                    player = voice.play(song['source'])
                except AudioDownloadError:
                    print(f"{Color.RED}{Color.BOLD}Error: Failed to Download Track in Guild \""
                          f"{ctx.guild.name}\"{Color.END}")

            settings.env_vars[ctx.guild.id]["Downloading"] = False

            # Reinitialized Timer
            settings.env_vars[ctx.guild.id]["Active"] = True

        # If there is not an active queue, it cleans up and pauses the timer
        else:
            settings.env_vars[ctx.guild.id]["Active"] = False
            print(f"No queued items for {Color.BLUE}{Color.BOLD}{ctx.guild.name}{Color.END}")
