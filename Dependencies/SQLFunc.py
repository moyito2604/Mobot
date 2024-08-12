import nextcord
import settings
import os
from Dependencies.Error import ReconnectError
from mysql.connector import InterfaceError
from Dependencies.Functions import Color
from mysql.connector import Error


# This function simplifies the creation of Guild.txt for the multiple instances that it may be created
# If a database exists, then it places the information in a database
async def guildSave():

    # Checks if there is an SQL connection still active
    try:
        await checkConn()
    except ReconnectError:
        return

    # Sets up cursor and attempts to see if a table is created for the current guild
    cursor = settings.connection.cursor(dictionary=True, buffered=True)
    for guild in settings.client.guilds:
        try:
            cursor.execute(f"""CREATE TABLE {guild.id}_Halls (
                    Channel varchar(50) NOT NULL,
                    Emote varchar(100) NOT NULL,
                    Amount int NOT NULL,
                    Hall varchar(50) NOT NULL,
                    Hall_Emote varchar(100) NOT NULL)""")
        except Error:
            pass
    settings.connection.commit()
    cursor.close()


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


async def blocklistcheck(guild):

    # Checks if there is an SQL connection still active
    try:
        await checkConn()
    except ReconnectError:
        return

    # It then sets up a cursor and sees if the bot has been blocked for a Guild
    settings.connection.commit()
    cursor = settings.connection.cursor(dictionary=True, buffered=True)
    cursor.execute(f"SELECT * FROM Blocklist WHERE Guild_id = {guild.id}")
    record = cursor.fetchone()
    if record:
        print(f"Bot is blocked from joining Guild {Color.BLUE}{Color.BOLD}{guild.id}{Color.END}")
        await guild.leave()


# This function checks the history of a server to see if there is a hall
async def historycheck(guild, channel_id, hall_id, amount, emoji, hall_emoji):

    # First it grabs the channels from the provided IDs
    channel = nextcord.utils.get(guild.channels, id=int(channel_id))
    hall = nextcord.utils.get(guild.channels, id=int(hall_id))

    # Then it goes over the past 100 messages in the channels history
    async for message in channel.history(limit=100):

        # It then checks if they have attachments or embeds
        if message.attachments or message.embeds:
            hall_found = False
            emote_amount = 0
            await message.add_reaction(emoji)

            # If the message doesn't have the hall emote, and it has the right amount of emotes for a hall, it adds it
            # to the hall
            for emote in message.reactions:
                if str(emote) == hall_emoji and emote.me:
                    hall_found = True
                if str(emote) == emoji:
                    emote_amount = emote.count
            if not hall_found and emote_amount >= amount:
                await halladd(message, hall, hall_emoji)


# This function is run if a hall is found
async def halladd(message, hall_channel, hall_emote):

    # First it generates the string that holds the original message content
    string = f"Posted by <@{message.author.id}>:\n{message.content}"

    # Then it grabs any attachments that were placed in the message, temporarily saves them, and adds them to files
    files = []
    for attachment in message.attachments:
        await attachment.save(attachment.filename)
        files.append(nextcord.File(attachment.filename))

    # It then attempts to add the hall emote to the message and add the message to the hall
    try:
        await message.add_reaction(hall_emote)
    except nextcord.errors.Forbidden:
        pass
    else:
        await hall_channel.send(string, files=files)

    # It then removes all the temporary attachments
    for file in files:
        try:
            os.remove(file.filename)
        except FileNotFoundError:
            pass


# checkConn ensures that anytime an SQL command is run, there is an SQL connection available
async def checkConn():

    # First it tries to ping the server. If it fails, it sends a message with the error specifics to the console
    try:
        settings.connection.ping(True, attempts=3, delay=1)
    except InterfaceError:
        print(f"{Color.RED}{Color.BOLD}Error: Failed to Connect to the SQL Server{Color.END}")
        raise ReconnectError("Failed to reconnect to SQL Server")
    except AttributeError:
        print(f"{Color.RED}{Color.BOLD}Error: No Existing SQL Connection{Color.END}")
        raise ReconnectError("No Existing SQL Connection")
