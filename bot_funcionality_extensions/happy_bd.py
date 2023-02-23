import discord
from time import sleep
from datetime import datetime
import json
import random
from discord import app_commands
from threading import Thread
import schedule
from Interfaces.IGenericBot import IGenericBot
from DB_instances.generic_config_interface import server_config
from discord_modification_tools.channel_modifier import set_readonly
from ui_components_extension.HappyBD_ui import MyView, ConfigView, MyModal, SetBirthdayView, testView, userMview, configUserModal
from ui_components_extension.generic_ui_comps import Generic_Button, Generic_View
from discord.ui import Button, View, Modal, TextInput

with open('data_base/happy_bd_static_data.json', 'r') as f: 
    EMBED_URLS = json.load(f)["embed_urls"]

ACTIVATED = "activated"
GREETING_ROOM = "greeting_room_id"
BD_ROOM = "birthday_room_id"
#TODO:  קאטסטומיזציה מלאה של הברכות
BIRTHDAY_GREETINGS = [
    "Happy birthday! Have an amazing day!",
    "Wishing you a wonderful birthday!",
    "May your birthday be as special as you are!",
    "Have a fantastic birthday filled with lots of love and joy!",
]

class happy_bd:
    def __init__(self, client : IGenericBot):
        self.bot_client = client
        self.logger = client.get_logger()
        self.bot_client.add_on_ready_callback(self.start_schedular)
        self.birthday_data = self.load_bd_data()

                                #========commands=========#
        @client.tree.command(name="set_happy-birthday_channel", description="set your birthday")   
        async def birthday_set(ctx):   
            this_server_config = server_config(ctx.guild.id)
            this_server_config.set_params(BD_ROOM = ctx.channel.id)
            embed = discord.Embed(title = "Would you like to celebrate your birthday?", description = "Enter your date of birth to join" , color = 0x2ecc71)
            my_view = MyView()
            #TODO:לשנות בחינה לטוגל של הודעות יום הולדת
            my_view.set_callbacks(self.set_bd_button_callback, self.test_button_callback)
            await ctx.response.send_message(embed = embed ,view = my_view)  
        
        @client.tree.command(name="channel_config", description="to config a channel") 
        async def channel_config(ctx):
            embed = discord.Embed(title = "pick channel", color = 0x2ecc71)
            our_view = Generic_View()
            our_view.add_generic_button("greeting", discord.ButtonStyle.red, None, self.sendgreeingview) 
            our_view.add_generic_button("date_set", discord.ButtonStyle.red, None, self.sendBDview)
            await ctx.response.send_message(embed = embed , view = our_view)

        @client.tree.command(name="server_config", description="to config the bot") 
        async def toggle_bot(ctx):
            embed = discord.Embed(title = "this bot server settings:", color = 0x2ecc71)
            our_view = Generic_View()
            our_view.add_generic_button("deactivate toggle", discord.ButtonStyle.gray, None, self.deactive_button_click) 
            our_view.add_generic_button()
            await ctx.response.send_message(embed = embed , view = our_view)

        @client.tree.command(name="modify_user_birthday", description="to test") 
        async def test(ctx):
            embed = discord.Embed(title = "select user:", color = 0x2ecc71)
            our_view = userMview()
            our_view.set_callbacks(self.modufy_user_pannle)
            await ctx.response.send_message(embed = embed , view = our_view)    
        
        @client.tree.command(name="remove_birthday", description="to remove someone birthday") 
        async def remove_birthday(ctx, tag_user: str = None):
            tag_user = tag_user[1:2]
            tag_user = tag_user[:-1]
            self.remove_user(ctx.guild.id, tag_user)
            embed = discord.Embed(title = f"birthday has been removed ", color = 0x2ecc71)
            await ctx.response.send_message(tag_user, embed = embed)

        @client.tree.command(name="setup", description="to reset the rooms")         
        @app_commands.checks.bot_has_permissions(administrator = True)
        async def setup(ctx):
            await self.setup(ctx.guild)
            embed = discord.Embed(title = "new rooms are open!", color = 0x2ecc71)
            await ctx.response.send_message(embed = embed)

