import discord
from discord import app_commands
from discord.ui import View, button, Modal
from discord.ext import commands
from DB_instances.server_config_interface import server_config

class InstantButtonView(View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, bot_client):
        super().__init__()
        self.bot_client = bot_client
        
    @button(label="Edit VC", style=discord.ButtonStyle.primary, emoji="😎") 
    async def button_callback(self, interaction, button):
         # Send a message when the button is clicked
         print("button clicked")
         await self.bot_client.initialize_buttons()

def get_InstantButtonView(bot_client):
    return InstantButtonView(bot_client)

    

    
