# Buttons.py holds all the buttons necessary for use in Mobot
import nextcord


# The class queueButton is used for the queue command to move through the pages
class queueButton(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label='Back', style=nextcord.ButtonStyle.red)
    async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = False
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='Next', style=nextcord.ButtonStyle.green)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        await interaction.response.edit_message(view=self)
        self.stop()


class queueButtonBackDisabled(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label='Back', style=nextcord.ButtonStyle.red, disabled=True)
    async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = False
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='Next', style=nextcord.ButtonStyle.green)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        await interaction.response.edit_message(view=self)
        self.stop()


class queueButtonFrontDisabled(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label='Back', style=nextcord.ButtonStyle.red)
    async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = False
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='Next', style=nextcord.ButtonStyle.green, disabled=True)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        await interaction.response.edit_message(view=self)
        self.stop()


# THe class searchButton holds all the buttons used to make a selection in a search. The buttons correspond to the
# 1-5 buttons needed for a search
class searchButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=20)
        self.value = None

    @nextcord.ui.button(label='1', style=nextcord.ButtonStyle.blurple)
    async def one(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 1
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='2', style=nextcord.ButtonStyle.blurple)
    async def two(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 2
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='3', style=nextcord.ButtonStyle.blurple)
    async def three(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 3
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='4', style=nextcord.ButtonStyle.blurple)
    async def four(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 4
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='5', style=nextcord.ButtonStyle.blurple)
    async def five(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 5
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()
        
class playlistSelectButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=20)
        self.value = None
    
    @nextcord.ui.button(label='Playlist', style=nextcord.ButtonStyle.blurple)
    async def playlist(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 1
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @nextcord.ui.button(label='Song', style=nextcord.ButtonStyle.blurple)
    async def song(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = 2
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()