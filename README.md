# Mobot
This is a bot made originally for The Commune server but is open to anybody who wants to use it for their own servers <br />

The music portion of the bot requires a couple dependencies to run properly as it utilizes **yt_dlp, nextcord, youtube-search-python, scrapetube, pydub, argparse, PyNaCl and ffmpeg** to process the audio that is recieved through the bot. 

First clone the repository to the location desired using this command:
```
git clone https://github.com/moyito2604/Mobot.git
```

Then to install these dependencies, it is necessary to run the commands below in a Debian based distro:
```
pip3 install --upgrade pip
pip3 install -r requirements.txt
apt-get install ffmpeg
```

This bot is only designed to run in a version of linux since it uses some shell commands only available to Linux <br /> <br />
Once the bot is downloaded to the desired location, navigate the directory and run the following command to activate it.
```
python3 main.py --token='TOKEN'
```
On the first run of the program, the bot will generate a config.py with a couple fields in it and you won't have to use the ```--token``` argument for any later runs <br />

To activate the database, you will need to add environment variables for ```MYSQL_HOST``` ```MYSQL_DATABASE``` ```MYSQL_USER``` and ```MYSQL_PASSWORD``` which all represent the hostname, database, database user, and database password respectively. <br /> <br />

The syntax for linux is:
```export MYSQL_HOST=hostname```

To make a prebuilt container, you will have to run the following command
```
docker run -e token='TOKEN' -e MYSQL_HOST='hostname' -e MYSQL_DATABASE='database' -e MYSQL_USER='username' -e MYSQL_PASSWORD='password' ghcr.io/moyito2604/mobot:latest
```
