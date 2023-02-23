import discord
from discord.ext import commands
import ui_components_extension.room_opening_ui as room_opening_ui
import ui_components_extension.ui_tools as ui_tools
from DB_instances.generic_config_interface import server_config
import discord_modification_tools.channel_modifier as channel_modifier
from ui_components_extension.generic_ui_comps import Generic_View, Generic_Modal
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
VC_INVITE_DM = 'vc_invite_dm'
SPECIAL_ROLES = 'special_roles'
RATE_LIMIT_ERROR_TITLE = 'rate_limit_error_title'
RATE_LIMIT_ERROR_DESCRIPTION = 'rate_limit_error_description'
DEFAULT_USER_LIMIT = 'default_user_limit'


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
        @client.tree.command(name = 'edit_channel', description='choose a channel for editing new voice channels')
        async def choose_editing_channel(interaction: discord.Interaction):

            try:
                # get server config
                this_server_config = server_config(interaction.guild.id)

                embed_title = this_server_config.get_param(EMBED_MESSAGE_TITLE)
                embed_description = this_server_config.get_param(EMBED_MESSAGE_DESCRIPTION)
                embed = discord.Embed(title = embed_title, description = embed_description)
                message = await interaction.response.send_message(embed = embed, view = self.get_menu_view(this_server_config), ephemeral=True)

            except Exception as e:
                self.log(str(e))
                await interaction.response.send_message('Ops.. Something went wrong', ephemeral = True)

        #@client.tree.command(name = 'create_static_message', description='create a static message for vc creation channel')
        #@commands.has_permissions(administrator=True)
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
        
        #@client.tree.command(name = 'choose_vc_for_vc', description='set a channel for vc creation')
        #@commands.has_permissions(administrator=True)
        async def choose_vc_for_vc(interaction: discord.Interaction, channel : discord.VoiceChannel):

            try:
                # get server config
                this_server_config = server_config(interaction.guild.id)

                # set channel
                this_server_config.set_params(vc_for_vc = channel.id)
                await channel_modifier.set_readonly(channel)
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

        @client.tree.command(name = 'set_dynamics_name', description='set what name will be given to new vcs, for example: {name}\'s vc')
        @commands.has_permissions(administrator=True)
        async def set_vc_names(interaction: discord.Interaction, name : str):
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

        #@client.tree.command(name = 'set_user_limit', description='set what user limit will be given to new vcs. unlimited: 0')
        #@commands.has_permissions(administrator=True)
        async def set_vc_names(interaction: discord.Interaction, amount : int):
            if amount >= 100 or amount < 0:
                await interaction.response.send_message('invalid amount, choose either unlimited (0) or 1-100', ephemeral = True)
                return
            try:
                # get server config
                this_server_config = server_config(interaction.guild.id)

                # set channel
                this_server_config.set_params(default_user_limit = amount)

                await interaction.response.send_message(f'\"{amount}\" was set as new user limit', ephemeral = True)

            except Exception as e:
                self.log(str(e))
                await interaction.response.send_message('error', ephemeral = True)

        #@client.tree.command(name = 'add_special_role', description='add role to special roles list')
        #@commands.has_permissions(administrator=True)
        async def add_special_role(interaction : discord.Interaction, role : discord.Role, emoji : str = ''):
            try:
                this_server_config = server_config(interaction.guild.id)
                special_roles = this_server_config.get_param(SPECIAL_ROLES)
                if special_roles is None:
                    special_roles = []
                exists_flag = False
                for x in special_roles:
                    if x[0] == role.id:
                        await interaction.response.send_message(f'role \"{role.name}\" is already in the list, updating emoji', ephemeral = True)
                        special_roles.remove(x)
                        special_roles.append((role.id, emoji))
                        exists_flag = True
                if not exists_flag:
                    special_roles.append((role.id, emoji))
                    await interaction.response.send_message(f'role \"{role.name}\" was added to the list', ephemeral = True)
                this_server_config.set_params(special_roles=special_roles)
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
            if not self.confirm_is_owner(interaction, this_server_config):
                return
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
        await self.clean_special_roles(interaction.user.voice.channel, interaction.guild, this_server_config)
        embed = discord.Embed(title='Your channel is now public !')
        await interaction.response.send_message(embed=embed, ephemeral = True)
        await channel_modifier.publish_vc(interaction.user.voice.channel)
    
    async def private_channel(self, interaction, button, view):
        this_server_config = server_config(interaction.guild.id)
        if not await self.confirm_is_owner(interaction, this_server_config):
            return
        await self.clean_special_roles(interaction.user.voice.channel, interaction.guild, this_server_config)
        embed = discord.Embed(title='Your channel is now private !')
        await interaction.response.send_message(embed=embed, ephemeral = True)
        await channel_modifier.private_vc(interaction.user.voice.channel)

    async def special_channel(self, interaction, button, view):
        embed = discord.Embed(title='Coming soon!')
        await interaction.response.send_message(embed=embed, ephemeral = True)
        return
        this_server_config = server_config(interaction.guild.id)
        if not await self.confirm_is_owner(interaction, this_server_config):
            return
        special_roles = this_server_config.get_param(SPECIAL_ROLES)
        if special_roles is None:
            special_roles = []
        roles_list = []
        for x in special_roles:
            role_id = x[0]
            role = interaction.guild.get_role(role_id)
            # role = [y for y in interaction.guild.roles if y.id == x[0]][0]
            roles_list.append({'label' : x[1] + role.name, 'value' : x[0], 'description' : None})

        my_view = Generic_View()
        if len(special_roles) == 0:
            await interaction.response.send_message('no special roles were found', ephemeral = True)
            return
        my_view.add_generic_select(placeholder = 'choose role', options=roles_list, callback=self.make_room_special, max_values=1)
        await interaction.response.send_message('choose role', view=my_view, ephemeral = True)

    async def rename_channel(self, interaction, button, view):
        this_server_config = server_config(interaction.guild.id)
        if not await self.confirm_is_owner(interaction, this_server_config):
            return

        this_modal = Generic_Modal(title='Rename channel')
        this_modal.add_input(label = 'Enter new name:', placeholder='new name',
                              default=interaction.user.voice.channel.name)
        this_modal.set_callback(self.rename_channel_callback)
        await interaction.response.send_modal(this_modal)

    async def show_user_limit(self, interaction, button, view):
        this_server_config = server_config(interaction.guild.id)
        if not await self.confirm_is_owner(interaction, this_server_config):
            return
        limit_options = [{'label' : 'Unlimited',
                    'description' : '',
                    'value' : 0}] + [
                        {'label' : x,
                        'description' : '',
                        'value' : x}
                         for x in range(1, 25)
                    ]
        gen_view = Generic_View()
        gen_view.add_generic_select(placeholder='✋ User Limit', options=limit_options,
                                     min_values=0, max_values=1, callback=self.set_vc_limit)
        embed = discord.Embed(title='Choose user limit:')
        await interaction.response.send_message(embed=embed, view = gen_view, ephemeral = True)
        
    #################
    # select events #
    #################

    async def add_users_to_vc(self, interaction):
        if len(interaction.data['values']) == 0: 
            await interaction.response.defer(ephemeral = True)
            return
        
        this_server_config = server_config(interaction.guild.id)
        if not await self.confirm_is_owner(interaction, this_server_config):
            return
        
        
        user_id = interaction.data['values'][0]
        
        
        if int(interaction.user.id) != int(user_id):
            user = interaction.guild.get_member(int(user_id))
            await channel_modifier.allow_vc(interaction.user.voice.channel, user)
            embed = discord.Embed(title=user.display_name + ' can now connect to your channel')
            await interaction.response.send_message(embed=embed, ephemeral = True)
        else:
            embed = discord.Embed(title='you can\'t add yourself')
            await interaction.response.send_message(embed=embed, ephemeral = True)

    async def ban_users_from_vc(self, interaction):
        if len(interaction.data['values']) == 0: 
            await interaction.response.defer(ephemeral = True)
            return
        
        this_server_config = server_config(interaction.guild.id)
        if not await self.confirm_is_owner(interaction, this_server_config):
            return
        
        user_id = interaction.data['values'][0]
        
        
        if int(interaction.user.id) != int(user_id):
            user = interaction.guild.get_member(int(user_id))
            await channel_modifier.private_vc(interaction.user.voice.channel, user)
            embed = discord.Embed(title='<@'+user_id+'> can not connect to your channel anymore')
            await interaction.response.send_message(embed=embed, ephemeral = True)
        else:
            await interaction.response.send_message('you can\'t ban yourself', ephemeral = True) 
    
    async def make_room_special(self, interaction, select, view):
        this_server_config = server_config(interaction.guild.id)
        if not await self.confirm_is_owner(interaction, this_server_config):
            return
        
        if len(interaction.data['values']) == 0:
            embed= discord.Embed(title='no roles selected')
            await interaction.response.send_message(embed=embed)
            return
        await channel_modifier.private_vc(interaction.user.voice.channel)
        await self.clean_special_roles(interaction.user.voice.channel, interaction.guild, this_server_config)
        role = interaction.guild.get_role(int(interaction.data['values'][0]))
        await channel_modifier.allow_vc(interaction.user.voice.channel, role)
        embed= discord.Embed(title='room is now special for ' + role.name)
        await interaction.response.send_message(embed=embed, ephemeral = True)

    async def set_vc_limit(self, interaction, select, view):
        if len(interaction.data['values']) == 0:
            interaction.response.defer(ephemeral = True)
            return
        this_server_config = server_config(interaction.guild.id)
        if not await self.confirm_is_owner(interaction, this_server_config):
            return
        selected_value = int(interaction.data['values'][0])
        await interaction.user.voice.channel.edit(user_limit = selected_value)
        if selected_value == 0:
            embed= discord.Embed(title='Your channel\'s user limit has changed to unlimited')
            await interaction.response.send_message(embed=embed, ephemeral = True)
        else:
            embed= discord.Embed(title='Your channel\'s user limit has changed to ' + str(selected_value))
            await interaction.response.send_message(embed=embed, ephemeral = True)

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

    async def rename_channel_callback(self, interaction):
        this_server_config = server_config(interaction.guild.id)
        if not await self.confirm_is_owner(interaction, this_server_config):
            return
        new_name = ui_tools.get_modal_value(interaction, 0)
        if interaction.user.voice.channel.name == new_name or new_name == '':
            await interaction.response.send_message('no changes have been made', ephemeral = True)
            return
        result, time = await self.rename_channel_request(interaction.user.voice.channel, new_name)
        if not result:
            minutes = time // 60
            seconds = time % 60
            this_server_config = server_config(interaction.guild.id)
            embed_response = discord.Embed(title = "You renamed your channel too fast !",
                                            description = "Please wait" + str(time) \
                                             + " seconds until next rename, \nor just open a new dynamic channel - \n<#" + str(this_server_config.get_param(VC_FOR_VC)) + ">")
            await interaction.response.send_message(embed = embed_response, ephemeral = True)
            #await interaction.response.send_message(f'please wait {minutes} minutes and {seconds} seconds before changing the channel again', ephemeral = True)
        else:
            embed = discord.Embed(title = "Your channel\'s name has changed to " + new_name)
            await interaction.response.send_message(embed=embed, ephemeral = True)
    

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
            overwrites=master_channel.overwrites, user_limit=master_channel.user_limit, reason='opening channel for ' + member.name,
            rtc_region=master_channel.rtc_region, video_quality_mode=master_channel.video_quality_mode)
        await channel_modifier.remove_readonly(new_channel)
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
        
    async def rename_channel_request(self, channel, new_name):
        url = "https://discord.com/api/v10/channels/" + str(channel.id)
        
        headers = {
            "Authorization": "Bot " + self.bot_client.get_secret(),
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": new_name
        }
        # get reply from discord
        response = requests.patch(url, headers=headers, json=payload)

        # if channel is rate limited
        if response.status_code == 429:
            
            time = int(response.headers["Retry-After"])
            return False, time
        else:
            return True, 0

    async def clean_special_roles(self, channel, guild, this_server_config): #
        special_roles = this_server_config.get_param(SPECIAL_ROLES)
        for x in special_roles:
            a_role = guild.get_role(int(x[0]))
            await channel_modifier.delete_role_permissions(channel, a_role)

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

        
        # add category with vc_for_vc channel and edit channel
        await self.setup_guild(guild, this_server_config)

        if guild.id not in self.active_channels.keys():
            self.active_channels[guild.id] = {}

    async def setup_guild(self, guild, this_server_config):
        # set default params
        if this_server_config.get_param(EMBED_MESSAGE_TITLE) is None:
            self.log('setting default params for ' + guild.name)
            this_server_config.set_params(is_message_embed=True, 
                                        embed_message_title='Manage your dynamic voice channel',
                                        embed_message_description='Here you can manage your voice \
                                            channel and edit it as you see fit. \
                                        \nYou must be connected to the voice channel in order to edit it.',
                                        vc_invite_dm = False,
                                        rate_limit_error_title='Easy does it...',
                                        rate_limit_error_description='youv\'e renamed the channel too many times \
                                        \nplease wait {time} seconds or open a new channel - <#{channel}>',
                                        default_user_limit = 0,
                                        vc_name='{name}\'s Channel'
                                        )



        category = await guild.create_category('⚡ Dynamic Channels')
        edit_channel = await category.create_text_channel('✍edit-channel')
        this_server_config.set_params(initial_category_id=category.id)
        this_server_config.set_params(editing_vc_channel=edit_channel.id)

        Master_Channel = await category.create_voice_channel('➕ New Channel')
        this_server_config.set_params(vc_for_vc=Master_Channel.id)
        await channel_modifier.set_readonly(Master_Channel)
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
            if this_server_config.get_param(IS_MESSAGE_EMBED):
                static_message = this_server_config.get_param(EMBED_MESSAGE_TITLE)
            else:
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
        embed = discord.Embed(title = "you are not connected to any channel", description = "You should open your own channel and try again - \
                              \n<#" + str(this_server_config.get_param(VC_FOR_VC)) + ">", color = 0xe74c3c)
        embed.set_thumbnail(url = "https://i.imgur.com/epJbz6n.gif")
        return embed
    
    def get_not_owned_channel(self, user, guild_id, this_server_config):
        embed = discord.Embed(title = "Oops, this is not your channel !", description = "It will not happen in your channel - \
                            \n<#" + str(this_server_config.get_param(VC_FOR_VC)) + ">", color = 0xe74c3c)
        embed.set_thumbnail(url = "https://i.imgur.com/epJbz6n.gif")
        return embed
    
    #############
    # get views #
    #############

    def get_menu_view(self, this_server_config):
        button_color = ui_tools.string_to_color(this_server_config.get_param(BUTTON_STYLE))
        gen_view = Generic_View()
        gen_view.add_generic_button(label = ' Public',
                                    style = ui_tools.string_to_color('white'),
                                    callback = self.publish_channel,
                                    emoji='🌐'
                                    )
        gen_view.add_generic_button(label = ' Private',
                                    style = ui_tools.string_to_color('white'),
                                    callback = self.private_channel,
                                    emoji= '🚫'
                                    )
        
        gen_view.add_generic_button(label = ' Rename', 
                                    style= ui_tools.string_to_color('white'),
                                    callback = self.rename_channel,
                                    emoji= '✏️'
                                    )
        
        gen_view.add_generic_button(label=' User Limit',
                                    style= ui_tools.string_to_color('white'),
                                    callback = self.show_user_limit,
                                    emoji='✋'
                                    )
        
        gen_view.add_generic_button(label=' Special Channel',
                                    style= ui_tools.string_to_color('blue'),
                                    callback = self.special_channel,
                                    emoji='🌟'
                                    )
        
        gen_view.add_user_selector(placeholder='👋 Add Users', callback=self.add_users_to_vc)
        gen_view.add_user_selector(placeholder='👊 Ban Users', callback=self.ban_users_from_vc)


        
        return gen_view
