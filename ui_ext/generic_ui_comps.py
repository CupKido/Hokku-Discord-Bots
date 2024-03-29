import discord
from discord import app_commands
from discord.ui import View, button, Modal, Button, select
from discord.ext import commands
from discord import ui
from ui_ext.buttons.on_off_button import on_off_button

####################################
# A Generic Button, that lets you  #
# add a callback, and to store a   #
# value. send it's view as a       #
# parameter to the callback.       #
####################################
# callback arguments:              #
#       (interaction)              #
#       (button)                   #
#       (view)                     #
####################################
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
        if 'value' in kwargs.keys():
            self.value = kwargs['value']
        else:
            self.value = None
        if 'url' in kwargs.keys():
            self.the_url = kwargs['url']
        else:
            self.the_url = None
        self.callback = self.callbacks
        super().__init__(label=my_label, style=my_style, emoji=my_emoji, url=self.the_url)
    

    async def callbacks(self, interaction):
        if self.func is not None:
            await self.func(interaction, self, self.view)

    # def set_view(self, view):
    #     self.view = view

class Generic_Select(ui.Select):
    def __init__(self, **kwargs):
        if 'callback' in kwargs:
            self.func = kwargs['callback']
            kwargs.pop('callback')
        if 'placeholder' in kwargs.keys():
            my_placeholder = kwargs['placeholder']
        else:
            my_placeholder = None
        if 'min_values' in kwargs.keys():
            my_min_values = kwargs['min_values']
        else:
            my_min_values = None
        if 'max_values' in kwargs.keys():
            my_max_values = kwargs['max_values']
        else:
            my_max_values = None
        if 'options' in kwargs.keys():
            my_options = kwargs['options']
        else:
            my_options = []
        self.callback = self.callbacks
        super().__init__(placeholder=my_placeholder,
                          min_values=my_min_values,
                            max_values=my_max_values,
                              options=my_options)
    
    async def callbacks(self, interaction):
        if self.callback is not None:
            await self.func(interaction, self, self.view)

    # def set_view(self, view):
    #     self.view = view

class Generic_Selector(discord.ui.UserSelect):

    def set_callback(self, callback):
        self.func = callback

    def callbacks(self, interaction, select):
        if self.func is not None:
            self.func(interaction, select, self.view)



####################################
# A Generic View, that easily lets #
# you add buttons and selects,     #
# with callbacks, and more options #
####################################
# callback arguments:              #
#   button:                        #
#       (interaction)              #
#       (button)                   #
#       (view)                     #
#   select:                        #
#       (interaction)              #
#       (select)                   #
#       (view)                     #
####################################

class Generic_View(View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)
    
    def add_generic_button(self, label=None, style=None, emoji=None, callback=None, value=None, url=None):
        new_button = Generic_Button(label=label,
                                     style=style,
                                     emoji=emoji,
                                     callback=callback,
                                     value=value,
                                     url=url)
        self.add_item(new_button)

        return new_button
    
    def add_generic_select(self, **kwargs):
        if 'options' not in kwargs.keys():
            raise ValueError('options must be specified')
        options = kwargs['options']
        if 'max_values' not in kwargs.keys():
            kwargs['max_values'] = len(options)
        # create options
        options_list = [discord.SelectOption(**option) for option in options]
        kwargs['options'] = options_list
        new_select = Generic_Select(**kwargs)
        #new_select.set_view(self)
        self.add_item(new_select)

        return new_select
    
    def add_user_selector(self, placeholder=None, min_values = 0, max_values = None, callback=None):
        
        user_select = discord.ui.UserSelect(placeholder=placeholder,
                            min_values=min_values, max_values=max_values)
        user_select.callback = callback
        self.add_item(user_select)

    def add_on_off_button(self, **kwargs):
        new_button = on_off_button(**kwargs)
        self.add_item(new_button)
        return new_button

####################################
# A Generic Modal, that lets you   #
# add a callback, and to store a   #
# value.                           #
####################################
# callback arguments:              #
# (interaction)                    #
####################################

class Generic_Modal(ui.Modal):
    def set_callback(self, callback):
        self.on_submit = callback

    def set_value(self, value):
        self.value = value
        
    def add_input(self, label='Label', placeholder='', default='', max_length=None, required=False, long=False):
        if long:
            self.add_item(ui.TextInput(label=label,
                                        placeholder=placeholder,
                                        default=default,
                                        max_length=max_length,
                                        required=required,
                                        style=discord.TextStyle.paragraph))
        else:
            self.add_item(ui.TextInput(label=label, 
                                       placeholder=placeholder, 
                                       default=default, 
                                       max_length=max_length, 
                                       required=required, 
                                       style=discord.TextStyle.short))
        