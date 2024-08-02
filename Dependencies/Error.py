import nextcord
import settings


class ReconnectError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class AudioDownloadError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


def internalErrorEmbed(desc, details):
    embed = nextcord.Embed(title="Internal Exception", color=0xFF0000)
    embed.add_field(name="Exception Details:", value=f"```{details}"[0:1020] + "```")
    embed.set_footer(text=desc)
    if settings.owner != "None":
        embed.description = f"Please contact the bot owner <@!{settings.owner}> to report"
    return embed
