import discord
from discord.ext import commands, tasks
from discord import app_commands
import permission_checks
from Interfaces.BotFeature import BotFeature
from DB_instances.DB_instance import General_DB_Names
from bot_funcionality_extensions.OpenAI_features.gpt_wrapper import gpt_wrapper, role_options
from ui_components_extension.generic_ui_comps import Generic_Modal
import ui_components_extension.ui_tools as ui_tools
from dotenv import dotenv_values
config = dotenv_values('.env')
import io
import datetime
import asyncio

class gpt3_5_feature(BotFeature):
    users_collection = None
    servers_collection = None

    delete_after_minutes = 15
    slowmode_delay_seconds = 10
    # for feature db and server db
    OPEN_CHATS = "active_gpt_chats"

    # for server db
    GPT_CATEGORY = "gpt_category"

    # for user db
    ACTIVE_GPT_CHAT = "active_gpt_chat"
    GPT_TOKENS_USED = "gpt_tokens_used"
    GPT_CHAT_COST = "gpt_chat_cost"

    # feature item name
    FEATURE_NAME = "gpt3_5_data"

    def __init__(self, bot):
        super().__init__(bot)
        self.feature_collection = bot.db.get_collection_instance("gpt3_5_feature")
        self.servers_collection = bot.db.get_collection_instance(General_DB_Names.Servers_data.value)
        
        # decorator example
        # @bot.add_on_message_callback
        # async def call_on_message(message):
        #     await self.on_message(message)
        bot.add_on_message_callback(self.on_message)
        bot.add_on_ready_callback(self.start_cleaning_loop)

        @bot.tree.command(name="set_gpt_category", description="Starts a new chat with GPT 3_5")
        @app_commands.check(permission_checks.is_admin)
        async def set_gpt_category(interaction, category: discord.CategoryChannel):
            server_data = self.servers_collection.get(interaction.guild.id)
            server_data[self.GPT_CATEGORY] = category.id
            self.servers_collection.set(interaction.guild.id, server_data)
            await category.edit(overwrites={interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False)})
            await interaction.response.send_message("GPT category set to " + category.name, ephemeral=True)

        @bot.tree.command(name="new_gpt_chat", description="Starts a new chat with GPT 3_5")
        async def new_gpt_chat(interaction):
            server_data = self.servers_collection.get(interaction.guild.id)

            # check if server has a GPT category
            if self.GPT_CATEGORY not in server_data.keys() or server_data[self.GPT_CATEGORY] is None:
                await interaction.response.send_message("server has no GPT category.", ephemeral=True)
                return
            
            user_data = self.feature_collection.get(interaction.user.id)
            # check if user already has an active GPT chat
            if self.ACTIVE_GPT_CHAT in user_data.keys():
                if user_data[self.ACTIVE_GPT_CHAT] is not None:
                    await interaction.response.send_message("you already have an active GPT chat.", ephemeral=True)
                    # add option to switch to the active chat to this server
                    return
                
            
            # create new chat with permissions for the user
            category = interaction.guild.get_channel(server_data[self.GPT_CATEGORY])
            if category is None:
                await interaction.response.send_message("server has no GPT category.", ephemeral=True)
                server_data[self.GPT_CATEGORY] = None
                self.servers_collection.set(interaction.guild.id, server_data)
                return
            channel = await category.create_text_channel(
                name=interaction.user.name, 
                topic=str(interaction.user.id),
                slowmode_delay=self.slowmode_delay_seconds, 
                overwrites={
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), 
                    interaction.user: discord.PermissionOverwrite(read_messages=True), 
                    bot.user: discord.PermissionOverwrite(read_messages=True),
                }
            )
            self.add_active_gpt_channel(channel.id, user_data, server_data)
            await channel.send("starting new GPT chat with " + interaction.user.mention)
            await interaction.response.send_message("new GPT chat created.", ephemeral=True)

        @bot.tree.command(name="close_gpt_chat", description="Ends your active GPT chat")
        async def close_gpt_chat(interaction):
            user_data = self.feature_collection.get(interaction.user.id)
            server_data = self.servers_collection.get(interaction.guild.id)
            if self.ACTIVE_GPT_CHAT not in user_data.keys() or user_data[self.ACTIVE_GPT_CHAT] is None:
                await interaction.response.send_message("you have no active GPT chat.", ephemeral=True)
                return
            
            await self.send_transcript(user_data)
            channel = self.bot_client.get_channel(user_data[self.ACTIVE_GPT_CHAT])
            await channel.delete()
            self.remove_active_gpt_channel(user_data[self.ACTIVE_GPT_CHAT], user_data, server_data)
            await interaction.response.send_message("GPT chat closed.", ephemeral=True)
            
        @bot.tree.command(name="ask_gpt", description="Ask GPT 3_5 a question (privately)")
        async def ask_gpt(interaction):
            question_modal = Generic_Modal(title='Ask ChatGPT')
            question_modal.add_input(label="Question", 
                                    placeholder="What would you like to ask ChatGPT?", 
                                    required=True,
                                    long=True, max_length=4000)
            question_modal.set_callback(callback=self.ask_GPT_modal_callback)
            await interaction.response.send_modal(question_modal)

        @bot.tree.command(name="public_gpt_chat", description="make your active GPT chat public")
        async def public_gpt_chat(interaction):
            user_data = self.feature_collection.get(interaction.user.id)
            if self.ACTIVE_GPT_CHAT not in user_data.keys() or user_data[self.ACTIVE_GPT_CHAT] is None:
                await interaction.response.send_message("you have no active GPT chat.", ephemeral=True)
                return
            
            channel = self.bot_client.get_channel(user_data[self.ACTIVE_GPT_CHAT])
            await channel.edit(overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
            })
            await interaction.response.send_message("GPT chat made public.", ephemeral=True)

        @bot.tree.command(name="private_gpt_chat", description="make your active GPT chat private")
        async def private_gpt_chat(interaction):
            user_data = self.feature_collection.get(interaction.user.id)
            if self.ACTIVE_GPT_CHAT not in user_data.keys() or user_data[self.ACTIVE_GPT_CHAT] is None:
                await interaction.response.send_message("you have no active GPT chat.", ephemeral=True)
                return
            
            channel = self.bot_client.get_channel(user_data[self.ACTIVE_GPT_CHAT])
            await channel.edit(overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
            })
            await interaction.response.send_message("GPT chat made private.", ephemeral=True)

    def add_active_gpt_channel(self, channel_id, user_data, server_data):
        # save channel id to user db, server db and feature db
        # feature db
        feature_data = self.feature_collection.get(self.FEATURE_NAME)
        if self.OPEN_CHATS not in feature_data.keys() or feature_data[self.OPEN_CHATS] is None or type(feature_data[self.OPEN_CHATS]) is not list:
            feature_data[self.OPEN_CHATS] = [channel_id]
        else:
            feature_data[self.OPEN_CHATS].append(channel_id)

        # server db
        if self.OPEN_CHATS not in server_data.keys() or server_data[self.OPEN_CHATS] is None or type(server_data[self.OPEN_CHATS]) is not list:
            server_data[self.OPEN_CHATS] = [channel_id]
        else:
            server_data[self.OPEN_CHATS].append(channel_id)
        

        # user db
        user_data[self.ACTIVE_GPT_CHAT] = channel_id

        # save data
        self.feature_collection.set(self.FEATURE_NAME, feature_data)
        self.feature_collection.set(user_data['_id'], user_data)
        self.servers_collection.set(server_data['_id'], server_data)

    async def send_transcript(self, user_data):
        # send transcript to user
        # get channel
        if self.ACTIVE_GPT_CHAT not in user_data.keys() or user_data[self.ACTIVE_GPT_CHAT] is None:
            return
        
        channel = self.bot_client.get_channel(user_data[self.ACTIVE_GPT_CHAT])
        # get user
        user = self.bot_client.get_user(int(user_data['_id']))
        # get messages
        data = []
        async for message in channel.history(limit=None):
            data.append(message.author.name + ": " + message.content +
                         ('\n' if len(message.embeds) > 0 else '') +
                           '\n'.join(x.description for x in message.embeds))
        data.reverse()
        await user.send(file=discord.File(io.BytesIO('\n'.join(data).encode()), filename=str(datetime.datetime.today()) + '_transcript.txt'))

    def remove_active_gpt_channel(self, channel_id, user_data, server_data):
        # remove channel id from user db, server db and feature db
        # feature db
        feature_data = self.feature_collection.get(self.FEATURE_NAME)
        if self.OPEN_CHATS in feature_data.keys() and feature_data[self.OPEN_CHATS] is not None and type(feature_data[self.OPEN_CHATS]) is list:
            feature_data[self.OPEN_CHATS].remove(channel_id)

        # server db
        if self.OPEN_CHATS in server_data.keys() and server_data[self.OPEN_CHATS] is not None and type(server_data[self.OPEN_CHATS]) is list:
            server_data[self.OPEN_CHATS].remove(channel_id)
        

        # user db
        user_data[self.ACTIVE_GPT_CHAT] = None

        # save data
        self.feature_collection.set(self.FEATURE_NAME, feature_data)
        self.feature_collection.set(user_data['_id'], user_data)
        self.servers_collection.set(server_data['_id'], server_data)

    async def load_user_history(self, channel, amount):
        user_history = []
        async for chat_message in channel.history(limit=amount):
            if chat_message.author == self.bot_client.user:
                if len(chat_message.embeds) == 0:
                    continue
                user_history.append((role_options.assistant, chat_message.embeds[0].description))
            else:
                user_history.append((role_options.user , chat_message.content))
        user_history.reverse()
        return user_history
    
    
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # check if server has an active GPT chat
        server_data = self.servers_collection.get(message.guild.id)
        if self.OPEN_CHATS not in server_data.keys() or server_data[self.OPEN_CHATS] is None or type(server_data[self.OPEN_CHATS]) is not list:
            return

        # check if message is in an active GPT chat
        if message.channel.id not in server_data[self.OPEN_CHATS]:
            return
        
        # the message is indeed in an active GPT chat, intended for GPT 3_5
        # change permissions of channel to only allow the bot to send messages
        await message.channel.edit(overwrites={message.author: discord.PermissionOverwrite(send_messages=False),})

        # load user chat history
        user_history = await self.load_user_history(message.channel, 7)
        
        # forward message to GPT 3_5 and return response
        used_model = gpt_wrapper.supported_models.gpt_3_5_turbo
        please_wait_message = await message.channel.send("Please wait while I ask GPT 3.5...")
        try:
            response, tokens_used = await gpt_wrapper.get_response_with_history(user_history, 
                                                                                used_model, 
                                                                                config["OPENAI_KEY"])
            await please_wait_message.delete()
            #print(response)
            # prepare response to user
            response_embed = self.get_response_embed(response)
            embeds=[response_embed]
            # add button to show chat history
            user_mention = message.author.mention
            # send response to user
            await message.channel.send(content=user_mention,embeds=embeds)

            # save tokens used
            user_data = self.feature_collection.get(message.author.id)
            if self.GPT_CHAT_COST not in user_data.keys() or type(user_data[self.GPT_CHAT_COST]) is not float:
                user_data[self.GPT_CHAT_COST] = gpt_wrapper.tokens_to_dollars(tokens_used, used_model)
            else:
                user_data[self.GPT_CHAT_COST] += gpt_wrapper.tokens_to_dollars(tokens_used, used_model)
            
            self.feature_collection.set(message.author.id, user_data)
        except Exception as e:
            await please_wait_message.delete()
            await message.channel.send("GPT 3.5 is not responding. Please try again later.")
            print(e)
        
        # change permissions of channel to allow user to send messages
        await message.channel.edit(overwrites={message.author: discord.PermissionOverwrite(send_messages=True),})

        

    async def ask_GPT_modal_callback(self, interaction):
        message = ui_tools.get_modal_value(interaction, 0)
        question_embed = discord.Embed(title=f"Your question:", description=message, color=0x00ff00)
        await interaction.response.send_message("Please wait while I ask GPT 3.5...", ephemeral=True)
        try:
            used_model = gpt_wrapper.supported_models.gpt_3_5_turbo
            response, tokens_used = await gpt_wrapper.get_response(message, used_model, config["OPENAI_KEY"])
            
            response_embed = self.get_response_embed(response)
            await interaction.followup.send(embeds=[question_embed, response_embed], ephemeral=True)

            # save tokens used
            user_data = self.feature_collection.get(interaction.user.id)
            if self.GPT_CHAT_COST not in user_data.keys() or type(user_data[self.GPT_CHAT_COST]) is not float:
                user_data[self.GPT_CHAT_COST] = gpt_wrapper.tokens_to_dollars(tokens_used, used_model)
            else:
                user_data[self.GPT_CHAT_COST] += gpt_wrapper.tokens_to_dollars(tokens_used, used_model)
            
            self.feature_collection.set(interaction.user.id, user_data)
            
        except Exception as e:
            await interaction.followup.send("GPT 3.5 is not responding. Please try again later.", embed=question_embed, ephemeral=True)
            print(e)
        
    
    
    def get_response_embed(self, response):
        response_embed = discord.Embed(title=f"GPT3.5\'s response:", description=str(response), color=0x00ff00)
        return response_embed

    async def start_cleaning_loop(self):
        self.clean_dead_gpt_chats.start()

    @tasks.loop(minutes=10)
    async def clean_dead_gpt_chats(self):
        # clean dead gpt chats
        # get all open chats
        feature_data = self.feature_collection.get(self.FEATURE_NAME)
        if self.OPEN_CHATS not in feature_data.keys() or feature_data[self.OPEN_CHATS] is None or type(feature_data[self.OPEN_CHATS]) is not list:
            return
        open_gpt_chats = feature_data[self.OPEN_CHATS]
        now = None
        minutes_ago= None
        for chat_id in open_gpt_chats:
            channel = self.bot_client.get_channel(chat_id)
            if channel is None:
                continue
            # get last message
            last_message = None
            async for the_last_message in channel.history(limit=1):
                last_message = the_last_message
            # print("last_message", last_message.created_at.tzinfo)
            if now is None:
                now = datetime.datetime.now(last_message.created_at.tzinfo)
                minutes_ago = now - datetime.timedelta(minutes=self.delete_after_minutes)
            # print("now", now.tzinfo)
            print(last_message.created_at, "<=", minutes_ago)
            if last_message.created_at <= minutes_ago:
                # remove channel id from user db, server db and feature db
                user_id = channel.topic
                user_data = self.feature_collection.get(user_id)
                server_id = channel.guild.id
                server_data = self.servers_collection.get(server_id)
                await self.send_transcript(user_data)
                self.remove_active_gpt_channel(chat_id, user_data, server_data)
                await channel.delete()
        pass