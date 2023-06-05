import discord
from ui_components_extension.ui_tools import mode_styles 
import inspect
class on_off_button(discord.ui.Button):
    def __init__(self, **kwargs):
        if 'callback' in kwargs.keys():
            # make sure callback returns a bool
            if 'return' not in kwargs['callback'].__annotations__.keys() or\
            not kwargs['callback'].__annotations__['return'] == bool:
                raise TypeError('callback must return a bool')
            self.get_value = kwargs['callback']
            del kwargs['callback']
        else:
            self.get_value = lambda x, y: not y
        if 'value' in kwargs.keys():
            self.value = kwargs['value']
            del kwargs['value']
        else: 
            self.value = False
        kwargs['style'] = mode_styles.get_on_off(self.value)
        super().__init__(**kwargs)
    
    async def callback(self, interaction):
        # if get value is a coroutine, await it, otherwise just call it
        prev = self.value
        if inspect.iscoroutinefunction(self.get_value):
            self.value = await self.get_value(interaction, prev)
        else:
            self.value = self.get_value(interaction, prev)
        if self.value != prev:
            self.style = mode_styles.get_on_off(self.value) 
            if interaction.response.is_done():
                await interaction.message.edit(view=self.view)
            else:
                await interaction.response.edit_message(view=self.view)
        
    async def turn_on(self):
        self.value = True
        self.style = mode_styles.get_on_off(self.value) 
        await self.view.message.edit(view=self.view)

    async def turn_off(self):
        self.value = False
        self.style = mode_styles.get_on_off(self.value) 
        await self.view.message.edit(view=self.view)
