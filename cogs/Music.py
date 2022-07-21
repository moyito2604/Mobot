#cogs.Music runs the Music message commands for mewbot
#This file contains all of the commands associated with the mewbot Music commands

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

#The Music Command holds the definitions for all of the commands needed to run the bot
class Music(commands.Cog):

    def __init__(self, client):
        print("Music Initialized Successfully")
        self.client = client

    #The join function is a command used to join the bot to a server's voice channel
    @commands.command(pass_context = True)
    async def join(self, ctx):

        #First it grabs the voice channel that the music bot is currently in that specific server
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)

        #It then checks if the author is in a voice channel currently
        #It then checks if the bot is in a voice channel and if its not, it joins the voice channel
        #It also arranges server specific dictionary keys to run the bot as well and sets up logging
        #It sets up the threaded timer to monitor the voice activity of the bot as well.
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
                settings.channels[ctx.guild.id] = ctx
                if os.path.exists(f'logs/{ctx.guild.name}_logs.log'):
                    os.remove(f'logs/{ctx.guild.name}_logs.log')

            #If the bot is already currently in a voice channel, sends a message saying its already connected
            else:
                await ctx.send("I am already connected")
        
        #It also checks if the user is not in a voice channel and reminds the user that they need to be in a voice channel for the bot to join.
        else:
            print('User is not in a voice channel')
            await ctx.send("You are not in a voice channel, you must be in a voice channel for me to join")

    #The leave command is what allows the bot to leave a voice channel once the user is done using it in a specific server
    @commands.command(pass_context = True)
    async def leave(self, ctx):
        pwd = os.path.dirname(os.path.realpath(__file__))

        #First it grabs the voice channel that the bot is currently in
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)

        #It then checks if the bot is in a valid voice channel and if its not, it sends a message saying that its not in a VC
        #It then cleans up dictionary keys that are used to run the bot and removes directories
        if (ctx.voice_client):
            shutil.rmtree(pwd + '/' + str(ctx.guild.id))
            print('directory ' + str(ctx.guild.id) + ' has been deleted')
            await settings.timers[ctx.guild.id].stop()
            settings.timers.pop(ctx.guild.id)
            settings.queues.pop(ctx.guild.id)
            settings.searches.pop(ctx.guild.id)
            settings.titles.pop(ctx.guild.id)
            settings.channels.pop(ctx.guild.id)
            print('Successfully left the voice Channel')
            await voice.disconnect()
            await ctx.send("Left the voice channel")
        else:
            await ctx.send("I am not in a voice channel")

    #This command is the most versatile command used for Mewbot
    #It allows you play a song from a youtube link, load a playlist from a youtube link, allows you to search for a song on youtube
    #It also allows a user to select a song to play from the search results
    #It can also be used to join the bot automatically and play a song
    @commands.command(pass_context = True)
    async def play(self, ctx, *, url:str):

        #First it grabs the voice channel to check if the bot is in a voice channel
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        pwd = os.path.dirname(os.path.realpath(__file__))

        #It then checks if the bot is in a Voice channel and if not, it sets it up similarly to the join command
        if (ctx.author.voice):
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
                settings.channels[ctx.guild.id] = ctx
                if os.path.exists(f'logs/{ctx.guild.name}_logs.log'):
                    os.remove(f'logs/{ctx.guild.name}_logs.log')

        #It then verifies that that the bot is in a Voice Channel for it to be used properly
        if voice != None:

            #It then checks if a youtube link was inputted or a search prompt. It then also checks if a youtube link is a playlist or not
            #it then starts the threaded timer
            if 'https://www.youtube.com' in url or 'https://youtu.be' in url or 'https://youtube.com' in url:
                settings.queues[ctx.guild.id].append(url)
                with yt_dlp.YoutubeDL() as ydl:
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
                    else:
                        await ctx.send('Now playing:\n***' + title + '***')
                if settings.downloading[ctx.guild.id][0] == False:
                    await settings.timers[ctx.guild.id].start()

            #Once it checks that its not a youtube link, it checks if it is selecting a song from the search function
            #Once it verifies that it is a search, it then selects the song and adds it to the queue and clears the search
            #It then starts the timer
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
                        await settings.timers[ctx.guild.id].start()
            
            #It then checks if a video search is being performed
            #Once it confirms that its a video search, it saves the key for the search for later use
            else:
                vidsearch = VideosSearch(url, limit = 5)
                settings.searches[ctx.guild.id][0] = vidsearch.result()
                msg = await ctx.send('Please select a song from the following results:\nSyntax:\n' + extensions + 'play 3\n' + '1: ***' + settings.searches[ctx.guild.id][0]['result'][0]['title']+'***\n'
                '2: ***' + settings.searches[ctx.guild.id][0]['result'][1]['title']+'***\n'+
                '3: ***' + settings.searches[ctx.guild.id][0]['result'][2]['title']+'***\n'+
                '4: ***' + settings.searches[ctx.guild.id][0]['result'][3]['title']+'***\n'+
                '5: ***' + settings.searches[ctx.guild.id][0]['result'][4]['title']+'***\n')
                settings.searches[ctx.guild.id][1] = msg
        
        #This then checks if the bot is not in a voice channel and if its not, it sends a message reminding a user to join the voice channel to bring the bot in
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel for me to join")

    #This function checks for an error to the play command, essentially it checks if the wrong amount of arguments are put in and if they are, it changes the function
    #Instead of playing a song, this play command unpauses any paused music in the discord bot
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

    #The pause function is pretty self explanatory
    @commands.command(pass_context = True)
    async def pause(self, ctx):

        #It grabs the voice channel and checks if the bot is in
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send("I am not in a voice channel")
        
        #and if it is, it checks if there is any music playing, if it is, it pauses the music
        #if it is not playing anything, it sends a message stating that there is no music to pause
        else:
            if voice.is_playing():
                voice.pause()
                await ctx.send("Music has been paused")
            else:
                await ctx.send("There is no audio playing in the voice channel.")

    #The stop command is also self-explanatory, it allows the user stop any audio playing from the bot
    #It also allows the bot to cleanup the dictionary keys that run the bot
    @commands.command(pass_context = True)
    async def stop(self, ctx):

        #First it checks for a voice channel
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send("I am not in a voice channel")

        #Then it stops the music and cleans up
        #If there is no music playing, it states that there is no audio currently playing
        else:
            if voice.is_playing() or voice.is_paused():
                settings.queues[ctx.guild.id] = []
                settings.titles[ctx.guild.id] = []
                voice.stop()
                await ctx.send("Music has been stopped and queue has been cleared")
                print("Music has been stopped and queue has been cleared")
                os.system('rm ' + str(ctx.guild.id) + '/*.opus')
                os.system('rm ' + str(ctx.guild.id) + '/*.webm')
                await settings.timers[ctx.guild.id].pause()
            else:
                await ctx.send("There is no audio to stop.")

    #The skip function allows for a user to skip a certain amount of songs ahead
    @commands.command(pass_context = True)
    async def skip(self, ctx, amount:int):

        #It checks for a voice channel
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice == None:
            await ctx.send("I am not in a voice channel")

        #And then it checks if there is music playing and if the amount of songs being skipped is less than the length of the queue
        else:
            if voice.is_playing() or voice.is_paused() and (amount <= len(settings.queues[ctx.guild.id]) and amount > 0):
                await ctx.send(f"{amount} songs have been skipped")
                print("\nSong has been skipped\n")

                #It also checks if the repeat function is on and adds those songs to the end of the queue
                #It displays what the next item of the queue is
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
                        else:
                            await ctx.send('Now playing:\n***' + title + '***')
                    elif "song" in settings.queues[ctx.guild.id][0]:
                        await ctx.send('Now playing the next item in your playlist')
                
                #It then checks if the queue is empty
                else:
                    await ctx.send("Your queue is empty")
                #it then stops the music to load the next song
                voice.stop()
            elif amount > len(settings.queues[ctx.guild.id]) and amount <= 0:
                await ctx.send("Please input a valid amount of songs to skip")
            else:
                await ctx.send("There is no music to skip.")

    #The skips function is an error function designed to just skip the default ammount of songs which is just 1
    @skip.error
    async def skips(self, ctx, error):

        #It checks for the missing error argument
        if isinstance(error, commands.MissingRequiredArgument):

            #Checks voice once again
            voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
            if voice == None:
                await ctx.send("I am not in a voice channel")
            
            #And then it skips the song similarly to the skip command
            else:
                if voice.is_playing() or voice.is_paused():
                    await ctx.send("Song has been skipped")
                    print("\nSong has been skipped\n")
                    if settings.queues[ctx.guild.id]:
                        settings.indexes[ctx.guild.id] = True
                        if settings.downloading[ctx.guild.id][1]:
                            settings.queues[ctx.guild.id].append(settings.queues[ctx.guild.id][0])
                            settings.titles[ctx.guild.id].append(settings.titles[ctx.guild.id][0])
                        if "youtube" in settings.queues[ctx.guild.id][0]:
                            title = settings.titles[ctx.guild.id][0]
                            if "playlist" in settings.queues[ctx.guild.id][0]:
                                await ctx.send('Now playing playlist:\n***' + title + '***')
                            else:
                                await ctx.send('Now playing:\n***' + title + '***')
                        elif "song" in settings.queues[ctx.guild.id][0]:
                            await ctx.send('Now playing the next item in your playlist')
                    else:
                        await ctx.send("Your queue is empty")
                    voice.stop()
                else:
                    await ctx.send("There is no music to skip.")

    #The song command allows a user to search for a song and automatically play the first search result for this song
    #The search terms for this one has to be very specific or it will not be very useful since the first result may be irrelevant
    @commands.command(pass_context = True)
    async def song(self, ctx, *, song: str):
        
        #It checks for voice
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)

        #Once it has checked for voice it searches for the song and automatically adds it to the end of the queue
        #It also starts the threaded timer if it is not downloading
        if voice != None:
            vidsearch = VideosSearch(song, limit = 1)
            settings.searches[ctx.guild.id][0] = vidsearch.result()
            if voice.is_playing() or voice.is_paused() or settings.downloading[ctx.guild.id][0] == True:
                await ctx.send('***' + settings.searches[ctx.guild.id][0]['result'][0]['title']+'\n*** has been added to the queue')
            else:
                await ctx.send('Song Selected')   
            settings.queues[ctx.guild.id].append(settings.searches[ctx.guild.id][0]['result'][0]['link'])
            settings.titles[ctx.guild.id].append(settings.searches[ctx.guild.id][0]['result'][0]['title'])
            settings.searches[ctx.guild.id][0] = ''
            if settings.downloading[ctx.guild.id][0] == False:
                await settings.timers[ctx.guild.id].start()
        else:
            await ctx.send('I am not in a voice channel')
    
    #The playlist command allows a user to search and select for a playlist of their choosing
    @commands.command(pass_context = True)
    async def playlist(self, ctx, *, playlist: str):

        #First it checks for a voice channel once again
        voice = nextcord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice != None:

            #It then checks if the user has selected a specific playlist from the search key for their server
            #If it is true, then it adds the song to the end of the queue
            #Once this is done, it adds the song to the end of the queue
            if playlist == '1' or playlist == '2' or playlist == '3' or playlist == '4' or playlist == '5':
                if settings.searches[ctx.guild.id][0] == '':
                    await ctx.send('There is currently no searched music, please search for a playlist and try again.')
                else:
                    print('successfully chose a playlist')
                    if voice.is_playing() or voice.is_paused() or settings.downloading[ctx.guild.id][0] == True:
                        if settings.searches[ctx.guild.id][1] == None:
                            await ctx.send('Playlist number ' + playlist + ' selected:\n***' + settings.searches[ctx.guild.id][0]['result'][int(playlist)-1]['title']+'*** has been added to the queue')
                        else:
                            await settings.searches[ctx.guild.id][1].edit('Playlist number ' + playlist + ' selected:\n***' + settings.searches[ctx.guild.id][0]['result'][int(playlist)-1]['title']+'*** has been added to the queue')
                    else:
                        if settings.searches[ctx.guild.id][1] == None:
                            await ctx.send('Playlist number ' + playlist + ' selected:\nNow Playing:\n***' + settings.searches[ctx.guild.id][0]['result'][int(playlist)-1]['title']+'***')
                        else:
                            await settings.searches[ctx.guild.id][1].edit('Playlist number ' + playlist + ' selected:\nNow Playing:\n***' + settings.searches[ctx.guild.id][0]['result'][int(playlist)-1]['title']+'***')
                    settings.queues[ctx.guild.id].append(settings.searches[ctx.guild.id][0]['result'][int(playlist)-1]['link'])
                    settings.titles[ctx.guild.id].append(settings.searches[ctx.guild.id][0]['result'][int(playlist)-1]['title'])
                    settings.searches[ctx.guild.id][0] = ''
                    settings.searches[ctx.guild.id][1] = ''
                    if settings.downloading[ctx.guild.id][0] == False:
                        await settings.timers[ctx.guild.id].start()

            #Then it checks if the user has put a search term, if it is, then it provides the user with the top 5 options
            #It then saves it to the search key for later use
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
    
    #The qplaylist function provides a similar function to playlist
    #This command however instead of allowing a user to quickly search for a playlist and automatically add it to the queue
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
                await settings.timers[ctx.guild.id].start()
        else:
            await ctx.send('I am not in a voice channel')

    #The showqueue function allows a user to see the queue key for their specific server
    @commands.command(pass_context = True)
    async def showqueue(self, ctx, *, msg:str=''):
        queued = ''
        counter = 0

        #First it checks if their guild id is in the queue dictionary
        if ctx.guild.id in settings.titles:

            #Once it checks that the queue is available, it generates the queue into a printable string
            for title in settings.titles[ctx.guild.id]:
                queued = queued + str(counter+1) + ': ***' + title + '***\n'
                counter+=1
            if queued == '':
                await ctx.send('There are no songs currently on queue')
            
            #It then checks the size of the queue
            #If the queue is too long to print in a text channel, it gives the user the option too be able to print it to a place of their choosing
            #If the user chooses to print it in a text channel, it prints the first 10 songs in queue
            #However, if the user chooses DM, it allows the user to see the entire queue through a DM message from the bot
            else:
                if len(queued) > 1970:
                    await ctx.send('The queue is currently too long to print')
                    queued = ''
                    if msg.lower() == 'dm':
                        await ctx.send('The queue has been sent to DM')
                        queued = '***Queue***\n\n\n\nSongs currently on queue:\n'
                        reset = 0
                        counter = 0
                        for title in settings.titles[ctx.guild.id]:
                            if reset == 20:
                                reset = 0
                                await ctx.author.send(queued)
                                queued = ''
                            queued = queued + str(counter+1) + ': ***' + title + '***\n'
                            reset += 1
                            counter += 1
                        if queued != '':
                            await ctx.author.send(queued)
                    else:    
                        for counter in range(0, 10):
                            queued = queued + str(counter+1) + ': ***' + settings.titles[ctx.guild.id][counter] + '***\n'
                        await ctx.send('The next 10 songs in queue will be printed instead:\n' + queued)
                else:
                    await ctx.send('Songs currently on queue:\n' + queued)
        else:
            await ctx.send('There is no active queue for this server')

    #The repeat function allows a user to repeat the queue
    #If the bot is in a voice channel, this function allows the user to toggle the repeat key off and on
    #This is off by default
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

    #The shuffle function allows a user to shuffle the queue
    #If the bot is in a voice channel, this function allows the user to toggle the shuffle key off and on
    #This is off by default
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
    
    #The status command allows a user to see if repeating and shuffling both are turned on or off
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

    #The remove command allows a user to remove a single song from the queue
    #This is used with the index number retrieved from the showqueue command
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

