import discord

from discord.ext import commands

# Defines a custom Select containing colour options
# that the user can choose. The callback function
# of this class is called when the user changes their choice
class Dropdown(discord.ui.Select):
    def __init__(self):

        contact_topics = [
            {'Title':'Red','Description':'Your favourite colour is red','Emoji':'🟥'},
            {'Title':'Green','Description':'Your favourite colour is green','Emoji':'🟩'},
            {'Title':'Blue','Description':'Your favourite colour is blue','Emoji':'🟦'},
        ]

        # Set the options that will be presented inside the dropdown
        options = []
        for option in contact_topics:
            options.append(discord.SelectOption(label=option['Title'], description=option['Description'], emoji=option['Emoji']))

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(placeholder='Choose your favourite colour...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's 
        # selected options. We only want the first one.
        await interaction.response.send_message(f'Your favourite colour is {self.values[0]}')


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())