#===== Primary methods ====#
    async def send_birthday_message(self, guild_id, user):
        #TODO:  אפשרות להודעה רגילה או אמבד (לבחירת הלקוח)
        #TODO - כפתור שמצורף לברכות היום הולדת ומאפשר למשתמשים לברך את החוגג (הודעה רנדומלית מתוך המאגר או טופס? נשלח בצ'אנל או בהודעה פרטית?)
        try:
            this_server_config = server_config(guild_id)
            greeting = random.choice(BIRTHDAY_GREETINGS)   
            embed = discord.Embed(title = f"Happy Birthday {user.display_name}!", description = f'{greeting}', color = 0xFF8077)
            embed.set_thumbnail(url = random.choice(EMBED_URLS["happy"]))
            geeting_room = await self.bot_client.fetch_channel(this_server_config.get_param(GREETING_ROOM))
            await geeting_room.send(embed = embed)
        except Exception as e:
            print(f"Error sending birthday message: {str(e)}")    
    
    async def check_birthdays(self, guild_id, date):
        if guild_id not in self.birthday_data.keys():
            return
        
        for user_id in self.birthday_data[guild_id][(date)]:
                user = self.bot_client.get_user(user_id)
                if user:
                    await self.send_birthday_message(guild_id, user)
    
    async def sendBDview(self, interaction, button, view):
        await interaction.response.send_message(view = greetingRoomPick())

    async def senddb(self, interaction, select):
        return
                          
    async def sendgreeingview(self, interaction, button, view):
        nview = Generic_View()
        nview.add_generic_button("work", discord.ButtonStyle.red, None) 
        await interaction.response.send_message(view = nview)

    async def main_task(self):   
        for guild in self.bot_client.guilds:
            try:
                this_server_config = server_config(guild.id)
                if not this_server_config.get_param(ACTIVATED):
                    print("the bot is off")        
                elif this_server_config.get_param(GREETING_ROOM) is None:
                    print("need to set a greeting room")
                else:
                    await self.check_birthdays(guild.id, f"{datetime.now().day}.{datetime.now().month}") 
            except Exception as e:
                print(f"Error sending: {str(e)}") 

    async def start_schedular(self):
        # create a new thread to run the scheduler
        t = Thread(target=self.scheduler_functionality)
        t.start()

    def scheduler_functionality(self):
        schedule.every(24).hours.do(self.main_task)
        while True:
            schedule.run_pending()
            ########################################
            sleep(60) # 60 seconds
            ########################################

    async def deactive_button_click(self, interaction, button, view):
        this_server_config = server_config(interaction.guild.id)    

        active = not this_server_config.get_param("activated")
        this_server_config.set_params(activated = active)
        if active: 
            button.style = discord.ButtonStyle.red
            button.label="Deactivate"
        else: 
            button.style =  discord.ButtonStyle.green 
            button.label="Activate"
        await interaction.response.edit_message(view=view)

    async def setup(self, guild):        
        this_server_config = server_config(guild.id)     
        category = discord.utils.get(guild.categories, name='Happy Birthday')
        if category is None:   
            category = await guild.create_category("Happy Birthday", position=0)

        for channel in category.text_channels:
            await channel.delete()

        new_Set_Birthday_channel = await guild.create_text_channel("Set Birthday date", category = category)
        await self.send_setup_message(new_Set_Birthday_channel)
        await set_readonly(new_Set_Birthday_channel)

        new_greeting_channel = await guild.create_text_channel("party room", category = category)
        embed = discord.Embed(title = "Welcome to the party room!", description = "Birthday messages will be sent here when celebrating" , color = 0x2ecc71)
        await new_greeting_channel.send(embed = embed) 
        await set_readonly(new_greeting_channel)
        this_server_config.set_params(GREETING_ROOM = new_greeting_channel.id)   
        this_server_config.set_params(BD_ROOM = new_Set_Birthday_channel.id)

    async def send_setup_message(self, channel):   
        embed = discord.Embed(title = "Would you like to celebrate your birthday?", description = "\n Do you feel like celebrating your birthday with us? \n Enter your date of birth and we will surprise you with a wonderful greeting \n Note: \n You can only do it once. " , color = 0x2ecc71)
        my_view = MyView()
        my_view.set_callbacks(self.set_bd_button_callback, self.test_button_callback)
        await channel.send(embed = embed ,view = my_view)  


