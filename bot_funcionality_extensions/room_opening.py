import discord
import discord
from discord import app_commands
from discord.ext import commands
import ui_components_extension.views as views
import ui_components_extension.modals as modals
import asyncio
import threading
import tasks
from DB_instances.server_config_interface import server_config
import discord_modification_tools.channel_modifier as channel_modifier
import json
import requests

class room_opening:
    def __init__(self, client):
        self.bot_client = client
        self.logger = client.get_logger()
        self.active_channels = {}
        self.logger.log('room_opening extension loading...')
        self.bot_client.add_on_ready_callback(self.initialize_buttons)
        self.bot_client.add_on_ready_callback(self.initialize_active_channels)
        self.bot_client.add_on_session_resumed_callback(self.initialize_buttons)
        self.bot_client.add_on_session_resumed_callback(self.initialize_active_channels)
        self.bot_client.add_on_voice_state_update_callback(self.vc_state_update)
        self.bot_client.add_on_guild_channel_delete_callback(self.on_guild_channel_delete_callback)
        
        @client.tree.command(name = 'choose_creation_channel', description='choose a channel for creationg new voice channels')
        async def choose_creation_channel(interaction: discord.Interaction, channel : discord.TextChannel):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message('you are not an admin', ephemeral = True)
                return
            
            try:

                # get server config
                this_server_config = server_config(interaction.guild.id)

                if channel.id == this_server_config.get_creation_vc_channel():
                    await interaction.response.send_message('this channel is already set as creation channel', ephemeral = True)
                    return

                # check if channel is set, and if so, remove readonly and delete static message
                if this_server_config.get_creation_vc_channel() != ' ':
                    await self.clean_previous_channel(this_server_config)

                # set announcement channel
                await self.initialize_creation_channel(channel, this_server_config)
                await interaction.response.send_message(f'\"{channel.name}\" was set as vc creation channel', ephemeral = True)

            except Exception as e:
                self.log(str(e))
                await interaction.response.send_message('error', ephemeral = True)

        @client.tree.command(name = 'set_closing_timer', description='set a timer for closing a vc after creation in case no one joins')
        async def set_closing_timer(interaction: discord.Interaction, timer : int):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message('you are not an admin', ephemeral = True)
                return
            try:
                # get server config
                this_server_config = server_config(interaction.guild.id)

                # set timer
                this_server_config.set_vc_closing_timer(timer)
                await interaction.response.send_message(f'\"{timer}\" was set as closing timer', ephemeral = True)

            except Exception as e:
                self.log(str(e))
                await interaction.response.send_message('error', ephemeral = True) 

        @client.tree.command(name = 'choose_static_message', description='choose a static message for vc creation channel')
        async def choose_static_message(interaction: discord.Interaction, message : str):
            #check if user is admin
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message('you are not an admin', ephemeral = True)
                return
            try:
                # get server config
                this_server_config = server_config(interaction.guild.id)

                #check if channel exists
                try:
                    channnel = interaction.guild.fetch_channel(this_server_config.get_creation_vc_channel())
                except:
                    this_server_config.set_creation_vc_channel(' ')

                # check if channel is set, and if not, exits
                if this_server_config.get_creation_vc_channel() == ' ':
                    await interaction.response.send_message('please set a creation channel first', ephemeral = True)
                    return
                await self.clean_previous_static_message(this_server_config)
                this_server_config.set_static_message(message)

                # set message
                await interaction.response.send_message(f'\"{message}\" was set as static message', ephemeral = True)

                # get creation channel
                await self.initialize_static_message(this_server_config)


            except Exception as e:
                self.log(str(e))
                await interaction.response.send_message('error', ephemeral = True)
        
        @client.tree.command(name = 'choose_vc_for_vc', description='set a channel for vc creation')
        async def choose_vc_for_vc(interaction: discord.Interaction, channel : discord.VoiceChannel):
            try:
                # get server config
                this_server_config = server_config(interaction.guild.id)

                # set channel
                this_server_config.set_vc_for_vc(channel.id)

                await interaction.response.send_message(f'\"{channel.name}\" was set as vc for vc', ephemeral = True)

            except Exception as e:
                self.log(str(e))
                await interaction.response.send_message('error', ephemeral = True)

    async def vc_state_update(self, member, before, after):
        # check if before channel is empty
        # print(f'{member} moved from {before.channel} to {after.channel}')
        
        if before.channel is not None and len(before.channel.members) == 0:
            # check if channel is active
            if before.channel.guild.id in self.active_channels.keys() and before.channel.id in self.active_channels[before.channel.guild.id].values():
                # delete channel
                try:
                    self.active_channels[before.channel.guild.id].pop(
                    [ x for x in self.active_channels[before.channel.guild.id].keys() 
                    if self.active_channels[before.channel.guild.id][x] == before.channel.id][0] )
                    await before.channel.delete()
                except discord.errors.NotFound as e:
                    pass
                except Exception as e:
                    self.log('Error deleting channel due to error: ' + str(e))
                    self.load_active_channels()
                    return
                self.save_active_channels()
                self.log_guild(f'deleted {before.channel.name} channel because it was empty', before.channel.guild)
        try:
        # check if after channel is vc for vc
            if after.channel is None:
                return
            this_server_config = server_config(after.channel.guild.id)
            if after.channel is not None and after.channel.id == this_server_config.get_vc_for_vc():
                if after.channel.guild.id not in self.active_channels.keys():
                    self.active_channels[int(after.channel.guild.id)] = {}
                new_channel = await after.channel.category.create_voice_channel(name = f'{member.name}\'s Office')
                await channel_modifier.give_management(new_channel, member)
                await member.move_to(new_channel)
                self.active_channels[after.channel.guild.id][member.id] = new_channel.id
                self.save_active_channels()
            self.log(self.active_channels)
        except discord.errors.HTTPException as e:
            self.log_guild('Error creating channel due to error: ' + str(e), after.channel.guild)
            self.load_active_channels()
            return

    async def initialize_buttons(self):
        '''
        restarts all active buttons on all creatrion channels
        '''
        self.log('initializing buttons')

        # get all guilds
        for guild in self.bot_client.guilds:
            # get all channels
            this_server_config = server_config(guild.id)
            creation_channel = this_server_config.get_creation_vc_channel()
            static_message = this_server_config.get_static_message()
            static_message_id = this_server_config.get_static_message_id()
            if  creation_channel != ' ' and static_message != ' ' and static_message_id != ' ':
                creation_channel = self.bot_client.get_channel(int(this_server_config.get_creation_vc_channel()))
                if creation_channel is not None:
                    async for msg in creation_channel.history(limit=100):
                        if msg.author == self.bot_client.user:
                            if msg.id == static_message_id:
                                new_msg = await msg.edit(content = msg.content, view = views.get_InstantButtonView(self))
                                this_server_config.set_static_message_id(new_msg.id)
                                self.log('button initialized for ' + guild.name)

    async def on_guild_channel_delete_callback(self, channel):
        if channel.guild.id in self.active_channels.keys() and channel.id in self.active_channels[channel.guild.id].values():
            self.active_channels[channel.guild.id].pop(
                [x for x in self.active_channels[channel.guild.id].keys() if self.active_channels[channel.guild.id][x] == channel.id][0]
            )
            self.log_guild(f'deleted {channel.name} channel from active channels because it was deleted', channel.guild)
            self.save_active_channels()

    async def edit_channel_button(self, interaction):
        self.log('edit channel button pressed')
        try:
            flag = True
            # if rooms are open for this guild
            self.log('this room\'s id: ' + str(interaction.guild.id) + '\nopen guilds ids: ' + str(self.active_channels.keys())
            + '\nis inside? ' + str(interaction.guild.id in self.active_channels.keys()))
            if interaction.guild.id in self.active_channels.keys():
                self.log('guild is open, checking if user has active channel')
                # check if user has active channel
                if interaction.user.id in self.active_channels[interaction.guild.id].keys():
                    self.log('presenting vc editing modal')
                    # edit channel
                    channel = self.bot_client.get_channel(self.active_channels[interaction.guild.id][interaction.user.id])
                    thisModal = modals.InstantModal(title="Edit channel")
                    thisModal.set_callback_func(self.change_channel_details)
                    thisModal.set_fields(channel.name, channel.user_limit, channel.bitrate)
                    # thisModal.set_pre_fileds(channel.name, channel.user_limit, channel.bitrate)
                    flag = False
                    await interaction.response.send_modal(thisModal)
            if flag:
                self.log('user doesn\'t have an active channel, sending error message')
                await interaction.response.send_message('you don\'t have an active channel, please open one first', ephemeral = True)
        except Exception as e:
            self.log('Error editing channel due to error: ' + str(e))
            self.load_active_channels()
        

    async def change_channel_details(self, interaction):

        # get chosen values from modal
        # get name
        name = self.get_modal_value(interaction, 0)
        if name == '':
            name = f'{interaction.user.name}\'s office'

        # get users limit
        users_amount = self.get_modal_value(interaction, 1)
        if users_amount == '':
            users_amount = None
        else:
            try:
                users_amount = int(users_amount)
            except:
                await interaction.response.send_message('please only use numbers in the user limit textbox', ephemeral = True)
                return

        channel = self.bot_client.get_channel(self.active_channels[interaction.guild.id][interaction.user.id])
        
        url = "https://discord.com/api/v10/channels/" + str(channel.id)
        
        headers = {
            "Authorization": "Bot " + self.bot_client.get_secret(),
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": name,
            "user_limit": users_amount
        }
        
        response = requests.patch(url, headers=headers, json=payload)
        if response.status_code == 429:
            time = int(response.headers["Retry-After"])
            minutes = time // 60
            seconds = time % 60
            await interaction.response.send_message(f'please wait {minutes} minutes and {seconds} seconds before changing the channel again', ephemeral = True)
        else:
            await interaction.response.send_message(f'\"{name}\" was edited', ephemeral = True)
        return 

    async def create_new_channel(self, interaction):
        
        # get chosen values from modal
        # get name
        name = self.get_modal_value(interaction, 0)
        if name == '':
            name = f'{interaction.user.name}\'s office'

        # get users limit
        users_amount = self.get_modal_value(interaction, 1)
        if users_amount == '':
            users_amount = None
        else:
            try:
                users_amount = int(users_amount)
            except:
                await interaction.response.send_message('please only use numbers in the user limit textbox', ephemeral = True)
                return


        


        # get vc creation channel
        this_server_config = server_config(interaction.guild.id)
        creation_channel = self.bot_client.get_channel(int(this_server_config.get_creation_vc_channel()))

        # get category
        category = creation_channel.category

        # create vc in category
        new_channel = await category.create_voice_channel(name = name, user_limit = users_amount)
        await channel_modifier.give_management(new_channel, interaction.user)
        #new_channel.permissions_synced = True

        # add vc to active channels list
        if not interaction.guild.id in self.active_channels.keys(): 
            self.active_channels[interaction.guild.id] = {}
        self.active_channels[interaction.guild.id][interaction.user.id] = new_channel.id
        self.save_active_channels()
        # create embed with vc info
        if users_amount is None:
            users_amount = 'unlimited'
        else:
            users_amount = str(users_amount)

        
        embed = discord.Embed(title = f'\"{new_channel.name}\" was created',
        description = f'\n\t users limit: {users_amount}',
        color = 0x00ff00)
        await interaction.response.send_message(embed = embed, ephemeral = True)


        
        # start timer
        await asyncio.sleep(this_server_config.get_vc_closing_timer())
        if new_channel.id in self.active_channels[new_channel.guild.id].values():
            if len(new_channel.members) == 0:
                # delete channel
                self.active_channels[new_channel.guild.id].pop(interaction.user.id)
                self.save_active_channels()
                self.log_guild(f'deleted {new_channel.name} channel after {this_server_config.get_vc_closing_timer()} seconds due to inactivity', new_channel.guild)
                try:

                    await new_channel.delete()
                except Exception as e:
                    self.log('could not delete channel due to error: \n' + str(e))
                    pass

    def get_modal_value(self, interaction, index): #
        return interaction.data['components'][index]['components'][0]['value']

    async def initialize_active_channels(self):
        '''
        loads active channels from file,
        and deletes channels that are not active
        '''
        self.load_active_channels()
        # delete channels that are not active
        for guild_id in self.active_channels.keys():
            to_pop = []
            for user_id in self.active_channels[guild_id].keys():

                channel = self.bot_client.get_channel(self.active_channels[guild_id][user_id])
                # delete if channel is empty
                if channel is None:
                    to_pop.append(user_id)
                    self.log('a channel was deleted due to it not existing')
                elif len(channel.members) == 0:
                    to_pop.append(user_id)
                    self.log_guild(f'deleted {channel.name} channel due to inactivity', channel.guild)
                    try:
                        await channel.delete()
                    except Exception as e:
                        self.log('could not delete channel due to error: \n' + str(e))
                        pass
                else:
                    await channel_modifier.give_management(channel, self.bot_client.get_user(user_id))
            for user_id in to_pop:
                self.active_channels[guild_id].pop(user_id)
        self.save_active_channels()

    def save_active_channels(self):
        with open('data_base/active_channels.json', 'w') as file:
            json.dump(self.active_channels, file, indent=4)

    def load_active_channels(self):
        with open('data_base/active_channels.json', 'r') as file:
            temp_dic = json.load(file)
        temp2_dic = {}
        for guild_id in temp_dic.keys():
            temp2_dic[int(guild_id)] = {}
            for user_id in temp_dic[guild_id].keys():
                temp2_dic[int(guild_id)][int(user_id)] = int(temp_dic[guild_id][user_id])
        self.active_channels = temp2_dic
    
    def log(self, message):
        print(message)
        if self.logger is not None :
            self.logger.log_instance(message, self)

    def log_guild(self, message, guild):
        print(message)
        if self.logger is not None:
            self.logger.log_guild_instance(message, guild.id, self)


    async def clean_previous_channel(self, this_server_config):
        previous_channel = self.bot_client.get_channel(int(this_server_config.get_creation_vc_channel()))
        if previous_channel is not None:
            await channel_modifier.remove_readonly(previous_channel)
            await self.clean_previous_static_message(this_server_config)
    
    async def clean_previous_static_message(self, this_server_config):
        previous_channel = self.bot_client.get_channel(int(this_server_config.get_creation_vc_channel()))
        if previous_channel is not None:
            if this_server_config.get_static_message_id() != ' ':
                previous_message = await self.bot_client.get_message(this_server_config.get_static_message_id(), previous_channel, 50)
                if previous_message is not None:
                    await previous_message.delete()
                    this_server_config.set_static_message_id(' ')


    async def initialize_creation_channel(self, channel, this_server_config):
        this_server_config.set_creation_vc_channel(channel.id)
        await channel_modifier.set_readonly(channel)
        await self.initialize_static_message(this_server_config)

    async def initialize_static_message(self, this_server_config): # creates a static message in the channel
        if this_server_config.get_static_message() == ' ':
            return
        creation_channel = self.bot_client.get_channel(int(this_server_config.get_creation_vc_channel()))

        embed = discord.Embed(title = 'Edit voice channel', description = this_server_config.get_static_message())
        
        message = await creation_channel.send(embed = embed, view = views.get_InstantButtonView(self))
        this_server_config.set_static_message_id(message.id)