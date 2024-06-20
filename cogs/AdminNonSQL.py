import nextcord
from nextcord.ext import commands
import settings


# The AdminNonSQL Cog is for general purpose commands related to Administration Commands that don't require the Database
class AdminNonSQL(commands.Cog):

    def __init__(self, client):
        print("AdminNonSQL Initialized Successfully")
        self.client = client

    @commands.command(name="guildleave", description="Forces the bot to leave a particular Guild")
    async def guildleave(self, ctx, id):
        if str(ctx.author.id) == settings.owner:
            server = nextcord.utils.get(self.client.guilds, id=int(id))
            await ctx.send(f"Leaving the Server {server.name}")
            await server.leave()
        else:
            await ctx.send("You are not allowed to use this command")

    @commands.command(name="help", description="Prints out helpful administration commands and options")
    async def help(self, ctx):

        if str(ctx.author.id) == settings.owner:
            # First it generates an embed
            embed = nextcord.Embed(title="Mobot Administration Commands")

            # Then it grabs all the slash commands for Mobot where it grabs the description and the command name
            for command in self.client.commands:
                desc = command.description
                if not desc or desc is None or desc == "":
                    desc = 'No Description Provided'
                embed.add_field(name=f"`{self.client.command_prefix}{command.name}`", value=desc)

            # It then sends the embed to be printed out
            await ctx.send(embed=embed)
        else:
            await ctx.send("You are not allowed to use this command")


def setup(client):
    client.add_cog(AdminNonSQL(client))