#=================== ui callbacks start =================#
    async def modufy_user_pannle(self, interaction, select):  
        new_view = Generic_View()
        new_view.add_generic_button("set date",discord.ButtonStyle.gray, None, await self.send_modify_panle(interaction, select.values[0]))
        new_view.add_generic_button("remove date",discord.ButtonStyle.gray, None, self.remove_user(interaction.guild, select.values[0].id))

        await interaction.response.send_message(f'You selected : {select.values[0]}, what to do with his date of birth?',view= new_view, ephemeral = True)
    
    async def send_modify_panle(self, interaction, user):   
        modal = configUserModal(title=f"set {user} birthday:")
        modal.set_callback(self.modify_panle_submit_callback)
        await interaction.response.send_modal(modal)

    async def modify_panle_submit_callback(self, interaction, user):
        if interaction.guild.id not in self.birthday_data.keys():
            self.birthday_data[interaction.guild.id] = {}
        #Dont enter invalid letters and numbers
        try:
            day = int(self.get_modal_value(interaction, 0))
            month = int(self.get_modal_value(interaction, 1)) 
        except:
            embed = discord.Embed(title = "חייב ליהיות מספר", description = f'יום הולדת לא הוגדר', color = 0xFF8077)
            embed.set_thumbnail(url = random.choice(EMBED_URLS["fail"]))
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return
        if month > 12 or day > 32 or month < 0 or day < 0:
            embed = discord.Embed(title = "התאריך לא קיים", description = f'יום הולדת לא הוגדר', color = 0xFF8077)
            embed.set_thumbnail(url = random.choice(EMBED_URLS["fail"]))
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return
        
        date = f"{day}.{month}"
        massge_content = f'יום ההולדת של המשתמש הוגדר ל{date}'
        for dates in self.birthday_data[interaction.guild.id]:
            for user_id in self.birthday_data[interaction.guild.id][dates]:
                if user_id == interaction.user.id:
                    massge_content = "התאריך שונה"
                    self.remove_user(interaction.guild.id, interaction.user.id)       
        self.save_birthday_data(interaction.guild.id ,interaction.user.id, date)

        embed = discord.Embed(title = "השינוי בוצע בהצלחה !", description = massge_content, color = 0x2ecc71)
        embed.set_thumbnail(url = random.choice(EMBED_URLS["success"]))
        await interaction.response.send_message(embed = embed, ephemeral = True)

    async def deactive_button_click(self, interaction, button):
        this_server_config = server_config(interaction.guild.id)    

        active = not this_server_config.get_param("activated")
        this_server_config.set_params(activated = active)
        return active
    
    async def set_greetings_button_click(self, interaction, button):
        this_server_config = server_config(interaction.guild.id)
        this_server_config.set_params(greeting_room_id = interaction.channel_id)
        await interaction.response.send_message("Greeting room set to " + str(interaction.channel_id))

    async def get_birthdays_button_click(self, interaction, button):
        #TODO: 
        """"
            רשימה שמכילה:
            שם משתמש, תאריך הלידה שלו, מזל, גיל (במידה ויש שנה) והתאריך שבו תאריך הלידה שלו התווסף למערכת.
            הרשימה מסודרת לפי התאריך שבו התווסף תאריך הלידה של המשתמש למערכת, המשתמש האחרון שהתווסף יופיע הכי למטה.
        """
        if interaction.guild.id not in self.birthday_data.keys():
            await interaction.response.send_message("No birthdays to show")
            return

        users_embed = discord.Embed(title='Users with Birthdays')
        for dates in self.birthday_data[interaction.guild.id]:
            for user_id in self.birthday_data[interaction.guild.id][dates]:
                user = await self.bot_client.fetch_user(user_id)
                users_embed.add_field(name= user.display_name, value= dates)
        await interaction.response.send_message(embed=users_embed, ephemeral=True)

    async def select_changed(self, interaction, select):
        this_server_config = server_config(interaction.guild.id)
        this_server_config.set_params(GREETING_ROOM = select.values[0].id)
        await interaction.response.send_message("Greeting room set to " + str(select.values[0]))       

    async def modal_submit_callback(self, interaction): 
        if interaction.guild.id not in self.birthday_data.keys():
            self.birthday_data[interaction.guild.id] = {}
        #Dont enter invalid letters and numbers
        try:
            day = int(self.get_modal_value(interaction, 0))
            month = int(self.get_modal_value(interaction, 1)) 
        except:
            embed = discord.Embed(title = "חייב ליהיות מספר", description = f'יום הולדת לא הוגדר', color = 0xFF8077)
            embed.set_thumbnail(url = random.choice(EMBED_URLS["fail"]))
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return
        if month > 12 or day > 32 or month < 0 or day < 0:
            embed = discord.Embed(title = "התאריך לא קיים", description = f'יום הולדת לא הוגדר', color = 0xFF8077)
            embed.set_thumbnail(url = random.choice(EMBED_URLS["fail"]))
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return
        
        date = f"{day}.{month}"
        massge_content = f'יום ההולדת שלך הוגדר ל{date}'
        for dates in self.birthday_data[interaction.guild.id]:
            for user_id in self.birthday_data[interaction.guild.id][dates]:
                if user_id == interaction.user.id:
                    massge_content = "אנא פנה למנהל השרת "
                    embed = discord.Embed(title = "לא ניתן לשנות תאריך!", description = massge_content, color = 0x2ecc71)
                    await interaction.response.send_message(embed = embed, ephemeral = True)
                    return 
                    self.remove_user(interaction.guild.id, interaction.user.id)       
        self.save_birthday_data(interaction.guild.id ,interaction.user.id, date)

        embed = discord.Embed(title = "השינוי בוצע בהצלחה !", description = massge_content, color = 0x2ecc71)
        embed.set_thumbnail(url = random.choice(EMBED_URLS["success"]))
        await interaction.response.send_message(embed = embed, ephemeral = True)

    async def test_button_callback(self, interaction, button):
        await self.main_task()
        await interaction.response.send_message("test ended!")