def setup(client):
    client.add_cog(Music(client))

#The queue function is what runs the entire music bot.
#This function is used to periodically check if a song is ready to be loaded up into the voice chat for playing
async def queue(ctx, client):

    #First it sets the working directory and checks if the bot is playing a song
    pwd = os.path.dirname(os.path.realpath(__file__))
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if (voice.is_playing() or voice.is_paused()):
        pass
    else:

        #It then checks if there is an active queue for an individual server
        if settings.queues[ctx.guild.id]:
            if settings.queues[ctx.guild.id][0].startswith('song'):
                source = FFmpegPCMAudio(pwd+'/'+str(ctx.guild.id)+'/'+settings.queues[ctx.guild.id][0])
            
            #It then sets up everything for the next song to play properly
            #It clears the guild directory and sets downloading to true
            else:
                settings.downloading[ctx.guild.id][0] = True
                os.system('rm ' + str(ctx.guild.id) + '/*.opus')
                os.system('rm ' + str(ctx.guild.id) + '/*.webm')

                #It then checks if shuffle is turned on and grabs the index for the next shuffle
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
                
                #It then checks if the next item is a playlist and retrieves every item in the playlist
                if "playlist" in settings.queues[ctx.guild.id][index]:
                    songlist, title = await dccommands.retrievePlaylist(settings.queues[ctx.guild.id][index], ctx)
                    voice.stop()
                    settings.queues[ctx.guild.id].pop(index)
                    settings.queues[ctx.guild.id] = songlist+settings.queues[ctx.guild.id]
                    settings.titles[ctx.guild.id].pop(index)
                    settings.titles[ctx.guild.id] = title+settings.titles[ctx.guild.id]
                
                #After that it then retrieves the next audio and if it is set to repeating, it places the song back to the end of the queue
                #It then plays the next song and sets downloading to false
                else:
                    source, title = await dccommands.retrieveAudio(settings.queues[ctx.guild.id][index], (pwd+'/'+str(ctx.guild.id)), ctx)
                    if settings.downloading[ctx.guild.id][1]:
                        settings.titles[ctx.guild.id].append(settings.titles[ctx.guild.id][index])
                        settings.queues[ctx.guild.id].append(settings.queues[ctx.guild.id][index])
                    settings.titles[ctx.guild.id].pop(index)
                    player = voice.play(source)
                    settings.queues[ctx.guild.id].pop(index)
            settings.downloading[ctx.guild.id][0] = False
        
        #If there is not an active queue, it cleans up and pauses the timer
        else:
            os.system('rm ' + str(ctx.guild.id) + '/*.opus')
            os.system('rm ' + str(ctx.guild.id) + '/*.webm')
            await settings.timers[ctx.guild.id].pause()
            print('No queued items')
