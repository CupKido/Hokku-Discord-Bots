import discord
from discord.ui import Button, View, Modal, TextInput
import json


with open('data_Base/happy_bd_dynamic_data.json', 'r') as birthdays_file:
    birthday_data = json.load(birthdays_file)

class MyView(View):
    def __init__(self,**kwargs):
        super().__init__(**kwargs, timeout=None)
        
    def set_callbacks(self, set_bd_button_callback, test_button_callback):
        self.set_bd_button_callback = set_bd_button_callback
        self.test_button_callback = test_button_callback
    # set_bd_button
    @discord.ui.button(label= "set my birthday", style = discord.ButtonStyle.blurple)
    async def button_callback(self, interaction, button):
        await self.set_bd_button_callback(interaction, button)


    # test_button
    @discord.ui.button(label= "test now", style = discord.ButtonStyle.red)
    async def testbutton_callback(self, interaction, button):
        await self.test_button_callback(interaction, button)

        

class ConfigView(View):
    def __init__(self,**kwargs):
        super().__init__(**kwargs, timeout=None)

    def set_callbacks(self, deactive_button_click, set_greetings_button_click, get_birthdays_button_click, select_changed_callback):
        self.deactive_button_callback = deactive_button_click
        self.set_greetings_button_callback = set_greetings_button_click
        self.get_birthdays_button_callback = get_birthdays_button_click
        self.select_changed_callback = select_changed_callback
    # deactive_button
    @discord.ui.button(label="Deactivate", style = discord.ButtonStyle.red)
    async def activate_button(self, interaction, button):
        activated = await self.deactive_button_callback(interaction, button)
        if activated: 
            button.style =  discord.ButtonStyle.red
            button.label="Deactivate"
        else: 
            button.style =  discord.ButtonStyle.green 
            button.label="Activate"
        await interaction.response.edit_message(view=self)
  
    # set_greetings_button 
    @discord.ui.button(label="make this Channel Greetings Channel", style=discord.ButtonStyle.primary, row= 2)
    async def set_greetings_channel_button(self, interaction, button):
        await self.set_greetings_button_callback(interaction, button)

    # get_birthdays_button
    @discord.ui.button(label="List Users", style=discord.ButtonStyle.grey)
    async def list_users_button(self, interaction, button):
        await self.get_birthdays_button_callback(interaction, button)
       
    @discord.ui.select(placeholder = "pick a greeting room", min_values = 1, max_values = 1, cls = discord.ui.ChannelSelect)
    async def select_callback(self, interaction, select):
        await self.select_changed_callback(interaction, select)
        
          

class MyModal(Modal):
    def __init__(self, title):
        super().__init__(title=title)

        self.add_item(TextInput(label= "day:", placeholder="day", max_length= 2)) 
        self.add_item(TextInput(label= "month:", placeholder= "month", max_length= 2))
        self.add_item(TextInput(label= "Year:", placeholder= "Year", max_length= 4, min_length= 4, required= False))

    def set_callback(self, submit_callback):
        self.submit_callback = submit_callback

    async def on_submit(self, interaction: discord.Interaction):
        await self.submit_callback(interaction)


    #===== באלגן===#
    
Options = []

class testView(View):
    def __init__(self,**kwargs):
        super().__init__(**kwargs, timeout=None)

    @discord.ui.button(label="get dynamic model", style=discord.ButtonStyle.grey)
    async def test_button(self, interaction, button):
        modal = dynamicModel(button.label ,button.label, button.label, False)
        await interaction.response.send_modal(modal)
     
    @discord.ui.select(placeholder = "room", min_values = 1, max_values = 1,cls = discord.ui.UserSelect)  
    async def user_select(self, interaction: discord.Interaction, select):
        return        

class dynamicModel(Modal):
    def __init__(self, title, label, placeholder, required):
        super().__init__(title=title)

        self.add_item(TextInput(label=label, placeholder=placeholder, required=required))

class SetBirthdayView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, timeout=None)
        
    def set_callbacks(self, deactive_button_click):
        self.select_changed_callback = deactive_button_click
 
    @discord.ui.select(placeholder = "day", min_values = 1, max_values = 1,
        cls = discord.ui.UserSelect)
    async def select_callback(self, interaction, select):
        await self.select_changed_callback(interaction, select)

class userMview(View):
    def __init__(self,**kwargs):
        super().__init__(**kwargs, timeout=None)

    def set_callbacks(self, submit_callback):        
        self.submit_callback = submit_callback

    @discord.ui.select(
        cls=discord.ui.UserSelect,
        placeholder='pick a user',
        min_values = 1, max_values = 1,
    )
    async def select_callback(self, interaction, select):
        await self.submit_callback(interaction, select)

class configUserModal(Modal):
    def __init__(self, title):
        super().__init__(title=title)

        self.add_item(TextInput(label= "day:", placeholder="day", max_length= 2)) 
        self.add_item(TextInput(label= "month:", placeholder= "month", max_length= 2))
        self.add_item(TextInput(label= "Year:", placeholder= "Year", max_length= 4, min_length= 4, required= False))

    def set_callback(self, submit_callback):
        self.submit_callback = submit_callback

    async def on_submit(self, interaction: discord.Interaction):
        await self.submit_callback(interaction, self.title)