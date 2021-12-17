from nextcord import client
import nextcord
from nextcord.ext.commands import bot
from nextcord.ext.commands.converter import GuildConverter
from plugins.contact.bot.dropdown import Dropdown, DropdownView
from bot.utils.sconfig import Sconfig
from utils import Gunibot, MyContext

async def set_message(channel):
    """Sends a message with our dropdown containing colours"""

    # Create the view containing our dropdown
    view = DropdownView()

    # Sending a message containing our view
    message = "Coucou, ceci est un message de contact" #self.bot.server_configs[ctx.guild.id]["contact_message"]
    await channel.send(message, view=view)

async def remove_previous(channel):
    async for msg in channel.history(limit=100):
        return None
        if msg.author == bot


async def update_message(channel):
    remove_previous(channel)
    set_message(channel)