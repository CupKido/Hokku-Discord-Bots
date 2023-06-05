import discord
from ui_component_extention.ui_tools import mode_style 
class on_off_button(discord.ui.Button):
    def __init__(self, **kwarg):
        if 'callback' in kwargs.keys():
            self.get_value = kwargs['callback']
            del kwargs['callback']
        else:
            self.get_value = lambda x: not x
        if 'value' in kwargs.keys():
            self.value = kwargs['value']
            del kwargs['value']
        else: 
            self.value = False
        
        super().__init__(**kwargs)
    
    async def callback(self, interaction):
        await interaction.response.defer()
        self.value = await self.get_value(self.value)
        self.style = mode_style.get_on_off(self.value) 
        await interaction.followup.edit(view=self.view)
        

