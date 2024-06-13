import nextcord
from nextcord.ext import commands
from nextcord.ui import Select, View
import settings


# The AdminNonSQL Cog is for general purpose commands related to Administration Commands that don't require the Database
class AdminNonSQL(commands.Cog):

    def __init__(self, client):
        print("AdminNonSQL Initialized Successfully")
        self.client = client

    @commands.command()
    async def guildinfo(self, ctx):

        async def dropdown_callback(interaction):
            for value in dropdown.values:
                server = nextcord.utils.get(self.client.guilds, name=value)
            embed = nextcord.Embed(title=f"{server.name} ({server.id})")
            membersamt = 20
            memberstr = ""
            for index, member in enumerate(server.members):
                memberstr += f"{member.name} ({member.id})\n"
                if index == membersamt:
                    break
            embed.add_field(name="Member Count", value=server.member_count)
            embed.add_field(name="Guild Owner", value=f"{server.owner} ({server.owner.id})", inline=False)
            embed.add_field(name=f"Guild Members (First {membersamt})", value=memberstr, inline=False)
            if server.icon:
                embed.set_thumbnail(url=server.icon.url)
            await interaction.send(embed=embed)
            await interaction.message.delete()

        if str(ctx.author.id) == settings.owner:
            options = []
            for guild in self.client.guilds:
                options.append(nextcord.SelectOption(label=guild.name))
            dropdown = Select(placeholder="Choose a Guild", min_values=1, max_values=1, options=options)
            dropdown.callback = dropdown_callback
            view = View(timeout=180)
            view.add_item(dropdown)
            await ctx.send("Choose a Guild to Display more Information", view=view)

        else:
            await ctx.send("You are not allowed to use this command")

    @commands.command()
    async def guildleave(self, ctx, id):
        if str(ctx.author.id) == settings.owner:
            server = nextcord.utils.get(self.client.guilds, id=int(id))
            await ctx.send(f"Leaving the Server {server.name}")
            await server.leave()


def setup(client):
    client.add_cog(AdminNonSQL(client))
