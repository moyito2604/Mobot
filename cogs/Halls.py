import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import settings

class Halls(commands.Cog):
    
    def __init__(self, client):
        print("Halls Initialized Successfully")
        self.client = client
    
    @nextcord.slash_command(name="halllist", 
                            description="Prints the current Guild's Halls")
    async def halllist(self, interaction: Interaction):
        settings.connection.commit()
        cursor = settings.connection.cursor(dictionary=True, buffered=True)
        cursor.execute(f"SELECT * FROM {interaction.guild.id}_Halls")
        records = cursor.fetchall()
        embed = nextcord.Embed(title=f"{interaction.guild.name}'s Halls")
        for row in records:
            embed.add_field(name="", value=f"<#{row['Channel']}>{row['Emote']}x{row['Amount']} >> <#{row['Hall']}>", inline=False)
        await interaction.send(embed=embed)
        cursor.close()
    
    @nextcord.slash_command(name="hall", 
                            description="Updates or Adds a Hall")
    async def hall(self, interaction: Interaction, channel:str, emote:str, amount:int, hall:str):
        channel = channel.lstrip('<#')
        channel = channel.rstrip('>')
        hall = hall.lstrip('<#')
        hall = hall.rstrip('>')
        
        if not interaction.guild.get_channel(int(channel)) or not interaction.guild.get_channel(int(hall)):
            await interaction.send("Invalid Channel or Hall Channel Provided")
            return
        elif channel == hall:
            await interaction.send("Channel cannot be its own Hall")
            return
        
        emojis = await interaction.guild.fetch_emojis()
        emotefound = False
        for emoji in emojis:
            if str(emoji.id) in emote:
                emotefound = True
        if not emotefound:
            await interaction.send("Invalid Emoji Provided, Please provide a server Emoji")
            return
        
        settings.connection.commit()
        cursor = settings.connection.cursor(dictionary=True, buffered=True)
        cursor.execute(f"SELECT * FROM {interaction.guild.id}_Halls WHERE Channel = {channel}")
        record = cursor.fetchall()
        cursor.execute(f"SELECT * FROM {interaction.guild.id}_Halls")
        table = cursor.fetchall()
        
        for entry in table:
            if hall in entry['Channel'] or channel in entry['Hall']:
                await interaction.send("Hall Channel cannot be another Hall Entry")
                return

        if record:
            await interaction.send(f"Hall found, Updating according to the following specifications:\n"+
                                   f"Channel: <#{channel}>\nEmote: {emote}\nAmount: {amount}\nHall: <#{hall}>")
            cursor.execute(f"""UPDATE {interaction.guild.id}_Halls SET
                            Emote = '{emote}',
                            Amount = {amount},
                            Hall = '{hall}' WHERE
                            Channel = '{channel}'""")
        else:
            await interaction.send(f"Hall not found, adding according to the following specifications:\n"+
                                   f"Channel: <#{channel}>\nEmote: {emote}\nAmount: {amount}\nHall: <#{hall}>")
            cursor.execute(f"""INSERT INTO {interaction.guild.id}_Halls
                            (Channel, Emote, Amount, Hall) VALUES
                            ('{channel}', '{emote}', {amount}, '{hall}')""")
        settings.connection.commit()
        
def setup(client):
    client.add_cog(Halls(client))