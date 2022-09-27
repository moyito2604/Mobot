#cogs.Music runs the Music slash commands for Mobot
#This file contains all of the commands associated with the Mobot Music commands

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

#The Music Command holds the definitions for all of the commands needed to run the bot
class SlashMusic(commands.Cog):

    def __init__(self, client):
        print("SlashMusic Initialized Successfully")
        self.client = client

    #The join function is a command used to join the bot to a server's voice channel
    @nextcord.slash_command(name = "join", description = "Joins the Bot to a Voice Channel")
    async def join(self, interaction : Interaction):

        #First it grabs the voice channel that the music bot is currently in that specific server
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)

        #It then checks if the author is in a voice channel currently
        #It then checks if the bot is in a voice channel and if its not, it joins the voice channel
        #It also arranges server specific dictionary keys to run the bot as well and sets up logging
        #It sets up the threaded timer to monitor the voice activity of the bot as well.
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
                settings.downloading[interaction.guild.id] = [False, False, False, False]
                settings.searches[interaction.guild.id] = ['', '']
                settings.indexes[interaction.guild.id] = False
                channel = interaction.user.voice.channel
                voice = await channel.connect()
                await interaction.send('Successfully Joined the ' + str(channel) + ' voice channel')
                print('Successfully Joined the ' + str(channel) + ' voice channel')
                settings.timers[interaction.guild.id] = Threaded_timer.RepeatedTimer(1, Music.queue, interaction, self.client)
                settings.channels[interaction.guild.id] = interaction
                if os.path.exists(f'logs/{interaction.guild.name}_logs.log'):
                    os.remove(f'logs/{interaction.guild.name}_logs.log')
            
            #If the bot is already currently in a voice channel, sends a message saying its already connected
            else:
                await interaction.send("I am already connected")
        #It also checks if the user is not in a voice channel and reminds the user that they need to be in a voice channel for the bot to join.
        else:
            print('User is not in a voice channel')
            await interaction.send("You are not in a voice channel, you must be in a voice channel for me to join")

    #The leave command is what allows the bot to leave a voice channel once the user is done using it in a specific server
    @nextcord.slash_command(name = "leave", description = "Leaves the bot from a voice channel")
    async def leave(self, interaction : Interaction):
        pwd = os.path.dirname(os.path.realpath(__file__))

        #First it grabs the voice channel that the bot is currently in
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        
        #It then checks if the bot is in a valid voice channel and if its not, it sends a message saying that its not in a VC
        #It then cleans up dictionary keys that are used to run the bot and removes directories
        if (interaction.guild.voice_client):
            shutil.rmtree(pwd + '/' + str(interaction.guild.id))
            print('directory ' + str(interaction.guild.id) + ' has been deleted')
            await settings.timers[interaction.guild.id].stop()
            settings.timers.pop(interaction.guild.id)
            settings.queues.pop(interaction.guild.id)
            settings.searches.pop(interaction.guild.id)
            settings.titles.pop(interaction.guild.id)
            settings.channels.pop(interaction.guild.id)
            print('Successfully left the voice Channel')
            await voice.disconnect()
            await interaction.send("Left the voice channel")
        else:
            await interaction.send("I am not in a voice channel")
        
    #This command is the most versatile command used for Mobot
    #It allows you play a song from a youtube link, load a playlist from a youtube link, allows you to search for a song on youtube
    #It also allows a user to select a song to play from the search results
    #It can also be used to join the bot automatically and play a song
    @nextcord.slash_command(name = "play", description = "Allows the bot to play music from a youtube link or search")
    async def play(self, interaction : Interaction, url:str=' '):

        #First it grabs the voice channel to check if the bot is in a voice channel
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if url != ' ':

            #It then checks if the bot is in a Voice channel and if not, it sets it up similarly to the join command
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
                    settings.downloading[interaction.guild.id] = [False, False, False, False]
                    settings.searches[interaction.guild.id] = ['', '']
                    settings.indexes[interaction.guild.id] = False
                    channel = interaction.user.voice.channel
                    voice = await channel.connect()
                    await interaction.send('Successfully Joined the ' + str(channel) + ' voice channel')
                    print('Successfully Joined the ' + str(channel) + ' voice channel')
                    settings.timers[interaction.guild.id] = Threaded_timer.RepeatedTimer(1, Music.queue, interaction, self.client)
                    settings.channels[interaction.guild.id] = interaction
                    if os.path.exists(f'logs/{interaction.guild.name}_logs.log'):
                        os.remove(f'logs/{interaction.guild.name}_logs.log')
            
            #It then verifies that that the bot is in a Voice Channel for it to be used properly
            if voice != None:

                #It then checks if a youtube link was inputted or a search prompt. It then also checks if a youtube link is a playlist or not
                #it then starts the threaded timer
                if 'https://www.youtube.com' in url or 'https://youtu.be' in url or 'https://youtube.com' in url:
                    settings.queues[interaction.guild.id].append(url)
                    failed = False
                    with yt_dlp.YoutubeDL() as ydl:
                        try:
                            info = ydl.extract_info(url, download=False, process=False)
                            title = info.get('title', None)
                            settings.titles[interaction.guild.id].append(title)
                        except:
                            failed = True
                            settings.queues[interaction.guild.id].pop()
                            if voice.is_playing() or voice.is_paused() or settings.downloading[interaction.guild.id][0] == True:
                                await interaction.send("The current Track has failed to be added to the queue")
                            else:
                                await interaction.send("The current Track has failed to play")
                    if not failed:
                        if voice.is_playing() or voice.is_paused() or settings.downloading[interaction.guild.id][0] == True:
                            if "playlist" in url:
                                await interaction.send('Playlist ***' + title + '*** has been added to the queue')
                            else:
                                await interaction.send('***' + title + '*** has been added to the queue')
                        else:
                            await interaction.send('Retrieving from source')
                            if "playlist" in url:
                                await interaction.send('Now playing playlist:\n***' + title + '***')
                            #else:
                                #await interaction.send('Now playing:\n***' + title + '***')
                    if settings.downloading[interaction.guild.id][0] == False:
                        await settings.timers[interaction.guild.id].start()
                
                #Once it checks that its not a youtube link, it checks if it is selecting a song from the search function
                #Once it verifies that it is a search, it then selects the song and adds it to the queue and clears the search
                #It then starts the timer
                elif url == '1' or url == '2' or url == '3' or url == '4' or url == '5':
                    if settings.searches[interaction.guild.id][0] == '':
                        await interaction.send('There is currently no searched music, please search for a song and try again.')
                    else:
                        print('successfully chose a song')
                        if voice.is_playing() or voice.is_paused() or settings.downloading[interaction.guild.id][0] == True:
                            msgs = 'Song number ' + url + ' selected:\n***' + settings.searches[interaction.guild.id][0]['result'][int(url)-1]['title']+'*** has been added to the queue'
                            await interaction.send(msgs)
                        else:
                            msgs = 'Song number ' + url + ' selected:\n'
                            #Now Playing:\n***' + settings.searches[interaction.guild.id][0]['result'][int(url)-1]['title']+'***'
                            await interaction.send(msgs)
                        settings.queues[interaction.guild.id].append(settings.searches[interaction.guild.id][0]['result'][int(url)-1]['link'])
                        settings.titles[interaction.guild.id].append(settings.searches[interaction.guild.id][0]['result'][int(url)-1]['title'])
                        settings.searches[interaction.guild.id][0] = ''
                        settings.searches[interaction.guild.id][1] = ''
                        if settings.downloading[interaction.guild.id][0] == False:
                            await settings.timers[interaction.guild.id].start()
                
                #It then checks if a video search is being performed
                #Once it confirms that its a video search, it saves the key for the search for later use
                else:
                    vidsearch = VideosSearch(url, limit = 5)
                    settings.searches[interaction.guild.id][0] = vidsearch.result()
                    msg = await interaction.send('Please select a song from the following results:\nSyntax:\n' + extensions + 'play 3\n' + '1: ***' + settings.searches[interaction.guild.id][0]['result'][0]['title']+'***\n'
                    '2: ***' + settings.searches[interaction.guild.id][0]['result'][1]['title']+'***\n'+
                    '3: ***' + settings.searches[interaction.guild.id][0]['result'][2]['title']+'***\n'+
                    '4: ***' + settings.searches[interaction.guild.id][0]['result'][3]['title']+'***\n'+
                    '5: ***' + settings.searches[interaction.guild.id][0]['result'][4]['title']+'***\n')
                    settings.searches[interaction.guild.id][1] = msg
            
            #This then checks if the bot is not in a voice channel and if its not, it sends a message reminding a user to join the voice channel to bring the bot in
            else:
                await interaction.send("You are not in a voice channel, you must be in a voice channel for me to join")
        else:
            #It then also checks if an optional argument was inputted, if not, it just plays any music that has been paused
            if voice == None:
                await interaction.send("I am not in a voice channel")
            else:
                if voice.is_paused():
                    voice.resume()
                    await interaction.send("Music is playing")
                else:
                    await interaction.send("There is no paused audio in the voice channel.")

    #The pause function is pretty self explanatory
    @nextcord.slash_command(name = "pause", description = "pauses any music currently playing in the voice channel")
    async def pause(self, interaction : Interaction):
        
        #It grabs the voice channel and checks if the bot is in
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice == None:
            await interaction.send("I am not in a voice channel")

        #and if it is, it checks if there is any music playing, if it is, it pauses the music
        #if it is not playing anything, it sends a message stating that there is no music to pause
        else:
            if voice.is_playing():
                voice.pause()
                await interaction.send("Music has been paused")
            else:
                await interaction.send("There is no audio playing in the voice channel.")

    #The stop command is also self-explanatory, it allows the user stop any audio playing from the bot
    #It also allows the bot to cleanup the dictionary keys that run the bot
    @nextcord.slash_command(name = "stop", description = "stops the music in a voice channel and clears the queue")
    async def stop(self, interaction : Interaction):

        #First it checks for a voice channel
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice == None:
            await interaction.send("I am not in a voice channel")

        #Then it stops the music and cleans up
        #If there is no music playing, it states that there is no audio currently playing
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

    #The skip function allows for a user to skip a certain amount of songs ahead
    @nextcord.slash_command(name = "skip", description = "skips the current song")
    async def skip(self, interaction : Interaction, amount:int=1):
        
        #It checks for a voice channel
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice == None:
            await interaction.send("I am not in a voice channel")

        #And then it checks if there is music playing and if the amount of songs being skipped is less than the length of the queue
        else:
            if voice.is_playing() or voice.is_paused() and (amount <= len(settings.queues[interaction.guild.id]) and amount > 0):
                await interaction.send(f"{amount} songs have been skipped")
                print("\nSong has been skipped\n")

                #It also checks if the repeat function is on and adds those songs to the end of the queue
                #It displays what the next item of the queue is
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
                        #else:
                            #await interaction.send('Now playing:\n***' + title + '***')
                    elif "song" in settings.queues[interaction.guild.id][0]:
                        await interaction.send('Now playing the next item in your playlist')
                
                #It then checks if the queue is empty
                else:
                    await interaction.send("Your queue is empty")
                #it then stops the music to load the next song
                voice.stop()
            elif amount > len(settings.queues[interaction.guild.id]) and amount <= 0:
                await interaction.send("Please input a valid amount of songs to skip")
            else:
                await interaction.send("There is no music to skip.")

    #The song command allows a user to search for a song and automatically play the first search result for this song
    #The search terms for this one has to be very specific or it will not be very useful since the first result may be irrelevant
    @nextcord.slash_command(name = "song", description = "allows the user to search for a song and add it to the queue")
    async def song(self, interaction: Interaction, song: str):

        #It checks for voice
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        
        #Once it has checked for voice it searches for the song and automatically adds it to the end of the queue
        #It also starts the threaded timer if it is not downloading
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

    #The playlist command allows a user to search and select for a playlist of their choosing
    @nextcord.slash_command(name = "playlist", description = "allows a user to search for and select a playlist and add it to the queue")
    async def playlist(self, interaction : Interaction, playlist: str):

        #First it checks for a voice channel once again
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice != None:

            #It then checks if the user has selected a specific playlist from the search key for their server
            #If it is true, then it adds the song to the end of the queue
            #Once this is done, it adds the song to the end of the queue
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
            
            #Then it checks if the user has put a search term, if it is, then it provides the user with the top 5 options
            #It then saves it to the search key for later use
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
    
    #The qplaylist function provides a similar function to playlist
    #This command however instead of allowing a user to quickly search for a playlist and automatically add it to the queue
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

    #The showqueue function allows a user to see the queue key for their specific server
    @nextcord.slash_command(name = "showqueue", description = "allows the user to view the current queue")
    async def showqueue(self, interaction: Interaction, msg = SlashOption(name="printing",
    description="Allows the user to send to either print queue to DM or channel", 
    choices={"Channel":"channel", "DM":"dm"})):
        queued = ''
        counter = 0

        #First it checks if their guild id is in the queue dictionary
        if interaction.guild.id in settings.titles:

            #Once it checks that the queue is available, it generates the queue into a printable string
            for title in settings.titles[interaction.guild.id]:
                queued = queued + str(counter+1) + ': ***' + title + '***\n'
                counter+=1
            if queued == '':
                await interaction.send('There are no songs currently on queue')
            
            #It then checks the size of the queue
            #If the queue is too long to print in a text channel, it gives the user the option too be able to print it to a place of their choosing
            #If the user chooses to print it in a text channel, it prints the first 10 songs in queue
            #However, if the user chooses DM, it allows the user to see the entire queue through a DM message from the bot
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
    
    #The repeat function allows a user to repeat the queue
    #If the bot is in a voice channel, this function allows the user to toggle the repeat key off and on
    #This is off by default
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

    #The shuffle function allows a user to shuffle the queue
    #If the bot is in a voice channel, this function allows the user to toggle the shuffle key off and on
    #This is off by default
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

    #The status command allows a user to see if repeating and shuffling both are turned on or off
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
            if settings.downloading[interaction.guild.id][3]:
                await interaction.send('Normalized audio is turned on')
            else:
                await interaction.send('Normalized audio is turned off')
        else:
            await interaction.send('I am not in a voice channel')

    #The remove command allows a user to remove a single song from the queue
    #This is used with the index number retrieved from the showqueue command
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
    
    #The normalize command allows a user to normalize all audio playing through the bot to a voice channel
    #It is a toggle that then signals the program to normalize all audio
    #@nextcord.slash_command(name = "normalize", description = "allows a user the option to normalize all audio passing through the bot")
    #async def normalize(self, interaction : Interaction):
        #if interaction.guild.id in settings.downloading:
            #if settings.downloading[interaction.guild.id][3]:
                #settings.downloading[interaction.guild.id][3] = False
                #await interaction.send('Normalzing has been turned off')
            #else:
                #settings.downloading[interaction.guild.id][3] = True
                #await interaction.send('Normalizing has been turned on')
        #else:
            #await interaction.send('I am not in a voice channel')

def setup(client):
    client.add_cog(SlashMusic(client))
