import nextcord
import settings
import os
from Dependencies.Error import ReconnectError
from mysql.connector import InterfaceError
from Dependencies.Functions import Color


# Returns true if the person is allowed to run the command, else false
async def rolecheck(interaction):

    # Checks if there is an SQL connection still active
    try:
        await checkConn()
    except ReconnectError:
        return

    cursor = settings.connection.cursor(dictionary=True, buffered=True)

    # This ensures that person running the command is allowed to
    cursor.execute(f"SELECT * FROM Admin_Roles WHERE Guild_id = {interaction.guild.id}")
    record = cursor.fetchone()

    found = None
    if record:
        found = interaction.user.get_role(int(record['Role']))

    if not interaction.user.guild_permissions.administrator and not found:
        await interaction.send(f"You must have the <@&{record['Role']}> role to use this command")
        return False
    return True


async def historycheck(guild, channel_id, hall_id, amount, emoji, hall_emoji):
    channel = nextcord.utils.get(guild.channels, id=int(channel_id))
    hall = nextcord.utils.get(guild.channels, id=int(hall_id))
    async for message in channel.history(limit=100):
        if message.attachments or message.embeds:
            hall_found = False
            emote_amount = 0
            await message.add_reaction(emoji)
            for emote in message.reactions:
                if str(emote) == hall_emoji and emote.me:
                    hall_found = True
                if str(emote) == emoji:
                    emote_amount = emote.count
            if not hall_found and emote_amount >= amount:
                await halladd(message, hall, hall_emoji)


async def halladd(message, hall_channel, hall_emote):
    string = f"Posted by <@{message.author.id}>:\n{message.content}"
    files = []
    for attachment in message.attachments:
        await attachment.save(attachment.filename)
        files.append(nextcord.File(attachment.filename))
    try:
        await message.add_reaction(hall_emote)
    except nextcord.errors.Forbidden:
        pass
    else:
        await hall_channel.send(string, files=files)
    for file in files:
        try:
            os.remove(file.filename)
        except FileNotFoundError:
            pass


async def checkConn():
    try:
        #print(f"{Color.RED}{Color.BOLD}SQL Connection Lost. Attempting to reconnect.{Color.END}")
        settings.connection.ping(True, attempts=3, delay=1)
    except InterfaceError:
        print(f"{Color.RED}{Color.BOLD}Error: Failed to Connect to the SQL Server{Color.END}")
        raise ReconnectError("Failed to reconnect to SQL Server")
