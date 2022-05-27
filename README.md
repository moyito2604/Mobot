# Mobot
This is a bot made originally for The Commune server but is open to anybody who wants to use it for their own servers <br />
Here is a list of possible commands you can use with this bot:
```
m!ce: use to change the command extension using syntax        m!ce 'extension'
m!ding: replies with dong
m!deez: replies with nutz
m!tquote: Generates a tech quote

***Music Bot Commands***
m!join: joins voice channel
m!leave: leaves voice channel
m!play: plays music with a youtube link, queues music, and plays music that is currently paused
m!stop: stops playing audio and clears the queue
m!skip: skips the current track in queue
```

The music portion of the bot requires a couple dependencies to run properly as it utilizes **yt_dlp, nextcord, youtube-search-python, and ffmpeg** to process the audio that is recieved through the bot. 
To install these, it is necessary to run the three commands below in a Debian based distro:
```
pip3 install nextcord
pip3 install yt_dlp
pip3 install youtube-search-python
apt-get install ffmpeg
```
Once these dependencies are installed, clone the repository to the location desired using this command:
```
git clone https://github.com/lldmmoisessc/Mobot.git
```
This bot is only designed to run in a version of linux since it uses some shell commands only available to Linux
