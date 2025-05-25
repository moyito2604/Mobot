import nextcord
import settings


# ReconnectError is used to let the user know that the SQL server has not reconnected properly
class ReconnectError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


# AudioDownloadError is used when an item fails to download
class AudioDownloadError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


# This function generates an error message for the user when an item has failed to download
async def internalErrorEmbed(desc, details, ctx, notify: bool = False):
    embed = nextcord.Embed(title="Internal Exception", color=0xFF0000)
    embed.add_field(name="Exception Details:", value=f"```{details}"[0:1020] + "```")
    embed.set_footer(text=desc)
    if settings.owner != "None":
        if notify:
            user = settings.client.get_user(int(settings.owner))
            channel = await user.create_dm()
            embed.description = f"Issue Reported in server \"{ctx.guild.name}\""
            await channel.send(embed=embed)
        embed.description = f"Bot Owner <@!{settings.owner}> has been contacted to report the issue"
    return embed
