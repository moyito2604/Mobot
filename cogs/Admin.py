import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import settings
from Dependencies.Error import ReconnectError
import Dependencies.SQLFunc as SQLFunc


# The Admin Cog is for general purpose commands related to administration
class Admin(commands.Cog):

    def __init__(self, client):
        print("Admininstration Initialized Successfully")
        self.client = client

    # The Admin Command sets up the admin role for the current server
    @nextcord.slash_command(name="admin",
                            description="Sets the admin role for the current guild")
    async def admin(self, interaction: Interaction, role: str):

        # Strips the role string to just the id
        role = role.lstrip('<@&')
        role = role.rstrip('>')
        role = "".join(c for c in role if c.isnumeric())

        # Checks if there is an SQL connection still active
        try:
            await SQLFunc.checkConn()
        except ReconnectError:
            return

        # Updates the database and sets up the cursor to check if a admin role has been set
        settings.connection.commit()
        cursor = settings.connection.cursor(dictionary=True, buffered=True)
        cursor.execute(f"SELECT * FROM Admin_Roles WHERE Guild_id = {interaction.guild.id}")
        record = cursor.fetchone()

        # If there is an admin role set, then it checks to see if the role recorded is valid
        found = None
        if record:
            found = interaction.user.get_role(int(record['Role']))

        # It then makes sure that the user has permission to set the admin role for the server
        if not interaction.user.guild_permissions.administrator and not found:
            await interaction.send(f"You must have the <@&{record['Role']}> role to use this command")
            return

        # It then makes sure that the role provided is valid
        roletest = interaction.guild.get_role(int(role))
        if not roletest:
            await interaction.send("Invalid Role Provided, please try another role")
            return

        # If the record exists then it updates the admin role for the server
        if record:
            await interaction.send(f"Updating admin role to <@&{role}>")
            cursor.execute(f"""UPDATE Admin_Roles SET
                            Role = '{role}' WHERE
                            Guild_id = '{interaction.guild.id}'""")

        # If not it creates a new record and saves it to the database
        else:
            await interaction.send(f"No record found. Creating an admin role record for <@&{role}>")
            cursor.execute(f"""INSERT INTO Admin_Roles
                            (Guild_id, Role) VALUES
                            ('{interaction.guild.id}', '{role}')""")
        settings.connection.commit()


def setup(client):
    client.add_cog(Admin(client))
