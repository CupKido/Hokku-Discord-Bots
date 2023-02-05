import discord
from discord import app_commands
from discord.ui import View, button, Modal
from discord.ext import commands
from server_config_interface import server_config

class InsantButtonView(View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, callback_func):
        super().__init__()
        self.callback_func = callback_func

    @button(label="Open VC", style=discord.ButtonStyle.primary, emoji="😎") # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, interaction, button):
         # Send a message when the button is clicked
         print("button clicked")
         await self.callback_func(interaction)


    
