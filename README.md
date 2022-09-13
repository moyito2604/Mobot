# Mobot
This is a bot made originally for The Commune server but is open to anybody who wants to use it for their own servers <br />
Here is a list of possible commands you can use with this bot:
```
m!ding: replies with dong
m!deez: replies with nutz
m!tquote: Generates a tech quote
All commands with an extension are case insensitive
Music Bot Commands
m!join: joins voice channel
m!leave: leaves voice channel
m!play: plays music with a youtube link, queues music, and plays music currently paused
This command also allows you to search for a song on youtube

m!stop: stops playing audio and clears the queue
m!skip: skips the current track in queue
m!showqueue: shows the songs that are currently in queue
m!repeat: Allows you to toggle the queue repeat
m!remove: Allows the user to remove a single item from queue
m!save: Allows a user to save a queue
m!load: Allows a user to load a the saved queue
m!song: Searches and adds a song to the queue without selection
m!playlist: Searches for playlists and allows the user to select a playlist to add to the queue
m!qplaylist: Searches and adds a playlist to the queue without selection
Slash Commands
/ping: Displays the bot's ping
/unpause: plays any paused music in the bot
All of the Music commands have slash versions as well
```

The music portion of the bot requires a couple dependencies to run properly as it utilizes **yt_dlp, nextcord, youtube-search-python, scrapetube, pydub, argparse, PyNaCl and ffmpeg** to process the audio that is recieved through the bot. 
To install these, it is necessary to run the commands below in a Debian based distro:
```
pip3 install --upgrade pip
pip3 install -r requirements.txt
apt-get install ffmpeg
```
Once these dependencies are installed, clone the repository to the location desired using this command:
```
git clone https://github.com/lldmmoisessc/Mobot.git
```
This bot is only designed to run in a version of linux since it uses some shell commands only available to Linux <br /> <br />
Once the bot is downloaded to the desired location, navigate the directory and run the following command to activate it.
```
python3 main.py
```
On the first run of the program, the bot will generate a config.py with a couple fields in it and will prompt you to input your bot token
```
Token = 'TOKEN'
extension = 'm!'
```
Input the bot token under token and run the program again to be able to use the bot <br />
The extension field is the default extension used by the bot to run commands.
