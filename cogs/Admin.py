import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import settings

class Admin(commands.Cog):
    
    def __init__(self, client):
        print("Admininstration Initialized Successfully")
        self.client = client
        
    @nextcord.slash_command(name="admin", 
                            description="Sets the admin role for the current guild")
    async def admin(self, interaction: Interaction, role: str):
        role = role.lstrip('<@&')
        role = role.rstrip('>')
        role = "".join(c for c in role if c.isnumeric())
        
        settings.connection.commit()
        cursor = settings.connection.cursor(dictionary=True, buffered=True)
        cursor.execute(f"SELECT * FROM Admin_Roles WHERE Guild_id = {interaction.guild.id}")
        record = cursor.fetchone()
        
        found = None
        if record:
            found = interaction.user.get_role(int(record['Role']))
        
        if interaction.user.guild_permissions.administrator or found:
            roletest = interaction.guild.get_role(int(role))
            if not roletest:
                await interaction.send("Invalid Role Provided, please try another role")
                return
            if record:
                await interaction.send(f"Updating admin role to <@&{role}>")
                cursor.execute(f"""UPDATE Admin_Roles SET
                                Role = '{role}' WHERE
                                Guild_id = '{interaction.guild.id}'""")
            else:
                await interaction.send(f"No record found. Creating an admin role record for <@&{role}>")
                cursor.execute(f"""INSERT INTO Admin_Roles
                                (Guild_id, Role) VALUES
                                ('{interaction.guild.id}', '{role}')""")
            settings.connection.commit()
        else:
            await interaction.send("You do not have the permissions to use this command")
            return
        
def setup(client):
    client.add_cog(Admin(client))