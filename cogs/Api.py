from quart import Quart
from quart import request
import settings
from nextcord.ext import commands
from nextcord.ext import tasks
import nextcord
import signal

app = Quart(__name__)


@app.get("/info")
async def test():
    return {"test": "Successful"}


# This API routine returns the queue for a single server
@app.get("/queues/<guild_id>")
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
@app.get("/queues")
async def queues():
    return {"queues": settings.queues}


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
