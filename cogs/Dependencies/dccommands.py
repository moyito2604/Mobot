from random import randint
from nextcord import FFmpegOpusAudio
import settings
import yt_dlp
import os

pwd = os.path.dirname(os.path.realpath(__file__))

def techQuotes():
    files = open(pwd + '/Quotes/' + 'Funnytechquotes.txt', 'r')
    quote = ''
    randomquote = randint(1, 62)
    for counter in range(randomquote):
        quote = files.readline()
    print('\nQuote number ' + str(randomquote) + ' was printed')
    files.close()
    return quote

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

class loggerOutputs:
    def __init__(self, ctx):
        self.ctx = ctx
    def error(self, msg):
        with open(f'logs/{self.ctx.guild.id}_logs.log', 'a+') as file:
            file.write("Error: " + msg + "\n")
            print("Error: " + msg)
    def warning(self, msg):
        with open(f'logs/{self.ctx.guild.id}_logs.log', 'a+') as file:
            file.write("Warning: " + msg + "\n")
            print("Warning: " + msg)
    def debug(self, msg):
        with open(f'logs/{self.ctx.guild.id}_logs.log', 'a+') as file:
            file.write("Log: " + msg + "\n")
            print(msg)

def retrieveAudio(url, path:str, ctx):

    ydl_opts = {
    'format': 'bestaudio/best',
    'logger': loggerOutputs(ctx=ctx),
    'outtmpl': path + '/%(title)s.%(ext)s',
    'postprocessors': [{
        'key':'FFmpegExtractAudio',
        'preferredquality': '192',
    }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)
        title = info.get('title', None)
    for file in os.listdir(path):
        if file.endswith(".opus"):
            os.rename(path+'/'+ file, path+'/song.opus')
    source = FFmpegOpusAudio(path+'/song.opus')
    return source, title

def retrievePlaylist(url):
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(url, download = False)
    songlist = []
    title = []
    if 'entries' in info:
        results = info['entries']
        for i, item in enumerate(results):
            songlist.append(info['entries'][i]['webpage_url'])
            title.append(info['entries'][i]['title'])
    return songlist, title
    
