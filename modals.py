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
    name = ui.TextInput(label='Name', placeholder='Enter a name for the VC', max_length=20, required=False)
    users_limit = ui.TextInput(label='User Limit', placeholder='Enter a number between 1-99 or leave blank for no limit', max_length=2, required=False)
    bitrate = ui.TextInput(label='Bitrate', placeholder='Enter a number between 8-96 or leave blank for default', max_length=2, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await self.callback_func(interaction)