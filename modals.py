import discord
from discord import app_commands
from discord.ui import button, Modal
import discord.ui
from discord.ext import commands

from discord import ui

class InstantModal(ui.Modal, title='Questionnaire Response'):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    def set_callback_func(self, callback_func):
        self.callback_func = callback_func
    botlimit = ui.TextInput(label='User Limit', placeholder='Enter a number between 1-99 or leave blank for no limit', min_length=0, max_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        await self.callback_func(interaction)