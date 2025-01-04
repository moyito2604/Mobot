# cogs.Music runs the Music slash commands for Mobot
# This file contains all the commands associated with the Mobot Music commands
import asyncio
from asyncio import TimeoutError
import math
import os
import time
import jsonbuilder
import nextcord
import scrapetube
from nextcord.ext import commands, tasks
from nextcord import Interaction
from nextcord.errors import Forbidden
import os.path
import pytube
# from pytube import helpers
from pytube.exceptions import RegexMatchError, VideoUnavailable, VideoPrivate, VideoRegionBlocked, MembersOnly, PytubeError
import yt_dlp
import random
import shutil
import settings
import Dependencies.Functions as Functions
import Dependencies.Buttons as Buttons
from Dependencies.Scrape import get_video

color = Functions.Color


# The Music Command holds the definitions for all the commands needed to run the bot
class SlashMusic(commands.Cog):

    def __init__(self, client):
        print("SlashMusic Initialized Successfully")
        self.client = client
        self.timer.start()
        # if settings.proxy != "None":
        #     proxy_handler = {"http": settings.proxy, "https": settings.proxy}
        #     helpers.install_proxy(proxy_handler)

    # This nextcord task holds the timer for every single server. It ensures one instance of queue is run in every
    # server once every second
    @tasks.loop(seconds=1)
    async def timer(self):

        # First, it waits for the bot to be ready
        await self.client.wait_until_ready()

        # Then it loops through all servers with active bots in the voice client. It then checks if the Timer variable
        # is active, and it creates an instance of the queue to execute
        for voice in self.client.voice_clients:
            if settings.env_vars.get(voice.guild.id, None):
                if settings.env_vars[voice.guild.id]['Active']:
                    settings.env_vars[voice.guild.id]['Timer'] = (
                        asyncio.ensure_future(Functions.queue(settings.env_vars[voice.guild.id]['ctx'], self.client)))

    # The join function is a command used to join the bot to a server's voice channel
    @nextcord.slash_command(name="join", description="Joins the Bot to a Voice Channel")
    async def join(self, interaction: Interaction):

        # First it grabs the voice channel that the music bot is currently in that specific server
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)

        # It then checks if the author is in a voice channel currently
        # It then checks if the bot is in a voice channel and if it's not, it joins the voice channel
        # It also arranges server specific dictionary keys to run the bot as well and sets up logging
        # It sets up the threaded timer to monitor the voice activity of the bot as well.
        if interaction.user.voice:
            if voice is None:
                currdir = settings.pwd + '/Dependencies/'
                if os.path.isdir(currdir + '/' + str(interaction.guild.id)):
                    shutil.rmtree(currdir + '/' + str(interaction.guild.id))
                    print('Directory ' + str(interaction.guild.id) + ' has been deleted')
                os.mkdir(currdir + '/' + str(interaction.guild.id))
                print('Directory ' + str(interaction.guild.id) + ' has been created')
                settings.queues[interaction.guild.id] = []
                settings.env_vars[interaction.guild.id] = {"Downloading": False, "Repeat": False,
                                                           "ctx": interaction, "Active": False}
                settings.current[interaction.guild.id] = {}
                channel = interaction.user.voice.channel

                # Tests to ensure there is permission to join voice channel and to send a message in the current channel
                try:
                    await interaction.response.defer()
                    voice = await channel.connect(timeout=5)
                except TimeoutError:
                    try:
                        await interaction.send("Failed to connect to the voice channel")
                    except Forbidden:
                        print(f"Failed to connect to voice channel and send a message in {color.BLUE}{color.BOLD}"
                              f"{interaction.guild.name}{color.END}")
                    return

                await interaction.send('Successfully Joined the ' + str(channel) + ' voice channel')
                print(
                    f"Successfully Joined the {color.PURPLE}{color.BOLD}{str(channel)}{color.END} voice channel in the"
                    f" server {color.BLUE}{color.BOLD}{interaction.guild.name}{color.END}")
                settings.channels[interaction.guild.id] = interaction
                if os.path.exists(f'logs/{interaction.guild.name}_logs.log'):
                    os.remove(f'logs/{interaction.guild.name}_logs.log')

            # If the bot is already currently in a voice channel, sends a message saying its already connected
            else:
                await interaction.send("I am already connected")
        # It also checks if the user is not in a voice channel and reminds the user that they need to be in a voice
        # channel for the bot to join.
        else:
            await interaction.send("You are not in a voice channel, you must be in a voice channel for me to join")

    # The leave command is what allows the bot to leave a voice channel once the user is done using it in a specific
    # server
    @nextcord.slash_command(name="leave", description="Leaves the bot from a voice channel")
    async def leave(self, interaction: Interaction):
        currdir = settings.pwd + '/Dependencies/'

        # First it grabs the voice channel that the bot is currently in
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)

        # It then checks if the bot is in a valid voice channel and if it's not, it sends a message saying that it's
        # not in a VC It then cleans up dictionary keys that are used to run the bot and removes directories
        if interaction.guild.voice_client:
            shutil.rmtree(currdir + '/' + str(interaction.guild.id))
            print('Directory ' + str(interaction.guild.id) + ' has been deleted')
            await Functions.stopTimer(interaction.guild.id)
            settings.queues.pop(interaction.guild.id, None)
            settings.channels.pop(interaction.guild.id, None)
            settings.current.pop(interaction.guild.id, None)
            settings.env_vars.pop(interaction.guild.id, None)
            print(f"Successfully left the voice Channel in the server {color.BLUE}{color.BOLD}{interaction.guild.name}"
                  f"{color.END}")
            await voice.disconnect()
            await interaction.send("Left the voice channel")
        else:
            await interaction.send("I am not in a voice channel")

    # This command is the most versatile command used for Mobot It allows you to play a song from a YouTube link,
    # load a playlist from a YouTube link, allows you to search for a song on YouTube It also allows a user to select
    # a song to play from the search results It can also be used to join the bot automatically and play a song
    @nextcord.slash_command(name="play",
                            description="Allows the bot to play music from a link or search")
    async def play(self, interaction: Interaction, song: str = ' '):
        url = song
        # First it grabs the voice channel to check if the bot is in a voice channel
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if url != ' ':

            # It then checks if the bot is in a Voice channel and if not, it sets it up similarly to the join command
            if interaction.user.voice:
                if voice is None:
                    currdir = settings.pwd + '/Dependencies/'
                    if os.path.isdir(currdir + '/' + str(interaction.guild.id)):
                        shutil.rmtree(currdir + '/' + str(interaction.guild.id))
                        print('Directory ' + str(interaction.guild.id) + ' has been deleted')
                    os.mkdir(currdir + '/' + str(interaction.guild.id))
                    print('Directory ' + str(interaction.guild.id) + ' has been created')
                    settings.queues[interaction.guild.id] = []
                    settings.env_vars[interaction.guild.id] = {"Downloading": False, "Repeat": False,
                                                               "ctx": interaction, "Active": False}
                    settings.current[interaction.guild.id] = {}
                    channel = interaction.user.voice.channel

                    # Tests to ensure there is permission to join the voice channel and send a message in the channel
                    try:
                        await interaction.response.defer()
                        voice = await channel.connect(timeout=5)
                    except TimeoutError:
                        try:
                            await interaction.send("Failed to connect to the voice channel")
                        except Forbidden:
                            print(f"Failed to connect to voice channel and send a message in {color.BLUE}{color.BOLD}"
                                  f"{interaction.guild.name}{color.END}")
                        return

                    await interaction.send('Successfully Joined the ' + str(channel) + ' voice channel')
                    print(f"Successfully Joined the {color.PURPLE}{color.BOLD}{str(channel)}{color.END} voice channel "
                          f"in the server {color.BLUE}{color.BOLD}{interaction.guild.name}{color.END}")
                    settings.channels[interaction.guild.id] = interaction
                    if os.path.exists(f'logs/{interaction.guild.name}_logs.log'):
                        os.remove(f'logs/{interaction.guild.name}_logs.log')

            # It then verifies that the bot is in a Voice Channel for it to be used properly
            if voice is not None:

                # It then checks if a YouTube link was inputted or a search prompt. It then also checks if a YouTube
                # link is a playlist or not it then starts the threaded timer
                if Functions.checkurl(url):

                    if not interaction.response.is_done():
                        await interaction.response.defer()

                    # Retrieves current event loop to run synchronous functions
                    loop = asyncio.get_event_loop()

                    # Variables that Define if the given URL is a video or playlist
                    isVideo = True
                    isPlaylist = True
                    videoid = ""

                    if "youtube" in url or "youtu.be" in url:

                        # Tests to see if it's a YouTube Video
                        try:
                            video = await loop.run_in_executor(None, pytube.YouTube, url)
                            video.check_availability()
                            videoid = video.video_id
                            videodict = {"avatar": interaction.user.display_avatar.url, "title": video.title,
                                         "duration": time.strftime("%H:%M:%S", time.gmtime(video.length)),
                                         "url": "https://www.youtube.com/watch?v=" + video.video_id,
                                         "user": interaction.user.mention, "name": interaction.user.display_name}

                        # If it's not a YouTube video, it will fail with regex
                        except RegexMatchError:
                            isVideo = False
                        except VideoUnavailable or VideoPrivate or VideoRegionBlocked or MembersOnly:
                            await interaction.send("Track requested is Private or Unavailable")
                            return

                        # If it fails to extract info using pytube, then it attempts to grab the most information using
                        # Scrapetube
                        except PytubeError:
                            print(f"Error Extracting with Pytube in {color.BLUE}{color.BOLD}{interaction.guild.name}"
                                  f"{color.END}, attempting to extract information using scrapetube")
                            video = get_video(videoid)
                            videodict = {"avatar": interaction.user.display_avatar.url,
                                         "title": video['title']['runs'][0]['text'], "duration": "N/A",
                                         "url": "https://www.youtube.com/watch?v=" + videoid,
                                         "user": interaction.user.mention, "name": interaction.user.display_name}

                        # Tests to see if it's a YouTube Playlist:
                        try:
                            playlist = await loop.run_in_executor(None, pytube.Playlist, url)
                            playlistdict = {"items": playlist.length, "url": playlist.playlist_url,
                                            "user": interaction.user.mention, "name": interaction.user.display_name,
                                            "avatar": interaction.user.display_avatar.url, "title": playlist.title}
                        except:
                            isPlaylist = False

                        # If neither condition applies, the video or playlist is not playable
                        if not isVideo and not isPlaylist:
                            await interaction.send("The current Track has failed to be added to the queue")
                            return

                    else:

                        # If the selected video isn't from YouTube, a general extractor will be used instead
                        with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
                            try:
                                info = await loop.run_in_executor(None, lambda: ydl.extract_info(url,
                                                                                                 download=False,
                                                                                                 process=False))
                                title = info.get('title', None)
                                times = "N/A"
                                if "duration" in info:
                                    times = time.strftime("%H:%M:%S", time.gmtime(info['duration']))
                                videodict = {"duration": times, "url": url, "user": interaction.user.mention,
                                             "name": interaction.user.display_name,
                                             "avatar": interaction.user.display_avatar.url, "title": title}
                                settings.queues[interaction.guild.id].append(videodict)
                                await interaction.send('***' + title + '*** has been added to the queue')
                                print(f"Successfully added {color.RED}{color.BOLD}{title}{color.END} to the queue for "
                                      f"{color.BLUE}{color.BOLD}{interaction.guild.name}{color.END}")
                                if not settings.env_vars[interaction.guild.id]['Downloading']:
                                    settings.env_vars[interaction.guild.id]['Active'] = True
                                return
                            except:
                                if voice.is_playing() or voice.is_paused() or settings.env_vars[interaction.guild.id]['Downloading']:
                                    await interaction.send("The current Track has failed to be added to the queue")
                                else:
                                    await interaction.send("The current Track has failed to play")
                                return

                    # If the bot detects a playlist and a video, then it will ask the user which one it wants
                    if isVideo and isPlaylist:
                        embed = nextcord.Embed(title="**Playlist Detected**")
                        embed.add_field(name="",
                                        value="The link previously placed has a reference to a playlist and a "
                                              "song. Please specify if the song or playlist is needed")
                        view = Buttons.playlistSelectButton()
                        await interaction.send(embed=embed, ephemeral=True, view=view, delete_after=20)
                        await view.wait()
                        if view.value is None:
                            return
                        elif view.value == 1:
                            settings.queues[interaction.guild.id].append(playlistdict)
                            await interaction.send('Playlist ***' + playlistdict['title'] +
                                                   '*** has been added to the queue')
                            title = playlistdict['title']
                        elif view.value == 2:
                            settings.queues[interaction.guild.id].append(videodict)
                            await interaction.send('***' + videodict['title'] + '*** has been added to the queue')
                            title = videodict['title']

                    # If it's a video, it will be added to the queue
                    elif not isVideo and isPlaylist:
                        settings.queues[interaction.guild.id].append(playlistdict)
                        await interaction.send('Playlist ***' + playlistdict['title'] +
                                               '*** has been added to the queue')
                        title = playlistdict['title']

                    # If it's a playlist, it will be added to the queue
                    elif isVideo and not isPlaylist:
                        settings.queues[interaction.guild.id].append(videodict)
                        await interaction.send('***' + videodict['title'] + '*** has been added to the queue')
                        title = videodict['title']

                    print(f"Successfully added {color.RED}{color.BOLD}{title}{color.END} to the queue for "
                          f"{color.BLUE}{color.BOLD}{interaction.guild.name}{color.END}")

                    # It then activates the timer if there isn't a song currently downloading
                    if not settings.env_vars[interaction.guild.id]['Downloading']:
                        settings.env_vars[interaction.guild.id]['Active'] = True

                # It then checks if a video search is being performed
                else:

                    if not interaction.response.is_done():
                        await interaction.response.defer()

                    # Generates a search object
                    loop = asyncio.get_event_loop()
                    vidsearch = await loop.run_in_executor(None, lambda: scrapetube.get_search(query=url, limit=5))

                    search = []
                    for video in vidsearch:
                        search.append(video)

                    # It generates the buttons necessary for the search select
                    view = Buttons.searchButton()
                    embed = nextcord.Embed(title="Search Results")
                    for counter, result in enumerate(search):
                        if result.get("lengthText", None):
                            embed.add_field(name=f"{counter + 1}: ***{result['title']['runs'][0]['text']}***",
                                            value=f"Duration: {result['lengthText']['simpleText']}",
                                            inline=False)
                        else:
                            embed.add_field(name=f"{counter + 1}: ***{result['title']['runs'][0]['text']}***",
                                            value=f"Duration: N/A",
                                            inline=False)
                    await interaction.send(embed=embed, ephemeral=True, view=view, delete_after=20)
                    await view.wait()
                    if view.value is None:
                        return

                    # Once the user inputs the value, it is then saved to the queue
                    else:
                        await interaction.send('Song number ' + str(view.value) + ' selected:\n***' +
                                               search[int(view.value) - 1]['title']['runs'][0]['text'] +
                                               '*** has been added to the queue', ephemeral=True)
                        temp = {'url': 'https://www.youtube.com/watch?v=' + search[int(view.value) - 1]['videoId'],
                                'user': interaction.user.mention, 'name': interaction.user.display_name,
                                'avatar': interaction.user.display_avatar.url,
                                'duration': Functions.timetostr(search[int(view.value) - 1]['lengthText']['simpleText']),
                                'title': search[int(view.value) - 1]['title']['runs'][0]['text']}
                        settings.queues[interaction.guild.id].append(temp)
                        if not settings.env_vars[interaction.guild.id]['Downloading']:
                            settings.env_vars[interaction.guild.id]['Active'] = True
                        print(
                            f"Successfully added {color.RED}{color.BOLD}"
                            f"{search[int(view.value) - 1]['title']['runs'][0]['text']}{color.END} "
                            f"to the queue for {color.BLUE}{color.BOLD}{interaction.guild.name}{color.END}")

            # This then checks if the bot is not in a voice channel and if it's not, it sends a message reminding a
            # user to join the voice channel to bring the bot in
            else:
                await interaction.send("You are not in a voice channel, you must be in a voice channel for me to join")
        else:
            # It then also checks if an optional argument was inputted, if not, it just plays any music that has been
            # paused
            if voice is None:
                await interaction.send("I am not in a voice channel")
            else:
                if voice.is_paused():
                    voice.resume()
                    await interaction.send("Music is playing")
                else:
                    await interaction.send("There is no paused audio in the voice channel.")

    # The pause function is pretty self-explanatory
    @nextcord.slash_command(name="pause", description="Pauses any music currently playing in the voice channel")
    async def pause(self, interaction: Interaction):

        # It grabs the voice channel and checks if the bot is in
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice is None:
            await interaction.send("I am not in a voice channel")

        # and if it is, it checks if there is any music playing, if it is, it pauses the music
        # if it is not playing anything, it sends a message stating that there is no music to pause
        else:
            if voice.is_playing():
                voice.pause()
                await interaction.send("Music has been paused")
            else:
                await interaction.send("There is no audio playing in the voice channel.")

    # The stop command is also self-explanatory, it allows the user stop any audio playing from the bot
    # It also allows the bot to clean up the dictionary keys that run the bot
    @nextcord.slash_command(name="stop", description="Stops the music in a voice channel and clears the queue")
    async def stop(self, interaction: Interaction):

        # First it checks for a voice channel
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice is None:
            await interaction.send("I am not in a voice channel")

        # Then it stops the music and cleans up
        # If there is no music playing, it states that there is no audio currently playing
        else:
            if voice.is_playing() or voice.is_paused():
                settings.queues[interaction.guild.id] = []
                voice.stop()
                await interaction.send("Music has been stopped and queue has been cleared")
                print(f"Music has been stopped and queue has been cleared for {color.BLUE}{color.BOLD}"
                      f"{interaction.guild.name}{color.END}")
                settings.env_vars[interaction.guild.id]['Active'] = False
            else:
                await interaction.send("There is no audio to stop.")

    # The skip function allows for a user to skip a certain amount of songs ahead
    @nextcord.slash_command(name="skip", description="Skips the current song or a user-defined amount of songs")
    async def skip(self, interaction: Interaction, amount: int = 1):

        # It checks for a voice channel
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice is None:
            await interaction.send("I am not in a voice channel")

        # And then it checks if there is music playing and if the amount of songs being skipped is less than the
        # length of the queue
        else:
            if (voice.is_playing() or voice.is_paused()) and (len(settings.queues[interaction.guild.id]) >= amount > 0):
                await interaction.send(f"{amount} songs have been skipped")

                # It also checks if the repeat function is on and adds those songs to the end of the queue
                # It displays what the next item of the queue is
                for counter in range(1, amount):
                    if settings.env_vars[interaction.guild.id]['Repeat']:
                        settings.queues[interaction.guild.id].append(settings.queues[interaction.guild.id][0])
                    settings.queues[interaction.guild.id].pop(0)
                if settings.queues[interaction.guild.id]:
                    if "youtube" in settings.queues[interaction.guild.id][0]['url']:
                        title = settings.queues[interaction.guild.id][0]['title']
                        if "playlist" in settings.queues[interaction.guild.id][0]['url']:
                            await interaction.send('Now playing playlist:\n***' + title + '***')

                # It then checks if the queue is empty
                else:
                    await interaction.send("Your queue is empty")
                # it then stops the music to load the next song
                voice.stop()
            elif not (len(settings.queues[interaction.guild.id]) >= amount > 0):
                items = len(settings.queues[interaction.guild.id])
                await interaction.send(f"Please input a valid amount of songs to skip. There are {items} items in queue")
            else:
                await interaction.send("There is no music to skip.")

    # The song command allows a user to search for a song and automatically play the first search result for this
    # song The search terms for this one has to be very specific, or it will not be very useful since the first result
    # may be irrelevant
    @nextcord.slash_command(name="song",
                            description="Allows the user to search for a song and automatically adds it to the queue")
    async def song(self, interaction: Interaction, song: str):

        # It checks for voice
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)

        # Once it has checked for voice it searches for the song and automatically adds it to the end of the queue
        # It also starts the threaded timer if it is not downloading
        if voice is not None:

            await interaction.response.defer()

            loop = asyncio.get_event_loop()
            vidsearch = await loop.run_in_executor(None, lambda: scrapetube.get_search(query=song, limit=1))

            search = []
            for video in vidsearch:
                search.append(video)

            await interaction.send('***' + search[0]['title']['runs'][0]['text'] + '*** has been added to the queue',
                                   ephemeral=True)
            temp = {'url': 'https://www.youtube.com/watch?v=' + search[0]['videoId'], 'user': interaction.user.mention,
                    'name': interaction.user.display_name, 'avatar': interaction.user.display_avatar.url,
                    'duration': Functions.timetostr(search[0]['lengthText']['simpleText']),
                    'title': search[0]['title']['runs'][0]['text']}
            settings.queues[interaction.guild.id].append(temp)
            if not settings.env_vars[interaction.guild.id]['Downloading']:
                settings.env_vars[interaction.guild.id]['Active'] = True
            print(f"Successfully added {color.RED}{color.BOLD}{search[0]['title']['runs'][0]['text']}{color.END} to the"
                  f" queue for {color.BLUE}{color.BOLD}{interaction.guild.name}{color.END}")
        else:
            await interaction.response.send_message('I am not in a voice channel')

    # The playlist command allows a user to search and select for a playlist of their choosing
    @nextcord.slash_command(name="playlist",
                            description="Allows a user to search for and select a playlist and add it to the queue")
    async def playlist(self, interaction: Interaction, playlist: str):

        # First it checks for a voice channel once again
        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice is not None:

            # Defers Response until it is done
            await interaction.response.defer()

            # Then it checks if the user has put a search term, if it is, then it provides the user with the top 5
            # options.
            loop = asyncio.get_event_loop()
            vidsearch = await loop.run_in_executor(None, lambda: scrapetube.get_search(query=playlist, limit=5,
                                                                                       results_type="playlist"))

            search = []
            for video in vidsearch:
                search.append(video)

            # It then generates the buttons for selection
            view = Buttons.searchButton()
            embed = nextcord.Embed(title="Search Results")
            for counter, result in enumerate(search):
                embed.add_field(name=f"{counter + 1}: ***{result['title']['simpleText']}***",
                                value=f"Playlist Items: {result['videoCount']}",
                                inline=False)
            await interaction.send(embed=embed, ephemeral=True, view=view, delete_after=20)
            await view.wait()
            if view.value is None:
                return

            # Once that's done, it saves it to the queue
            else:
                await interaction.send('Playlist number ' + playlist + ' selected:\n***' +
                                       search[int(view.value) - 1]['title']['simpleText'] +
                                       '*** has been added to the queue', ephemeral=True)
                temp = {'url': "https://www.youtube.com/playlist?list=" + search[int(view.value - 1)]['playlistId'],
                        'user': interaction.user.mention, 'name': interaction.user.display_name,
                        'avatar': interaction.user.display_avatar.url, 'items': search[int(view.value - 1)]['videoCount'],
                        'title': search[int(view.value - 1)]['title']['simpleText']}
                settings.queues[interaction.guild.id].append(temp)
                if not settings.env_vars[interaction.guild.id]['Downloading']:
                    settings.env_vars[interaction.guild.id]['Active'] = True
                print(
                    f"Successfully added playlist {color.RED}{color.BOLD}{search[int(view.value) - 1]['title']['simpleText']}"
                    f"{color.END} to the queue for {color.BLUE}{color.BOLD}{interaction.guild.name}{color.END}")

        else:
            await interaction.send('I am not in a voice channel')

    # The qplaylist function provides a similar function to playlist This command however instead of allowing a user
    # to quickly search for a playlist and automatically add it to the queue
    @nextcord.slash_command(name="qplaylist",
                            description="Allows the user to search for a playlist and automatically adds it to the queue")
    async def qplaylist(self, interaction: Interaction, playlist: str):

        voice = nextcord.utils.get(self.client.voice_clients, guild=interaction.guild)

        if voice is not None:

            # Defers response until done
            await interaction.response.defer()

            # A search object is generated with one result required
            loop = asyncio.get_event_loop()
            vidsearch = await loop.run_in_executor(None, lambda: scrapetube.get_search(query=playlist, limit=1,
                                                                                       results_type="playlist"))

            search = []
            for video in vidsearch:
                search.append(video)

            # The playlist item is added into the queue
            await interaction.send('***' + search[0]['title']['simpleText'] + '*** has been added to the queue\n'
                                   'Size: ' + search[0]['videoCount'], ephemeral=True)
            temp = {'url': "https://www.youtube.com/playlist?list=" + search[0]['playlistId'],
                    'user': interaction.user.mention, 'name': interaction.user.display_name,
                    'avatar': interaction.user.display_avatar.url, 'items': search[0]['videoCount'],
                    'title': search[0]['title']['simpleText']}
            settings.queues[interaction.guild.id].append(temp)
            if not settings.env_vars[interaction.guild.id]['Downloading']:
                settings.env_vars[interaction.guild.id]['Active'] = True
            print(f"Successfully added playlist {color.RED}{color.BOLD}{search[0]['title']['simpleText']}{color.END} "
                  f"to the queue for {color.BLUE}{color.BOLD}{interaction.guild.name}{color.END}")
        else:
            await interaction.response.send_message('I am not in a voice channel')

    # The queue function allows a user to see the queue key for their specific server
    @nextcord.slash_command(name="queue", description="Shows the user the current server's queue")
    async def queue(self, interaction: Interaction):

        # First it checks if their guild id is in the queue dictionary
        if interaction.guild.id in settings.queues:

            # Then a view with the necessary buttons is retrieved
            items = 5
            pos = 0

            # An embed is then generated holding all the items in queue in pages (not yet done)
            embed = nextcord.Embed(title=f"{interaction.guild.name}'s Queue")
            await interaction.send(embed=embed)

            # Then the number of items per page and the number of pages are determined
            while True:
                pages = math.ceil(len(settings.queues[interaction.guild.id]) / items)
                if pos == 0:
                    view = Buttons.queueButtonBackDisabled()
                elif pos + 1 >= pages:
                    view = Buttons.queueButtonFrontDisabled()
                else:
                    view = Buttons.queueButton()

                # It then continues generating the embed and sets the page it is in
                embed = nextcord.Embed(title=f"{interaction.guild.name}'s Queue")
                minimum = pos * items
                if minimum + items > len(settings.queues[interaction.guild.id]):
                    maximum = len(settings.queues[interaction.guild.id])
                else:
                    maximum = (pos * items) + items
                for counter in range(minimum, maximum):
                    value = f"Added by: {settings.queues[interaction.guild.id][counter]['user']}\n"
                    if 'duration' in settings.queues[interaction.guild.id][counter]:
                        value += f"Duration: {settings.queues[interaction.guild.id][counter]['duration']}"
                    else:
                        value += f"Playlist Items: {settings.queues[interaction.guild.id][counter]['items']}"
                    embed.add_field(name=f"{counter + 1}: ***{settings.queues[interaction.guild.id][counter]['title']}***",
                                    value=value,
                                    inline=False)
                embed.set_footer(text=f"Page {pos + 1}/{pages} | Size: {len(settings.queues[interaction.guild.id])}")
                if pages == 1:
                    await interaction.edit_original_message(embed=embed)
                elif pages != 0:
                    await interaction.edit_original_message(embed=embed, view=view)
                    await view.wait()
                if view.value is None:
                    break
                elif view.value:
                    pos += 1
                else:
                    pos -= 1

        else:
            await interaction.send('There is no active queue for this server')

    # The repeat function allows a user to repeat the queue
    # If the bot is in a voice channel, this function allows the user to toggle the repeat key off and on
    # This is off by default
    @nextcord.slash_command(name="repeat", description="Toggles repeat on or off")
    async def repeat(self, interaction: Interaction):
        if interaction.guild.id in settings.env_vars:
            if settings.env_vars[interaction.guild.id]['Repeat']:
                settings.env_vars[interaction.guild.id]['Repeat'] = False
                if settings.queues[interaction.guild.id]:
                    for index in range(0, len(settings.queues[interaction.guild.id])):
                        if settings.current[interaction.guild.id]['url'] == settings.queues[interaction.guild.id][index]['url']:
                            settings.queues[interaction.guild.id].pop(index)
                            break
                await interaction.send('Repeating has been turned off')
            else:
                settings.env_vars[interaction.guild.id]['Repeat'] = True
                if settings.current[interaction.guild.id]:
                    settings.queues[interaction.guild.id].append({})
                    settings.queues[interaction.guild.id][-1] = settings.current[interaction.guild.id]
                await interaction.send('Repeating has been turned on')
        else:
            await interaction.send('I am not in a voice channel')

    # The shuffle function allows a user to shuffle the queue
    # If the bot is in a voice channel, this function allows the user to shuffle the entire queue
    @nextcord.slash_command(name="shuffle", description="Toggles shuffle on or off")
    async def shuffle(self, interaction: Interaction):

        # First, it checks if there is a valid queue
        if interaction.guild.id in settings.env_vars:

            # A temporary queue is generated with the shuffled items, then it is placed in the guild queue
            temp = []
            while settings.queues[interaction.guild.id]:
                index = random.randint(1, len(settings.queues[interaction.guild.id])) - 1
                temp.append(settings.queues[interaction.guild.id].pop(index))
            settings.queues[interaction.guild.id] = temp
            await interaction.send('Queue has been shuffled')
        else:
            await interaction.send('I am not in a voice channel')

    # The status command allows a user to see if repeating and shuffling both are turned on or off
    @nextcord.slash_command(name="status", description="Shows the user the status of the server")
    async def status(self, interaction: Interaction):
        if interaction.guild.id in settings.env_vars:
            embed = nextcord.Embed(title=f"{interaction.guild.name} status")
            embed.set_thumbnail(url=interaction.guild.icon.url)
            if settings.env_vars[interaction.guild.id]['Repeat']:
                embed.add_field(name="Repeat", value="On")
            else:
                embed.add_field(name="Repeat", value="Off")
            embed.add_field(name="Items in Queue", value=len(settings.queues[interaction.guild.id]))
            item = jsonbuilder.importJson(f"{settings.pwd}/Dependencies/{str(interaction.guild.id)}/preload.json")
            if item:
                embed.add_field(name="Preloaded Song", value=item['title'], inline=False)
            else:
                embed.add_field(name="Preloaded Song", value="None", inline=False)
            await interaction.send(embed=embed)
        else:
            await interaction.send('I am not in a voice channel')

    # The remove command allows a user to remove a single song from the queue
    # This is used with the index number retrieved from the queue command
    @nextcord.slash_command(name="remove", description="Allows a user to remove one item from queue")
    async def remove(self, interaction: Interaction, song: int):
        if interaction.guild.id in settings.queues:
            if len(settings.queues[interaction.guild.id]) >= song > 0:
                await interaction.send(
                    f"***{settings.queues[interaction.guild.id][song - 1]['title']}***\nhas been removed from the queue")
                settings.queues[interaction.guild.id].pop(song - 1)
            else:
                await interaction.send("Invalid choice of song removal")
        else:
            await interaction.send('There is no active queue')


def setup(client):
    client.add_cog(SlashMusic(client))
