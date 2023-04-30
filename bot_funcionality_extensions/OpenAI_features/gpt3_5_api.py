import discord
from discord import app_commands
from discord.ext import commands
import openai
from Interfaces.BotFeature import BotFeature
# from DB_instances.per_id_db import per_id_db
#from DB_instances.generic_config_interface import server_config
from DB_instances.DB_instance import General_DB_Names
from ui_components_extension.generic_ui_comps import Generic_View, Generic_Modal
import ui_components_extension.ui_tools as ui_tools
import permission_checks
import aiohttp
import json
from dotenv import dotenv_values
config = dotenv_values('.env')



per_id_db = None
server_config = None
class gpt3_5_api(BotFeature):
    openai_key = config["OPENAI_KEY"]

    GPT_USER_HISTORY = 'gpt_user_history'
    GPT_REPLIES_HIDDEN = "gpt_replies_hidden"

    GPT_CHANNELS = 'gpt_channels'

    def __init__(self, bot):
        global per_id_db, server_config
        super().__init__(bot)
        openai.api_key = self.openai_key
        per_id_db = bot.db.get_collection_instance('ChatGPTFeature').get_item_instance
        server_config = bot.db.get_collection_instance(General_DB_Names.Servers_data.value).get_item_instance
        @bot.tree.command(name='gpt_menu', description='open GPT actions menu')
        async def GPT_menu_command(interaction : discord.Interaction):
            # make sure openai key is set
            if self.openai_key is None:
                await interaction.response.send_message("OpenAI key not found. Please contact the bot owner")
                return
            
            await self.present_GPT_menu(interaction)
            

        # command for adding gpt text channels
        @bot.tree.command(name='add_gpt_channel', description='add a channel to the list of channels that can be used for GPT3.5')
        @app_commands.check(permission_checks.is_admin) 
        async def add_gpt_channel_command(interaction : discord.Interaction, channel : discord.TextChannel):
            if self.openai_key is None:
                await interaction.response.send_message("OpenAI key not found", ephemeral=True)
                return
            this_server_config = server_config(interaction.guild.id)
            gpt_channels = this_server_config.get_param(self.GPT_CHANNELS)
            if gpt_channels is None or type(gpt_channels) is not list:
                gpt_channels = []
            if channel.id in gpt_channels:
                await interaction.response.send_message("channel already in list", ephemeral=True)
                return
            gpt_channels.append(channel.id)
            this_server_config.set_params(gpt_channels=gpt_channels)
            await interaction.response.send_message(f"added {channel.mention} to list of GPT allowed channels", ephemeral=True)

        # command for removing gpt text channels
        @bot.tree.command(name='remove_gpt_channel', description='remove a channel from the list of channels that can be used for GPT3.5')
        @app_commands.check(permission_checks.is_admin)
        async def remove_gpt_channel_command(interaction : discord.Interaction, channel : discord.TextChannel):
            if self.openai_key is None:
                await interaction.response.send_message("OpenAI key not found", ephemeral=True)
                return
            this_server_config = server_config(interaction.guild.id)
            gpt_channels = this_server_config.get_param(self.GPT_CHANNELS)
            if gpt_channels is None or type(gpt_channels) is not list:
                gpt_channels = []
            if channel.id not in gpt_channels:
                await interaction.response.send_message("channel already not in list", ephemeral=True)
                return
            gpt_channels.remove(channel.id)
            this_server_config.set_params(gpt_channels=gpt_channels)
            await interaction.response.send_message(f"removed {channel.mention} from list of GPT allowed channels", ephemeral=True)

            
    async def present_GPT_menu(self, interaction):
        # make sure command is used in a channel that is allowed for GPT3.5
        is_gpt_channel = False
        this_server_config = server_config(interaction.guild.id)
        gpt_channels = this_server_config.get_param(self.GPT_CHANNELS)
        if gpt_channels is None or type(gpt_channels) is not list:
            gpt_channels = []
        if interaction.channel.id not in gpt_channels and gpt_channels != []:
            await interaction.response.send_message("GPT is not allowed in this channel, please go to <#"+str(gpt_channels[0])+">", ephemeral=True)
            return
        elif gpt_channels != []:
            is_gpt_channel = True

        # create view
        view = Generic_View()
        view.add_generic_button(label='ask GPT3.5', style=discord.ButtonStyle.primary, callback=self.ask_GPT3_5_button_click)
        view.add_generic_button(label='Show GPT history', style=discord.ButtonStyle.secondary, callback=self.show_history_button_click)
        view.add_generic_button(label='clear GPT history', style=discord.ButtonStyle.danger, callback=self.clear_GPT_history_button_click)
        view.add_generic_button(label='flip visibility', style=discord.ButtonStyle.secondary, callback=self.flip_visibility_button_click)
        view.add_generic_button(label='open website', style=discord.ButtonStyle.secondary, url='https://chat.openai.com/chat')
        # create embed that explains what GPT3.5 is and details the options
        embed = discord.Embed(title="ChatGPT menu", 
                                description="GPT3.5 is a machine learning model that can generate text based on a prompt. It is a very powerful tool." +
                                "\n\n**Options:**" + 
                                "\n**ask GPT3.5** - send ChatGPT a question/message and receive a response" +
                                "\n**Show GPT history** - show your ChatGPT history" +
                                "\n**clear GPT history** - clear your ChatGPT history" + 
                                "\n**open website** - open the website where you can use ChatGPT",
                                color=0x00ff00)
        # send embed and view
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def ask_GPT3_5(self, message, user_id=None):
        if user_id is not None:
            member_db = per_id_db(user_id)
            user_history = member_db.get_param(self.GPT_USER_HISTORY)
            if user_history is None or type(user_history) is not list:
                user_history = []

            user_history.append({"role":"user", "content" : message})
            while(len(str(user_history)) > 3500):
                user_history = user_history[1:]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=user_history
            )
            user_history.append({"role":"assistant", "content" : response["choices"][0]["message"]["content"]})
            if len(user_history) > 10:
                user_history = user_history[1:]
            member_db.set_params(gpt_user_history=user_history)
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user", "content" : message}]
            )
        
        return response["choices"][0]["message"]["content"]

    async def ask_GPT3_5_and_respond(self, message, interaction, is_gpt_channel):
        member_db = per_id_db(interaction.user.id)
        user_history = member_db.get_param(self.GPT_USER_HISTORY)
        if user_history is None or type(user_history) is not list:
            user_history = []

        user_history.append({"role":"user", "content" : message})
        while(len(str(user_history)) > 3500):
            user_history = user_history[1:]

        chatgpt_url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + config["OPENAI_KEY"]  # Replace with your actual API key
        }

        data = {
            "model" : "gpt-3.5-turbo",
            "messages": user_history
        }
        async with aiohttp.ClientSession() as session:
            #print('getting image:\t' + prompt)
            async with session.post(chatgpt_url, headers=headers, data=json.dumps(data)) as response:
                if response.status == 200:
                    response_json = await response.json()
                    answer = response_json["choices"][0]["message"]["content"]
                else:
                    await interaction.response.send_message("Sorry, we have encountered an error. Please try again", ephemeral=True)
                    return
                user_history.append({"role":"assistant", "content" : answer})
                if len(user_history) > 10:
                    user_history = user_history[1:]
                member_db.set_params(gpt_user_history=user_history)

                # prepare response to user
                question_embed = discord.Embed(title=f"Your question:", description=message, color=0x00ff00)
                response_embed = discord.Embed(title=f"GPT3.5\'s response:", description=answer, color=0x00ff00)
                embeds=[question_embed, response_embed]
                # add button to show chat history
                answer_view = Generic_View()
                answer_view.add_generic_button(label="Reply", style=discord.ButtonStyle.green, callback=self.ask_GPT3_5_button_click)
                answer_view.add_generic_button(label="Show chat history", style=discord.ButtonStyle.primary, callback=self.show_history_button_click)
                user_mention = interaction.user.mention
                invisible = member_db.get_param(self.GPT_REPLIES_HIDDEN)
                if invisible is None:
                    invisible = True
                # send response to user
                await interaction.followup.send(content=user_mention,embeds=embeds, view=answer_view, ephemeral=invisible)
                return answer

    async def show_history_button_click(self, interaction, button, view):
        member_db = per_id_db(interaction.user.id)
        user_history = member_db.get_param(self.GPT_USER_HISTORY)
        if user_history is None or type(user_history) is not list:
            user_history = []
        if len(user_history) == 0:
            await interaction.response.send_message("You have no history with ChatGPT", ephemeral=True)
            return
        embeds = []
        i = 0
        if len(user_history) > 10:
            user_history = user_history[-10:]
        for message in user_history:
            if i == 10:
                break
            if message["role"] == "user":
                author = "You"
            else:
                author = "GPT3.5"
            embed = discord.Embed(title=f"{author} said:", description=message["content"], color=0x11ffaa)
            embed.set_footer(text='_______________________________________________________________________________')
            embeds.append(embed)
            i += 1
        await interaction.response.send_message(content=interaction.user.mention + '\nYour chat history with ChatGPT:', embeds=embeds, ephemeral=True)
        return
    
    async def clear_history_confirmation_button_click(self, interaction, button, view):
        if button.label == "Confirm":
            member_db = per_id_db(interaction.user.id)
            member_db.set_params(gpt_user_history=[])
            embed = discord.Embed(title="Chat history cleared", description="Your chat history has been cleared", color=0x00ff00)
            await interaction.response.edit_message(view=None, embeds=[embed])
            
        else:
            embed = discord.Embed(title="Cancelled", description="Your chat history has not been cleared", color=0x00ff00)
            await interaction.response.edit_message(view=None, embeds=[embed])
            
    async def ask_GPT3_5_button_click(self, interaction, button, view): #
        # Send user a Modal to ask for a question
        question_modal = Generic_Modal(title='Ask ChatGPT')
        question_modal.add_input(label="Question", 
                                 placeholder="What would you like to ask ChatGPT?", 
                                 required=True,
                                 long=True, max_length=3400)
        question_modal.set_callback(callback=self.ask_GPT3_5_modal_callback)
        await interaction.response.send_modal(question_modal)
    
    async def ask_GPT3_5_modal_callback(self, interaction):
        # Get the question from the modal
        message = ui_tools.get_modal_value(interaction, 0)
        # make sure openai key is set
        if self.openai_key is None:
            await interaction.response.send_message("OpenAI key not found")
            return
        
        # make sure command is used in a channel that is allowed for GPT3.5
        is_gpt_channel = False
        this_server_config = server_config(interaction.guild.id)
        gpt_channels = this_server_config.get_param(self.GPT_CHANNELS)
        if gpt_channels is None or type(gpt_channels) is not list:
            gpt_channels = []
        if interaction.channel.id not in gpt_channels and gpt_channels != []:
            await interaction.response.send_message("GPT is not allowed in this channel")
            return
        elif gpt_channels != []:
            is_gpt_channel = True
        
        # make sure message is not too long
        if len(message) > 3500:
            await interaction.response.send_message("message too long, max 3500 characters")
            return
        
        # send message to GPT3.5 and get response
        await interaction.response.send_message("sending to ChatGPT, wait a few seconds for response...", ephemeral=True)
        await self.ask_GPT3_5_and_respond(message, interaction, is_gpt_channel)
        
    async def flip_visibility_button_click(self, interaction, button, view): #
        # get current visibility
        member_db = per_id_db(interaction.user.id)
        current_visibility = member_db.get_param(self.GPT_REPLIES_HIDDEN)
        if current_visibility is None:
            current_visibility = True
        # flip visibility
        member_db.set_params(gpt_replies_hidden=not current_visibility)
        await interaction.response.send_message("Your GPT3.5 replies are now " + ("hidden" if not current_visibility else "visible"), ephemeral=True)

    async def clear_GPT_history_button_click(self, interaction, button, view):
        confirmation_embed = discord.Embed(title=f"Are you sure you want to clear your chat history?", description="This action cannot be undone", color=0x00ff00)
        confiramtion_view = Generic_View()
        confiramtion_view.add_generic_button(label="Confirm", style=discord.ButtonStyle.primary, callback=self.clear_history_confirmation_button_click)
        confiramtion_view.add_generic_button(label="Cancel", style=discord.ButtonStyle.danger, callback=self.clear_history_confirmation_button_click)
        await interaction.response.send_message(embed=confirmation_embed, view=confiramtion_view, ephemeral=True)

    async def open_website_button_click(self, interaction, button, view):
        embed= discord.Embed(title=f"Open ChatGPT website", url="https://chat.openai.com/chat")
        await interaction.response.send_message(embed=embed, ephemeral=True)