import discord
from discord import app_commands
from discord.ui import View, button, Modal, Button
from discord.ext import commands
from DB_instances.room_opening_config_interface import server_config
from discord import ui

class Generic_Button(Button):
    def __init__(self, **kwargs):
        if 'callback' in kwargs:
            self.func = kwargs['callback']
            kwargs.pop('callback')
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
        self.callback = self.callbacks
        super().__init__(label=my_label, style=my_style, emoji=my_emoji)
    

    async def callbacks(self, interaction):
        if self.func is not None:
            await self.func(interaction, self, self.view)

    # def set_view(self, view):
    #     self.view = view


class Generic_View(View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)
    def add_generic_button(self, label=None, style=None, emoji=None, callback=None):
        new_button = Generic_Button(label=label,
                                     style=style,
                                     emoji=emoji,
                                     callback=callback)
        #new_button.set_view(self)
        self.add_item(new_button)

        return new_button

    
        





