import discord
from discord import app_commands
from discord.ui import button, Modal
import discord.ui
from discord.ext import commands

from discord import ui

class InstantModal(ui.Modal, title='Questionnaire Response'):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def set_fields(self, name_to_set=None, users_limit_to_set=None, bitrate_to_set=None):
        if name_to_set is not None:
            name = ui.TextInput(label='Name', placeholder='', default=name_to_set, max_length=20, required=False)
        else:
            name = ui.TextInput(label='Name', placeholder='Enter a name for the VC', max_length=20, required=False)
        if users_limit_to_set is not None:
            users_limit = ui.TextInput(label='User Limit', placeholder='', default=str(users_limit_to_set), max_length=2, required=False)
        else:
            users_limit = ui.TextInput(label='User Limit', placeholder='Enter a number between 1-99 or leave blank for no limit', max_length=2, required=False)
        
        self.add_item(name)
        self.add_item(users_limit)
    

    def set_callback_func(self, callback_func):
        self.callback_func = callback_func

    async def on_submit(self, interaction: discord.Interaction):
        await self.callback_func(interaction)

