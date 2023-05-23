import discord
from discord import app_commands
from discord.ui import View, button, Modal, Button, select
from discord.ext import commands
from discord import ui


class role_button(Button):
    def __init__(self, **kwargs):
        if 'label' in kwargs.keys():
            my_label = kwargs['label']
        else:
            my_label = None
        if 'style' in kwargs.keys():
            my_style = kwargs['style']
        else:
            my_style = None
        if 'emoji' in kwargs.keys():
            my_emoji = kwargs['emoji']
        else: 
            my_emoji = None
        if 'role_id' in kwargs.keys():
            self.role_id = kwargs['role_id']
        else:
            self.role_id = None
            
        super().__init__(label=my_label, style=my_style, emoji=my_emoji)
    
    async def callback(self, interaction):
        if interaction.user.id == interaction.guild.owner_id:
            await interaction.response.send_message('Sorry, Owner cannot be modified', ephemeral=True)
            return
        if self.role_id is not None:
            role = interaction.guild.get_role(self.role_id)
            if role is not None:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    await interaction.response.send_message('Role removed', ephemeral=True)
                else:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message('Role added', ephemeral=True)
            else:
                await interaction.response.send_message('Role not found', ephemeral=True)
        else:
            await interaction.response.send_message('Role not found', ephemeral=True)
