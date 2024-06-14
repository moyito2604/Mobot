import nextcord
from nextcord.ext import commands
import settings


# The AdminNonSQL Cog is for general purpose commands related to Administration Commands that don't require the Database
class AdminNonSQL(commands.Cog):

    def __init__(self, client):
        print("AdminNonSQL Initialized Successfully")
        self.client = client

    @commands.command()
    async def guildleave(self, ctx, id):
        if str(ctx.author.id) == settings.owner:
            server = nextcord.utils.get(self.client.guilds, id=int(id))
            await ctx.send(f"Leaving the Server {server.name}")
            await server.leave()
        else:
            await ctx.send("You are not allowed to use this command")


def setup(client):
    client.add_cog(AdminNonSQL(client))