#TODO:Set @member's Birthday & Remove @member's Birthday

#=================== end ui callbacks =================#


#=================== Database management start =================#
    def change_date(self, guild_id, user_id, new_date):
        self.remove_user(self, guild_id, user_id)
        self.save_birthday_data(self, guild_id, user_id, new_date)

    async def set_bd_button_callback(self, interaction, button):
        #TODO: אופטימיזציה והודעות מותאמות אישית
        for dates in self.birthday_data[interaction.guild.id]:
            for user_id in self.birthday_data[interaction.guild.id][dates]:
                if user_id == interaction.user.id:
                    massge_content = "אנא פנה למנהל השרת "
                    embed = discord.Embed(title = "לא ניתן לשנות תאריך!", description = massge_content, color = 0x2ecc71)
                    await interaction.response.send_message(embed = embed, ephemeral = True)
                    return 
        modal = MyModal(title="set your birthday:")
        modal.set_callback(self.modal_submit_callback)
        await interaction.response.send_modal(modal)

    def get_modal_value(self, interaction, index): #
            return interaction.data['components'][index]['components'][0]['value']
    
    def load_guild_bd_data(self, guild_id):
        with open('data_base/happy_bd_dynamic_data.json', 'r') as birthdays_file:
            birthday_data = json.load(birthdays_file)
        if guild_id not in birthday_data.keys():
            return {}
        return birthday_data[guild_id]
    
    def load_bd_data(self):
        with open('data_base/happy_bd_dynamic_data.json', 'r') as birthdays_file:
            birthday_data = json.load(birthdays_file)
        #return birthday_data
        temp_dict = {}
        for guild_id in birthday_data.keys():
            temp_dict[int(guild_id)] = {}
            for date in birthday_data[guild_id].keys():
                temp_dict[int(guild_id)][date] = birthday_data[guild_id][date]
        return temp_dict
           
    def save_birthday_data(self, guild_id, user_id, date):
        try:
            # Makes sure the date exists
            if guild_id not in self.birthday_data.keys():
                self.birthday_data[guild_id] = {}

            if date in self.birthday_data[guild_id]:
                self.birthday_data[guild_id][date].append(user_id)
            else:
                self.birthday_data[guild_id][date] = [user_id]

            with open('data_base\happy_bd_dynamic_data.json', 'w') as file:
                json.dump(self.birthday_data, file)

        except Exception as e:
            print(f"Error saving data: {str(e)}")
        
    def remove_user(self, guild_id, user_id):
        #TODO: לבדוק למה לא מסיר תאריך, להוסיף החזר פולס אם תאריך לא נמצא
        try:
            if guild_id not in self.birthday_data.keys():
                return
            # check if date exists
            for dates in self.birthday_data[guild_id]:
                if user_id in dates:
                    self.birthday_data[guild_id][dates].remove(user_id)
                    with open('data_base\happy_bd_dynamic_data.json', 'w') as file:
                        json.dump(self.birthday_data, file)
        except Exception as e:
            print(f"Error removing user: {str(e)}")

    def look_for_user(self, guild_id, user_id):
        #TODO: לעבור על כל המשתמשים ולחפש יוזר ספציפי
        return
#=================== Database management end =================#


#========ui no callbacls=============#

class greetingRoomPick(View):
    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.public_thread, discord.ChannelType.text],
        placeholder='pick a greeting room',
        min_values = 1, max_values = 1,
    )
    async def select_callback(self, interaction, select):
        this_server_config = server_config(interaction.guild.id)  
        for c in select.values:
            new_greeting_channel = c  
        embed = discord.Embed(title = "Welcome to the party room!", description = "Birthday messages will be sent here when celebrating" , color = 0x2ecc71)
        this_server_config.set_params(GREETING_ROOM = new_greeting_channel.id)   
        await interaction.response.send_message(f'You selected : {new_greeting_channel}', ephemeral = True)
