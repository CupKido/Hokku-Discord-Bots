import discord
from discord import app_commands
from discord.ui import View, button, Modal, Button
from discord.ext import commands
from DB_instances.server_config_interface import server_config

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

    

    
