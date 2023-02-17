import discord
from discord import app_commands
from discord.ui import View, button, Modal, Button
from discord.ext import commands
from DB_instances.room_opening_config_interface import server_config
from discord import ui

class CustomButton(Button):
    def __init__(self, **kwargs):
        if 'callback' in kwargs:
            self.callback = kwargs['callback']
            kwargs.pop('callback')
        super().__init__(label=kwargs['label'], style=kwargs['style'], emoji=kwargs['emoji'])

    async def callbacks(self, interaction):
        await self.callback(interaction)
        

class InstantButtonView(View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, room_opening, color):
        super().__init__(timeout=None)
        self.room_opening = room_opening
        self.color = color
        self.my_button = CustomButton(callback =self.button_callback, label="Edit VC", style=color, emoji="😎")
        self.add_item(self.my_button)
        
        
    async def button_callback(self, interaction):
        # Send a message when the button is clicked
        print("button clicked")
        await self.room_opening.edit_channel_button(interaction)

def get_InstantButtonView(roon_opening, color):
    return InstantButtonView(roon_opening, color)

    

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

