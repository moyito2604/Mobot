import nextcord


class queueButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=5)
        self.value = None

    @nextcord.ui.button(label='Back', style=nextcord.ButtonStyle.red)
    async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True

    @nextcord.ui.button(label='Next', style=nextcord.ButtonStyle.green)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True


class searchButton(nextcord.ui.View):
    def __init(self):
        super().__init__(timeout=5)
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