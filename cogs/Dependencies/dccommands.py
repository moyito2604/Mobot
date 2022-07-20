#dccommands.py defines several different functions necessary for all of the different functions Mobot has
#It includes several functions that retrieve songs, playlists, Quotes, etc.
import asyncio
from random import randint
from nextcord import FFmpegOpusAudio
import yt_dlp
import os
import scrapetube
import settings
import nextcord

#Sets the working directory
pwd = os.path.dirname(os.path.realpath(__file__))

#This function retrieves a techquote from the Funnytechquotes.txt repository of quotes
#It then returns the quote to be used in Mewbot when the command is run
def techQuotes():
    files = open(pwd + '/Quotes/' + 'Funnytechquotes.txt', 'r')
    quote = ''
    randomquote = randint(1, 62)
    for counter in range(randomquote):
        quote = files.readline()
    print('\nQuote number ' + str(randomquote) + ' was printed')
    files.close()
    return quote

#Both SeanQuotes() and oneSeam() retrieve a seanQuote from the repository of Sean Quotes
#As this is not a function of Mewbot, these two functions are useless when this file is included in the Mewbot code
def seanQuotes():
    files = open(pwd + '/Quotes/' + 'Seanquotes.txt', 'r')
    quote = ''
    randomquote = randint(2, 117)
    for counter in range(randomquote):
        quote = files.readline()
    print('\nSean Quote number ' + str(randomquote) + ' was printed')
    files.close()
    return quote

def oneSeam():
    files = open(pwd + '/Quotes/' + 'Seanquotes.txt', 'r')
    quote = ''
    quote = files.readline()
    print('\nSean Quote number ' + str(1) + ' was printed')
    files.close()
    return quote

#The loggerOutputs class defines a logger used for yt_dlp
#This logger is then used to output to STDOUT and STDERR
#It also generates files with yt_dlp logs for individual servers
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

#RetrieveAudio defines a function which downloads a youtube video and converts it to an .opus file to be played by mewbot
async def retrieveAudio(url, path:str, ctx):

#ydl_ops defines a set of options used to run yt_dlp and get the desired output
    ydl_opts = {
    'format': 'bestaudio/best',
    'logger': loggerOutputs(ctx=ctx),
    'outtmpl': path + '/%(title)s.%(ext)s',
    'postprocessors': [{
        'key':'FFmpegExtractAudio',
        'preferredquality': '192',
    }],
    }

#This then extracts the video from youtube and grabs the necessary information
#Its all done from the folder for each specific server
#It then returns the audio source and the title
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = await loop.run_in_executor(None, ydl.extract_info, url)
        title = info.get('title', None)
    for file in os.listdir(path):
        if file.endswith(".opus"):
            os.rename(path+'/'+ file, path+'/song.opus')
    source = FFmpegOpusAudio(path+'/song.opus')
    return source, title

#This function retrieves a playlist from youtube using scrapetube and pushes the urls to queue
#It also retrieves the titles of each song and pushes it to queue as well
async def retrievePlaylist(url, ctx):
    id = url.lstrip('https://www.youtube.com/playlist?list=')
    loop = asyncio.get_event_loop()
    videos = await loop.run_in_executor(None, scrapetube.get_playlist, id)
    songlist = []
    title = []
    for video in videos:
        songlist.append('https://www.youtube.com/watch?v='+ video['videoId'])
        title.append(video['title']['runs'][0]['text'])
    channel = nextcord.utils.get(settings.channels[ctx.guild.id].guild.channels, id=settings.channels[ctx.guild.id].channel.id)
    print("Playlist retrieved successfully")
    await channel.send('Playlist Retrieved Successfully')
    return songlist, title
    
