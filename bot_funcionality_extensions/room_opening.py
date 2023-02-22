import discord
from discord.ext import commands
import ui_components_extension.room_opening_ui as room_opening_ui
import ui_components_extension.ui_tools as ui_tools
from DB_instances.generic_config_interface import server_config
import discord_modification_tools.channel_modifier as channel_modifier
from ui_components_extension.generic_ui_comps import Generic_Button, Generic_View
from Interfaces.IGenericBot import IGenericBot
import json
import os
import requests

EDITING_VC_CHANNEL = 'editing_vc_channel'
STATIC_MESSAGE_ID = 'static_message_id'
STATIC_MESSAGE = 'static_message'
BUTTON_STYLE = 'button_style'
VC_FOR_VC = 'vc_for_vc'
VC_NAME = 'vc_name'
IS_MESSAGE_EMBED = 'is_message_embed'
EMBED_MESSAGE_TITLE = 'embed_message_title'
EMBED_MESSAGE_DESCRIPTION = 'embed_message_description'
INITIAL_CATEGORY_ID = 'initial_category_id'
class room_opening:
    clean_dead_every = 60
    db_dir_path = 'data_base/room_opening'
    db_file_name = 'active_channels.json'
    def __init__(self, client : IGenericBot):
        self.dead_channels_counter = 0
        self.bot_client = client
        self.logger = client.get_logger()
        self.active_channels = {}
        self.logger.log('room_opening extension loading...')
        self.bot_client.add_on_ready_callback(self.resume_buttons)
        self.bot_client.add_on_ready_callback(self.clean_dead_active_channels)
        self.bot_client.add_on_session_resumed_callback(self.resume_buttons)
        self.bot_client.add_on_session_resumed_callback(self.clean_dead_active_channels)
        self.bot_client.add_on_voice_state_update_callback(self.vc_state_update)
        self.bot_client.add_on_guild_channel_delete_callback(self.on_guild_channel_delete_callback)
        self.bot_client.add_on_guild_join_callback(self.on_guild_join_callback)
        self.bot_client.add_on_guild_remove_callback(self.on_guild_remove_callback)
        @client.tree.command(name = 'choose_editing_channel', description='choose a channel for editing new voice channels')
        @commands.has_permissions(administrator=True)
        async def choose_editing_channel(interaction: discord.Interaction, channel : discord.TextChannel):

            try:
                # get server config
                this_server_config = server_config(interaction.guild.id)

                if channel.id == this_server_config.get_param(EDITING_VC_CHANNEL):
                    await interaction.response.send_message('this channel is already set as editing channel', ephemeral = True)
                    return

                # check if channel is set, and if so, remove readonly and delete static message
                if this_server_config.get_param(EDITING_VC_CHANNEL) is not None:
                    await self.clean_previous_channel(this_server_config)

                # set announcement channel
                await self.initialize_creation_channel(channel, this_server_config)
                await interaction.response.send_message(f'\"{channel.name}\" was set as vc editing channel', ephemeral = True)

            except Exception as e:
                self.log(str(e))
                await interaction.response.send_message('Ops.. Something went wrong', ephemeral = True)

        @client.tree.command(name = 'create_static_message', description='create a static message for vc creation channel')
        @commands.has_permissions(administrator=True)
        async def create_static_message(interaction: discord.Interaction, message : str, button_color : str):

            try:
                # get server config
                this_server_config = server_config(interaction.guild.id)
                
                #check if channel exists
                try:
                    channnel = interaction.guild.fetch_channel(this_server_config.get_param(EDITING_VC_CHANNEL))
                except:
                    this_server_config.set_params(editing_vc_channel=None)
                    await interaction.response.send_message('please set a creation channel first', ephemeral = True)
                    return

                # check if channel is set, and if not, exits
                if this_server_config.get_param(EDITING_VC_CHANNEL) is None:
                    await interaction.response.send_message('please set a creation channel first', ephemeral = True)
                    return

                discord_color = ui_tools.string_to_color(button_color)
                # set button style
                if discord_color is None:
                    await interaction.response.send_message('please choose a valid color', ephemeral = True)
                    return
                else:
                    this_server_config.set_params(static_message=message, button_style=button_color)
                    response = f'\"{message}\" was set as static message' 
                    await interaction.response.send_message(response, ephemeral = True)
                await self.clean_previous_static_message(this_server_config)
                
                
                # respond to user
                

                # set message
                await self.initialize_static_message_with_config(this_server_config)



            except Exception as e:
                self.log(str(e))
                await interaction.response.send_message('error', ephemeral = True)
        
        @client.tree.command(name = 'choose_vc_for_vc', description='set a channel for vc creation')
        @commands.has_permissions(administrator=True)
        async def choose_vc_for_vc(interaction: discord.Interaction, channel : discord.VoiceChannel):

            try:
                # get server config
                this_server_config = server_config(interaction.guild.id)

                # set channel
                this_server_config.set_params(vc_for_vc = channel.id)
                await interaction.response.send_message(f'\"{channel.name}\" was set as vc for vc', ephemeral = True)

            except Exception as e:
                self.log(str(e))
                await interaction.response.send_message('error', ephemeral = True)
            
        @client.tree.command(name = 'setup', description='create default category with master and edit channels')
        async def setup_command(interaction):
            await interaction.response.send_message('setting up...', ephemeral = True)
            this_server_config = server_config(interaction.guild.id)
            await self.setup_guild(interaction.guild, this_server_config)

        @client.tree.command(name = 'clear', description='clears master and edit channels, with the default category')
        async def clear_command(interaction):
            await interaction.response.send_message('clearing...', ephemeral = True)
            this_server_config = server_config(interaction.guild.id)
            await self.clear_guild(interaction.guild, this_server_config)

        @client.tree.command(name = 'set_vc_names', description='set what name will be given to new vcs, for example: {name}\'s vc')
        @commands.has_permissions(administrator=True)
        async def s4et_vc_names(interaction: discord.Interaction, name : str):
            if len(name) >= 100:
                await interaction.response.send_message('name is too long, must be under 100 characters', ephemeral = True)
                return
            try:
                # get server config
                this_server_config = server_config(interaction.guild.id)

                # set channel
                this_server_config.set_params(vc_name = name)

                await interaction.response.send_message(f'\"{name}\" was set as new vc names', ephemeral = True)

            except Exception as e:
                self.log(str(e))
                await interaction.response.send_message('error', ephemeral = True)




    ################
    # guild events #
    ################

    async def vc_state_update(self, member, before, after):
        # check if before channel is empty
        # print(f'{member} moved from {before.channel} to {after.channel}')
        self.dead_channels_counter += 1
        if self.dead_channels_counter >= room_opening.clean_dead_every:
            self.clean_dead_active_channels()
            self.dead_channels_counter = 0
        if before.channel is not None and len(before.channel.members) == 0:
            # check if channel is active
            if before.channel.guild.id in self.active_channels.keys() and before.channel.id in self.active_channels[before.channel.guild.id].keys():
                # delete channel
                try:
                    self.active_channels[before.channel.guild.id].pop(before.channel.id)
                    await before.channel.delete()
                except discord.errors.NotFound as e:
                    pass
                except Exception as e:
                    self.log('Error deleting channel due to error: ' + str(e))
                    self.load_active_channels()
                    return
                self.save_active_channels()
                await self.log_guild(f'deleted {before.channel.name} channel because it was empty', before.channel.guild)

        try:
        # check if after channel is vc for vc
            if after.channel is None:
                return
            this_server_config = server_config(after.channel.guild.id)
            if this_server_config.get_param(VC_FOR_VC) is not None and after.channel.id == this_server_config.get_param(VC_FOR_VC):
                await self.create_dynamic_channel(member, after.channel, this_server_config)

            # self.log(self.active_channels)
        except discord.errors.HTTPException as e:
            await self.log_guild('Error creating channel due to error: ' + str(e), after.channel.guild)
            self.load_active_channels()
            return

    async def on_guild_channel_delete_callback(self, channel):
        if channel.guild.id in self.active_channels.keys() and channel.id in self.active_channels[channel.guild.id].keys():
            self.active_channels[channel.guild.id].pop(channel.id)
            await self.log_guild(f'deleted {channel.name} channel from active channels because it was deleted', channel.guild)
            self.save_active_channels()

    async def on_guild_join_callback(self, guild):
        await self.initialize_guild(guild)

    async def on_guild_remove_callback(self, guild):
        this_server_config = server_config(guild.id)
        try:
            await self.clear_guild(guild, this_server_config)
        except:
            print('couldnt clear guild')

    #################
    # button events #
    #################

    async def edit_channel_button(self, interaction, button, view):
        self.log('edit channel button pressed')
        this_server_config = server_config(interaction.guild.id)
        try:
            # if rooms are open for this guild
            self.log('this room\'s id: ' + str(interaction.guild.id) + '\nopen guilds ids: ' + str(self.active_channels.keys())
            + '\nis inside? ' + str(interaction.guild.id in self.active_channels.keys()))
            if interaction.user.voice is None or interaction.guild.id not in self.active_channels.keys():
                embed = discord.Embed(title = "צריך לפתוח משרד קודם..", description = "פשוט נכנסים למשרד ואז מנסים שוב - <#" + \
                                       str(this_server_config.get_param(VC_FOR_VC)) + ">", color = 0xe74c3c)
                embed.set_thumbnail(url = "https://i.imgur.com/epJbz6n.gif")
                await interaction.response.send_message(embed = embed, ephemeral = True)
                return
            # if user is in an active channel 
            if interaction.user.voice.channel.id in self.active_channels[interaction.guild.id].keys():
                # check if user has an active channel
                if interaction.user.id in self.active_channels[interaction.guild.id].values():
                    # check if user is in his active channel
                    if interaction.user.id != self.active_channels[interaction.guild.id][interaction.user.voice.channel.id]:
                        self.log('user doesn\'t have an active channel, sending error message')
                        embed = discord.Embed(title = "אופס.. זה לא המשרד שלך", description = "במשרד שלך זה יעבוד - <#" +
                                               str(this_server_config.get_param(VC_FOR_VC)) + ">", color = 0xe74c3c)
                        embed.set_thumbnail(url = "https://i.imgur.com/epJbz6n.gif")
                        await interaction.response.send_message(embed = embed, ephemeral = True)
                        return
                else:
                    self.log('user doesn\'t have an active channel, sending error message')
                    embed = discord.Embed(title = "אופס.. זה לא המשרד שלך", description = "במשרד שלך זה יעבוד - <#" +
                                           str(this_server_config.get_param(VC_FOR_VC)) + ">", color = 0xe74c3c)
                    embed.set_thumbnail(url = "https://i.imgur.com/epJbz6n.gif")
                    await interaction.response.send_message(embed = embed, ephemeral = True)
                    return
            # if user doesnt have a channel
            if interaction.user.id not in self.active_channels[interaction.guild.id].values():
                # if user is in a channel which is not hes own
                    embed = discord.Embed(title = "צריך לפתוח משרד קודם..", description = "פשוט פותחים משרד ואז מנסים שוב - <#" +
                                           str(this_server_config.get_param(VC_FOR_VC)) + ">", color = 0xe74c3c)
                    embed.set_thumbnail(url = "https://i.imgur.com/epJbz6n.gif")
                    await interaction.response.send_message(embed = embed, ephemeral = True)
                    return
            self.log('guild is open, user has active channel')
            
                # check if user has active channel
            
                
            #check user is inside his channel
            self.log('presenting vc editing modal')
            # edit channel
            channel = interaction.user.voice.channel
            thisModal = room_opening_ui.InstantModal(title="Edit channel")
            thisModal.set_callback_func(self.change_channel_details)
            thisModal.set_fields(channel.name, channel.user_limit, channel.bitrate)
            # thisModal.set_pre_fileds(channel.name, channel.user_limit, channel.bitrate)
            await interaction.response.send_modal(thisModal)
                    
                    # await interaction.response.send_message('you don\'t have an active channel, please open one first', ephemeral = True)
        except Exception as e:
            self.log('Error editing channel due to error: ' + str(e))
            self.load_active_channels()

    async def publish_channel(self, interaction, button, view):
        this_server_config = server_config(interaction.guild.id)
        if not await self.confirm_is_owner(interaction, this_server_config):
            return
        await interaction.response.send_message('publishing channel', ephemeral = True)
        await channel_modifier.publish_vc(interaction.user.voice.channel)
    
    async def private_channel(self, interaction, button, view):
        this_server_config = server_config(interaction.guild.id)
        if not await self.confirm_is_owner(interaction, this_server_config):
            return
        await interaction.response.send_message('making channel private', ephemeral = True)
        await channel_modifier.private_vc(interaction.user.voice.channel)

    #################
    # modal events  #
    #################
    
    async def change_channel_details(self, interaction):

        # get chosen values from modal
        # get name
        name = ui_tools.get_modal_value(interaction, 0)
        if name == '':
            name = f'{interaction.user.name}\'s office'

        # get users limit
        users_amount = ui_tools.get_modal_value(interaction, 1)
        if users_amount == '':
            users_amount = None
        else:
            try:
                users_amount = int(users_amount)
            except:
                await interaction.response.send_message('please only use numbers in the user limit textbox', ephemeral = True)
                return

        if interaction.user.voice is None:
            await interaction.response.send_message('you need to be in a voice channel to edit it', ephemeral = True)
            return
        channel = interaction.user.voice.channel
        
        url = "https://discord.com/api/v10/channels/" + str(channel.id)
        
        headers = {
            "Authorization": "Bot " + self.bot_client.get_secret(),
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": name,
            "user_limit": users_amount
        }
        # get reply from discord
        response = requests.patch(url, headers=headers, json=payload)

        # if channel is rate limited
        if response.status_code == 429:
            this_server_config = server_config(interaction.guild.id)
            time = int(response.headers["Retry-After"])
            minutes = time // 60
            seconds = time % 60
            embed_response = discord.Embed(title = "לאט לאט...", description = "שינית את שם החדר יותר מדיי פעמים \
            \nיש להמתין "+ str(time) +" שניות, \
            \nאו לפתוח משרד חדש - <#" + str(this_server_config.get_param(VC_FOR_VC)) + ">")
            await interaction.response.send_message(embed = embed_response, ephemeral = True)
            #await interaction.response.send_message(f'please wait {minutes} minutes and {seconds} seconds before changing the channel again', ephemeral = True)
        else:
            embed_response = discord.Embed(title = "השינויים בוצעו בהצלחה", description = "שם החדר: " + str(name) 
            + "\nהגבלת משתמשים: " + str(users_amount))
            await interaction.response.send_message(embed = embed_response, ephemeral = True)
        return 


    ######################
    # local db functions #
    ######################
    
    def save_active_channels(self):
        if not os.path.exists(room_opening.db_dir_path):
            os.makedirs(room_opening.db_dir_path)
        with open(room_opening.db_dir_path + '/' + room_opening.db_file_name, 'w+') as file:
            json.dump(self.active_channels, file, indent=4)

    def load_active_channels(self):
        try:
            with open(room_opening.db_dir_path + '/' + room_opening.db_file_name, 'r') as file:
                temp_dic = json.load(file)
        except:
            self.active_channels = {}
            return
        temp2_dic = {}
        for guild_id in temp_dic.keys():
            temp2_dic[int(guild_id)] = {}
            for channel_id in temp_dic[guild_id].keys():
                temp2_dic[int(guild_id)][int(channel_id)] = int(temp_dic[guild_id][channel_id])
        self.active_channels = temp2_dic
    
    #####################
    # logging functions #
    #####################

    def log(self, message):
        print(message)
        if self.logger is not None :
            self.logger.log_instance(message, self)

    async def log_guild(self, message, guild):
        print(message)
        if self.logger is not None:
            await self.logger.log_guild_instance(message, guild.id, self)

    ############################################
    # channel modification functions for guild #
    ############################################

    async def create_dynamic_channel(self, member : discord.Member, master_channel : discord.VoiceChannel, this_server_config : server_config):
        if master_channel.guild.id not in self.active_channels.keys():
            self.active_channels[int(master_channel.guild.id)] = {}

        # get vc name
        vc_name = this_server_config.get_param(VC_NAME)
        if vc_name is None:
            vc_name = f'{member.display_name}\'s Office'
        else:
            if vc_name.find('{name}') == -1:
                vc_name = member.display_name + ' ' + vc_name
            else:
                vc_name = vc_name.replace('{name}', member.display_name)
        #create channel
        new_channel = await master_channel.category.create_voice_channel(name = vc_name, bitrate = master_channel.bitrate, 
            overwrites=master_channel.overwrites, user_limit=master_channel.user_limit, reason='opening channel for ' + member.name)
        # print(after.channel.overwrites)
        # stop category sync
        await new_channel.edit(sync_permissions=False)
        # await after.channel.edit(sync_permissions=True)
        await channel_modifier.give_management(new_channel, member)
        #print(after.channel.overwrites)

        await member.move_to(new_channel)
        self.active_channels[master_channel.guild.id][new_channel.id] = member.id

        self.save_active_channels()

    async def clean_previous_channel(self, this_server_config):
        previous_channel = self.bot_client.get_channel(int(this_server_config.get_param(EDITING_VC_CHANNEL)))
        if previous_channel is not None:
            await channel_modifier.remove_readonly(previous_channel)
            await self.clean_previous_static_message(this_server_config)
    
    async def clean_previous_static_message(self, this_server_config):
        previous_channel = self.bot_client.get_channel(int(this_server_config.get_param(EDITING_VC_CHANNEL)))
        if previous_channel is not None:
            if this_server_config.get_param(STATIC_MESSAGE_ID) is not None:
                previous_message = await self.bot_client.get_message(this_server_config.get_param(STATIC_MESSAGE_ID), previous_channel, 50)
                if previous_message is not None:
                    await previous_message.delete()
                    this_server_config.set_params(static_message_id = None)

    async def clean_dead_active_channels(self):
        '''
        loads active channels from file,
        and deletes channels that are not active
        '''
        try:
            self.load_active_channels()
            # delete channels that are not active
            for guild_id in self.active_channels.keys():
                to_pop = []
                for channel_id in self.active_channels[guild_id].keys():

                    channel = self.bot_client.get_channel(channel_id)
                    # delete if channel is empty
                    if channel is None:
                        to_pop.append(channel_id)
                        self.log('a channel was deleted due to it not existing')
                    elif len(channel.members) == 0:
                        to_pop.append(channel_id)
                        await self.log_guild(f'deleted {channel.name} channel due to inactivity', channel.guild)
                        try:
                            await channel.delete()
                        except Exception as e:
                            self.log('could not delete channel due to error: \n' + str(e))
                            pass
                    else:
                        await channel_modifier.give_management(channel, self.bot_client.get_user(self.active_channels[guild_id][channel_id]))
                for channel_id in to_pop:
                    self.active_channels[guild_id].pop(channel_id)
        except Exception as e:
            self.log('could not load active channels due to fatal error: \n' + str(e))
        self.save_active_channels()
    
    async def initialize_creation_channel(self, channel, this_server_config):
        this_server_config.set_params(editing_vc_channel=channel.id)
        await channel_modifier.set_readonly(channel)
        await self.clean_previous_static_message(this_server_config)
        await self.initialize_static_message(this_server_config, channel)

    # if you dont have the channel object
    async def initialize_static_message_with_config(self, this_server_config): # creates a static message in the channel
        if this_server_config.get_param(STATIC_MESSAGE) is None:
            return
        creation_channel = self.bot_client.get_channel(int(this_server_config.get_param(EDITING_VC_CHANNEL)))
        
        await self.initialize_static_message(this_server_config, creation_channel)

    # if you have the channel object
    async def initialize_static_message(self, this_server_config, creation_channel):
        if creation_channel is None:
            return
        
        # prepare message and send
        if this_server_config.get_param(IS_MESSAGE_EMBED) is False:
            content = this_server_config.get_param(STATIC_MESSAGE)
            message = await creation_channel.send(content = content, view = self.get_menu_view(this_server_config))
        else:
            embed_title = this_server_config.get_param(EMBED_MESSAGE_TITLE)
            embed_description = this_server_config.get_param(EMBED_MESSAGE_DESCRIPTION)
            embed = discord.Embed(title = embed_title, description = embed_description)
            message = await creation_channel.send(embed = embed, view = self.get_menu_view(this_server_config))
        message_id = message.id
        this_server_config.set_params(static_message_id=message_id)
        
    #################
    # guild methods #
    #################

    async def initialize_guild(self, guild):
        self.log('initializing guild: ' + str(guild.name))
        await self.log_guild('initializing guild', guild)
        this_server_config = server_config(guild.id)

        # check if guild is already initialized
        if this_server_config.get_param(VC_FOR_VC) is not None:
            if guild.get_channel(int(this_server_config.get_param(VC_FOR_VC))) is not None:
                editing_channel_id = this_server_config.get_param(EDITING_VC_CHANNEL)
                if editing_channel_id is not None:
                    editing_channel = guild.get_channel(int(editing_channel_id))
                    if editing_channel is not None:
                        await self.initialize_creation_channel(editing_channel, this_server_config)
                return

        # set default params
        this_server_config.set_params(is_message_embed=True)
        this_server_config.set_params(embed_message_title='Manage your dynamic voice channel')
        this_server_config.set_params(embed_message_description='Here you can manage your voice channel and edit it as you see fit. \
                                      \nYou must be connected to the voice channel in order to edit it.')
        
        # add category with vc_for_vc channel and edit channel
        await self.setup_guild(guild, this_server_config)

        if guild.id not in self.active_channels.keys():
            self.active_channels[guild.id] = {}

    async def setup_guild(self, guild, this_server_config):
        category = await guild.create_category('⚡ Dynamic Channels')
        edit_channel = await category.create_text_channel('✍edit-channel')
        this_server_config.set_params(initial_category_id=category.id)
        this_server_config.set_params(editing_vc_channel=edit_channel.id)

        Master_Channel = await category.create_voice_channel('➕ New Channel')
        this_server_config.set_params(vc_for_vc=Master_Channel.id)

        await self.initialize_creation_channel(edit_channel, this_server_config)
    
    async def clear_guild(self, guild, this_server_config):
        master_channel = guild.get_channel(int(this_server_config.get_param(VC_FOR_VC)))
        initial_category_id = this_server_config.get_param(INITIAL_CATEGORY_ID)
        my_category = None
        if initial_category_id is not None:
            for category in guild.categories:
                if category.id == int(initial_category_id):
                    my_category = category
                    break
        if master_channel is not None:
            await master_channel.delete()
        edit_channel = guild.get_channel(int(this_server_config.get_param(EDITING_VC_CHANNEL)))
        if edit_channel is not None:
            await edit_channel.delete()
        if my_category is not None:
            await my_category.delete()

    #########################
    # maintanance functions #
    #########################

    async def resume_buttons(self):
        '''
        restarts all active buttons on all creatrion channels
        '''
        self.log('initializing buttons')

        # get all guilds
        for guild in self.bot_client.guilds:
            # get all channels
            this_server_config = server_config(guild.id)
            # print(str(this_server_config))
            creation_channel = this_server_config.get_param(EDITING_VC_CHANNEL)
            static_message = this_server_config.get_param(STATIC_MESSAGE)
            static_message_id = this_server_config.get_param(STATIC_MESSAGE_ID)
            # if all necessary params are set
            if creation_channel is not None and static_message is not None and static_message_id is not None:
                # get channel with saved id
                creation_channel = self.bot_client.get_channel(int(this_server_config.get_param(EDITING_VC_CHANNEL)))
                # if channel exists
                if creation_channel is not None:

                    # get message with saved id
                    msg = await self.bot_client.get_message(static_message_id, creation_channel, 20)

                    # if message doesnt exist
                    if msg is None:
                        self.log('could not find message, creating new one')
                        await self.initialize_creation_channel(creation_channel, this_server_config)
                    else:
                        # updating view
                        new_msg = await msg.edit(content = msg.content, view = self.get_menu_view(this_server_config))

                        # updating server config
                        this_server_config.set_params(static_message_id=new_msg.id)

                        self.log('button initialized for ' + guild.name)
    
    ##################
    # util functions #
    ##################

    def rooms_exist_in_guild(self, guild_id):
        return guild_id in self.active_channels.keys()

    def user_in_active_channel(self, user, guild_id):
        if user.voice is None:
            return False
        if self.rooms_exist_in_guild(guild_id):
            if user.voice.channel.id in self.active_channels[guild_id]:
                return True
        return False
    
    def user_has_active_channel(self, user, guild_id):
        return user.id in self.active_channels[guild_id].values()
    
    def user_inside_owned_active_channel(self, user, guild_id):
        if self.user_in_active_channel(user, guild_id):
            if self.active_channels[guild_id][user.voice.channel.id] == user.id:
                return True
        return False

    async def confirm_is_owner(self, interaction, this_server_config):
        self.load_active_channels()
        user = interaction.user
        guild_id = interaction.guild_id
        if not self.rooms_exist_in_guild(guild_id) or not self.user_in_active_channel(user, guild_id):
            await interaction.response.send_message(
                embed=self.get_need_to_open_channel(user, guild_id, this_server_config),
                ephemeral=True
            )
            return False
        elif not self.user_inside_owned_active_channel(user, guild_id):
            await interaction.response.send_message(
                embed=self.get_not_owned_channel(user, guild_id, this_server_config),
                ephemeral=True
            )
            return False
        
        return True

    ################
    # embed errors #
    ################

    def get_need_to_open_channel(self, user, guild_id, this_server_config):
        embed = discord.Embed(title = "צריך לפתוח משרד קודם..", description = "פשוט נכנסים למשרד ואז מנסים שוב - <#" + \
                                str(this_server_config.get_param(VC_FOR_VC)) + ">", color = 0xe74c3c)
        embed.set_thumbnail(url = "https://i.imgur.com/epJbz6n.gif")
        return embed
    
    def get_not_owned_channel(self, user, guild_id, this_server_config):
        embed = discord.Embed(title = "אופס.. זה לא המשרד שלך", description = "במשרד שלך זה יעבוד - <#" +
                                str(this_server_config.get_param(VC_FOR_VC)) + ">", color = 0xe74c3c)
        embed.set_thumbnail(url = "https://i.imgur.com/epJbz6n.gif")
        return embed
    
    #############
    # get views #
    #############

    def get_menu_view(self, this_server_config):
        button_color = ui_tools.string_to_color(this_server_config.get_param(BUTTON_STYLE))
        gen_view = Generic_View()
        gen_view.add_generic_button(label = 'Public',
                                    style = button_color,
                                    callback = self.publish_channel
                                    )
        gen_view.add_generic_button(label = 'Private',
                                    style = button_color,
                                    callback = self.private_channel
                                    )
        
        return gen_view
