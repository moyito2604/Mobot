from quart import Quart
import settings
from nextcord.ext import commands
from nextcord.ext import tasks
import nextcord
import signal
import os

app = Quart(__name__)


@app.route("/info")
async def info():
    version = os.environ.get("VERSION", "N/A")
    return f"""<html>
                <head>
                    <title>
                        Bot Information
                    </title>
                </head>
                <body>
                    <h1>{settings.client.user.name}</h1>
                    <p>Bot Version {version}</p>
                </body>
            </html>"""


# This API routine returns the queue for a single server
@app.route("/queues/<guild_id>")
async def queue(guild_id):
    guild = nextcord.utils.get(settings.client.guilds, id=int(guild_id))
    voice = nextcord.utils.get(settings.client.voice_clients, guild=guild)
    if voice and guild:
        return {"guild_id": guild_id, "guild_name": guild.name, "queue": settings.queues[int(guild_id)]}
    elif guild and not voice:
        return {"Error": "No Voice Channel Detected"}
    else:
        return {"Error": "Invalid Guild"}


# This API routine returns the global list of queues
@app.route("/queues")
async def queues():
    return {"queues": settings.queues}


@app.route("/guilds")
async def guilds():
    guilddict = {}
    for guild in settings.client.guilds:
        guilddict[guild.id] = {}
        guilddict[guild.id]["GuildName"] = guild.name
        guilddict[guild.id]["Members"] = guild.member_count
        guilddict[guild.id]["OwnerName"] = guild.owner.name
        guilddict[guild.id]["OwnerDisplayName"] = guild.owner.display_name
        guilddict[guild.id]["OwnerID"] = guild.owner.id
    return guilddict


@app.route("/guilds/<guild_id>")
async def guildinfo(guild_id):
    guilddict = {}
    guild = nextcord.utils.get(settings.client.guilds, id=int(guild_id))
    guilddict["GuildName"] = guild.name
    guilddict["MemberCount"] = guild.member_count
    guilddict["Thumbnail"] = guild.icon.url
    guilddict["OwnerName"] = guild.owner.name
    guilddict["OwnerDisplayName"] = guild.owner.display_name
    guilddict["OwnerID"] = guild.owner.id
    guilddict["Members"] = []
    for member in guild.members:
        if guild.owner.id is not member.id:
            guilddict["Members"].append({"Name": member.name, "DisplayName": member.display_name, "ID": member.id})
    return guilddict


# The Admin Cog is for general purpose commands related to administration
class API(commands.Cog):

    def __init__(self, client):
        print("API Initialized Successfully")
        self.client = client
        self.task = self.client.loop.create_task(app.run_task('0.0.0.0', port=2500))
        self.sighandle.start()

    @tasks.loop(count=1)
    async def sighandle(self):
        await self.client.wait_until_ready()
        self.client.loop.add_signal_handler(signal.SIGINT, lambda: self.client.loop.stop())
        self.client.loop.add_signal_handler(signal.SIGTERM, lambda: self.client.loop.stop())
        print("Signal Handlers Registered Successfully")


def setup(client):
    client.add_cog(API(client))
