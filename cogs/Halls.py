#The Halls.py Cog handles all of the commands related to the Halls functionality (starboard?)
import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import settings

class Halls(commands.Cog):
    
    def __init__(self, client):
        print("Halls Initialized Successfully")
        self.client = client
    
    #The halllist command lists all of the halls in the current guild
    @nextcord.slash_command(name="halllist", 
                            description="Prints the current Guild's Halls")
    async def halllist(self, interaction: Interaction):
        
        #First it ensures that its information is updated and sets up a cursor
        settings.connection.commit()
        cursor = settings.connection.cursor(dictionary=True, buffered=True)
        
        #It then queries the Database to grab all entries for the current guild
        cursor.execute(f"SELECT * FROM {interaction.guild.id}_Halls")
        records = cursor.fetchall()
        
        #It then embeds them, sends them to the current guild, and closes the cursor
        embed = nextcord.Embed(title=f"{interaction.guild.name}'s Halls")
        for row in records:
            embed.add_field(name="", value=f"<#{row['Channel']}>{row['Emote']}x{row['Amount']} >> <#{row['Hall']}>", inline=False)
        await interaction.send(embed=embed)
        cursor.close()
    
    #The hall command adds a hall to the current guild's database
    @nextcord.slash_command(name="hall", 
                            description="Updates or Adds a Hall")
    async def hall(self, interaction: Interaction, channel:str, emote:str, amount:int, hall:str):
        
        #First it strips the string to ensure it is in the right format
        channel = channel.lstrip('<#')
        channel = channel.rstrip('>')
        hall = hall.lstrip('<#')
        hall = hall.rstrip('>')
        channel = "".join(c for c in channel if c.isnumeric())
        hall = "".join(c for c in hall if c.isnumeric())
        
        #Then it ensures that the channels provided aren't invalid or duplicates
        if not interaction.guild.get_channel(int(channel)) or not interaction.guild.get_channel(int(hall)):
            await interaction.send("Invalid Channel or Hall Channel Provided")
            return
        elif channel == hall:
            await interaction.send("Channel cannot be its own Hall")
            return
        
        #It also makes sure that the emote is valid
        emojis = await interaction.guild.fetch_emojis()
        emotefound = False
        for emoji in emojis:
            if str(emoji.id) in emote:
                emotefound = True
        if not emotefound:
            await interaction.send("Invalid Emoji Provided, Please provide a server Emoji")
            return
        
        #It sets up the database connection and cursor, where it queries to make sure the hall exists or not
        #It also grabs the entire table of Halls for the guild
        settings.connection.commit()
        cursor = settings.connection.cursor(dictionary=True, buffered=True)
        cursor.execute(f"SELECT * FROM {interaction.guild.id}_Halls WHERE Channel = {channel}")
        record = cursor.fetchall()
        cursor.execute(f"SELECT * FROM {interaction.guild.id}_Halls")
        table = cursor.fetchall()
        
        #Using the table of halls, it makes sure that a Hall Channel isn't a main channel
        for entry in table:
            if hall in entry['Channel'] or channel in entry['Hall']:
                await interaction.send("Hall Channel cannot be another Hall Entry")
                return

        #If the hall exists, then it queries the database to update it with the information provided
        if record:
            await interaction.send(f"Hall found, Updating according to the following specifications:\n"+
                                   f"Channel: <#{channel}>\nEmote: {emote}\nAmount: {amount}\nHall: <#{hall}>")
            cursor.execute(f"""UPDATE {interaction.guild.id}_Halls SET
                            Emote = '{emote}',
                            Amount = {amount},
                            Hall = '{hall}' WHERE
                            Channel = '{channel}'""")
            
        #If not, then the database is queried to make a new record for the hall in the guild's database
        else:
            await interaction.send(f"Hall not found, adding according to the following specifications:\n"+
                                   f"Channel: <#{channel}>\nEmote: {emote}\nAmount: {amount}\nHall: <#{hall}>")
            cursor.execute(f"""INSERT INTO {interaction.guild.id}_Halls
                            (Channel, Emote, Amount, Hall) VALUES
                            ('{channel}', '{emote}', {amount}, '{hall}')""")
        
        #It then commits the changes and closes the cursor
        settings.connection.commit()
        cursor.close()
        
    #The remove hall command removes a single hall from the database
    @nextcord.slash_command(name="removehall", 
                            description="Removes a Hall")
    async def removehall(self, interaction: Interaction, channel:str,):
        
        #First it strips the string to ensure it is in the proper format
        channel = channel.lstrip('<#')
        channel = channel.rstrip('>')
        channel = "".join(c for c in channel if c.isnumeric())
        
        #Then it makes sure that the channel provided is a valid channel
        if not interaction.guild.get_channel(int(channel)):
            await interaction.send("Invalid Channel or Hall Channel Provided")
            return
        
        #It then prepares the database and checks to make sure that the hall exists
        settings.connection.commit()
        cursor = settings.connection.cursor(dictionary=True, buffered=True)
        cursor.execute(f"SELECT * FROM {interaction.guild.id}_Halls WHERE Channel = {channel}")
        record = cursor.fetchall()
        
        #If it doesn't exist, then it lets the user know and exits the function
        if not record:
            await interaction.send(f"No Hall with channel <#{channel}>")
            return
    
        #If it does exist, it deletes it from the database, lets the user know, updates the database
        #Finally, it closes the cursor to cleanup
        cursor.execute(f"DELETE FROM {interaction.guild.id}_Halls WHERE Channel = {channel}")
        await interaction.send(f"Deleted Hall associated with channel <#{channel}>")
        settings.connection.commit()
        cursor.close()
        
def setup(client):
    client.add_cog(Halls(client))