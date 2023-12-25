# cogs.General allows for some General commands for use in for Mobot
import asyncio
import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import Dependencies.Functions as Functions


# This class defines what the cogs.General will be able to do
class General(commands.Cog):

    def __init__(self, client):
        print("General Initialized Successfully")
        self.client = client

    # Ping test defines the ping command which allows a user to view the latency of the connection to Mobot
    @nextcord.slash_command(name="ping", description="Checks the bot's ping")
    async def ping(self, interaction: Interaction):
        embed = nextcord.Embed(title=f"My ping is {round(self.client.latency * 1000)}ms")
        await interaction.response.send_message(embed=embed)

    # Simple self-explanatory command
    @nextcord.slash_command(name="deez", description="Deez")
    async def deez(self, interaction: Interaction):
        await interaction.send('Nutz')
        await asyncio.sleep(1)
        await interaction.send('GOTTEM!')
        print("Response to deez printed")

    # This generates a tech quote from a small database of tech quotes under Dependencies/Quotes/Funnytechquotes.txt
    # Compiled quotes are from a variety of sources, most of them coming from Linus Torvalds
    @nextcord.slash_command(name="tquote", description="Prints a quote from a list of tech quotes")
    async def tquote(self, ctx):
        await ctx.send(Functions.techQuotes())
        print("Response to tquote printed")

    # The help function prints the help command using a slash command instead of a message command
    @nextcord.slash_command(name="help", description="Prints out helpful commands and options")
    async def help(self, interaction: Interaction):

        # First it generates an embed
        embed = nextcord.Embed(title="Mobot Commands")

        # Then it grabs all the slash commands for Mobot where it grabs the description and the command name
        for command in self.client.get_application_commands():
            desc = command.description
            if not desc or desc is None or desc == "":
                desc = 'No Description Provided'
            embed.add_field(name=f"`/{command.name}`", value=desc)

        # It then sends the embed to be printed out
        await interaction.send(embed=embed)


def setup(client):
    client.add_cog(General(client))
