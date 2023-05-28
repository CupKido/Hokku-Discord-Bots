import discord
from discord import app_commands
from Interfaces.IGenericBot import IGenericBot
from DB_instances.generic_config_interface import server_config
from DB_instances.per_id_db import per_id_db
from bot_funcionality_extensions.logger import logger
from discord.ext import commands, tasks
import io
import permission_checks
from DB_instances.DB_instance import *
############################################
# this is a generic bot that lets you sign #
# to events the bot receives from discord. #
# you may sign to events by using the      #
# add_<event name>_callback method.        #
############################################
# Type of events and their parameters:     #
#   general event ()                       #
#   changes event (before, after)          #
#       (for voice, (<member>, before,     #
#       after))                            #
#   one time event (<item>) (for messages, #
#       on_guild join...)                  #
############################################
# the idea is that you create a new        #
# features by creating a new class that    #
# recieves the bot as a parameter and      #
# then signs to the events it needs.       #
# that way you can create a new feature    #
# without changing the bot code.           #
# in order to add a feature to the bot,    #
# you need to use the add_feature method.  #
# if you want to add multiple features,    #
# you can use the add_features method.     #
############################################
# the bot comes with a pre-made logger,    #
# that lets you log either general logs or #
# guild specific logs.                     #
############################################

#TODO: add "initializer" function instead of __init__ to allow for easier feature adding, and changing parameters

class GenericBot_client(IGenericBot):
    developers_list = []

    def __init__(self, secret_key, db_name, db_method, alert_when_online : bool = False, command_prefix = '!', error_handler = None, debug=False, permissions_code : int = 8):
        # bot init
        super().__init__(intents = discord.Intents.all(), command_prefix=command_prefix)
        self.db = DB_factory(db_name, db_method)
        self.config_collection = self.db.get_collection_instance(General_DB_Names.Config_data.value)
        self.synced = False
        # bot options
        self.added = False
        self.alert_when_online = alert_when_online
        # bot logger
        self.logger = logger(self) 
        # bot secret key
        self.secret_key = secret_key
        # create features dict
        self.features = {}
        self.is_debug = debug
        self.permissions_code=permissions_code
        if error_handler is None:
            self.error_handler = self.default_error_handler
        else:
            self.error_handler = error_handler

        # adding event callbacks support
        self.add_scheduler_events()
        self.add_event_callback_support()



        @self.tree.command(name = 'get_invite_link', description='get invite link for this bot')
        async def get_invite_link(interaction):
            await interaction.response.send_message(f'https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions={self.permissions_code}&scope=bot', ephemeral=True)
    
        @self.tree.command(name = 'get_guild_config', description='get guild config')
        @app_commands.check(permission_checks.is_admin)
        async def get_guild_config(interaction):
            this_server_config = server_config(interaction.guild.id)
            res = 'guild config: \n'
            guild_config = this_server_config.get_params()
            for key in guild_config:
                res += f'\t{key} : {guild_config[key]}\n'
            await interaction.response.send_message(res, ephemeral=True)


    async def get_message(self, message_id, channel : discord.TextChannel, limit : int):
        async for message in channel.history(limit=limit):
            if int(message.id) == int(message_id):
                return message

    def get_all_members_list(self):
        members = []
        for member in self.get_all_members():
            if member not in members:
                members.append(member)
        return members

    async def on_ready(self):
        # running on_ready callbacks
        await self.wait_until_ready()
        #syncing commands tree to discord
        for callback in self.on_ready_callbacks:
            await callback()
        
        # adding error handler to all commands
        if not self.is_debug:
            for x in self.tree.get_commands():
                @x.error
                async def error_handler(interaction, error=None):
                    await self.error_handler(interaction, error)
                    if error is not None:
                        self.log(str(error))
                        print(type(error))

        # syncing commands tree to discord
        if not self.synced:
            self.log('=================================\nsyncing commands tree to discord')
            await self.tree.sync()
            self.synced = True
            self.log('synced \
            \n=================================')
        
        # printing active guilds
        self.log('im active on: ')
        for guild in self.guilds:
            self.log('\t    ' + str(guild.name) + ' (' + str(guild.id) + ')')
        # starting scheduler
        print('starting scheduler')
        self.go_every_hour.start()
        self.go_every_5_hours.start()
        self.go_every_day.start()




        # alerting when joining a guild
        @self.generic_event
        async def on_guild_join(guild):
            # sync commands tree to discord guild
            await self.tree.sync(guild=guild)
            self.log('bot joined guild: ' + str(guild.name) + ' (' + str(guild.id) + ')')
            for callback in self.on_guild_join_callbacks:
                await callback(guild)

    
    def generic_event(self, coro):
        async def wrapper(*args, **kwargs):
            for callback in self.on_before_any_event_callbacks:
                callback(coro.__name__, *args, **kwargs)
            await coro(*args, **kwargs)
            for callback in self.on_after_any_event_callbacks:
                callback(coro.__name__, *args, **kwargs)

        wrapper.__name__ = coro.__name__
        return self.event(wrapper)


    def add_event_callback_support(self):
        self.on_voice_state_update_callbacks = []
        self.on_ready_callbacks = []
        self.on_session_resumed_callbacks = []

        self.on_message_callbacks = []
        self.on_message_delete_callbacks = []
        self.on_message_edit_callbacks = []

        self.on_reaction_add_callbacks = []
        self.on_reaction_remove_callbacks = []

        self.on_invite_create_callbacks = []
        self.on_invite_delete_callbacks = []

        self.on_member_join_callbacks = []
        self.on_member_remove_callbacks = []
        self.on_member_update_callbacks = []
        self.on_member_ban_callbacks = []
        self.on_member_unban_callbacks = []

        self.on_guild_role_create_callbacks = []
        self.on_guild_role_delete_callbacks = []
        self.on_guild_role_update_callbacks = []

        self.on_guild_channel_create_callbacks = []
        self.on_guild_channel_delete_callbacks = []
        self.on_guild_channel_update_callbacks = []

        self.on_guild_join_callbacks = []
        self.on_guild_remove_callbacks = []

        self.on_before_any_event_callbacks = []
        self.on_after_any_event_callbacks = []
        

        # every time a member moves to a different voice channel
        @self.generic_event
        async def on_voice_state_update(member, before, after):
            for callback in self.on_voice_state_update_callbacks:
                await callback(member, before, after)

        @self.generic_event
        async def on_guild_channel_delete(channel):
            for callback in self.on_guild_channel_delete_callbacks:
                await callback(channel)

        @self.generic_event
        async def on_resumed():
            self.log("session resumed")
            for callback in self.on_session_resumed_callbacks:
                # print callback type
                self.log('activating: ' + str(callback))
                # start callback
                await callback()

        @self.generic_event
        async def on_message(message):
            for callback in self.on_message_callbacks:
                await callback(message)
            if message.content.startswith(str(self.command_prefix) + "devs_command") and message.author.id in self.developers_list:
                await self.handle_dev_command(message)

        @self.generic_event
        async def on_message_edit(before, after):
            for callback in self.on_message_edit_callbacks:
                await callback(before, after)

        @self.generic_event
        async def on_reaction_add(reaction, user):
            for callback in self.on_reaction_add_callbacks:
                await callback(reaction, user)

        @self.generic_event
        async def on_reaction_remove(reaction, user):
            for callback in self.on_reaction_remove_callbacks:
                await callback(reaction, user)

        @self.generic_event
        async def on_invite_create(invite):
            for callback in self.on_invite_create_callbacks:
                await callback(invite)
        
        @self.generic_event
        async def on_invite_delete(invite):
            for callback in self.on_invite_delete_callbacks:
                await callback(invite)



        @self.generic_event
        async def on_member_join(member):
            for callback in self.on_member_join_callbacks:
                await callback(member)
        
        @self.generic_event
        async def on_member_remove(member):
            for callback in self.on_member_remove_callbacks:
                await callback(member)
        
        @self.generic_event
        async def on_member_update(before, after):
            for callback in self.on_member_update_callbacks:
                await callback(before, after)

        @self.generic_event
        async def on_member_ban(member):
            for callback in self.on_member_ban_callbacks:
                await callback(member)

        @self.generic_event
        async def on_member_unban(member):
            for callback in self.on_member_unban_callbacks:
                await callback(member)

        @self.generic_event
        async def on_guild_role_create(role):
            for callback in self.on_guild_role_create_callbacks:
                await callback(role)

        @self.generic_event
        async def on_guild_role_delete(role):
            for callback in self.on_guild_role_delete_callbacks:
                await callback(role)

        @self.generic_event
        async def on_guild_role_update(before, after):
            for callback in self.on_guild_role_update_callbacks:
                await callback(before, after)

        @self.generic_event
        async def on_guild_channel_create(channel):
            for callback in self.on_guild_channel_create_callbacks:
                await callback(channel)
        
        @self.generic_event
        async def on_message_delete(message):
            for callback in self.on_message_delete_callbacks:
                await callback(message)

        @self.generic_event
        async def on_guild_channel_update(before, after):
            for callback in self.on_guild_channel_update_callbacks:
                await callback(before, after)
        @self.generic_event
        async def on_guild_remove(guild):
            for callback in self.on_guild_remove_callbacks:
                await callback(guild)

        ################################################################
        # on_guild join is placed on the on_ready event function above #
        ################################################################

    def add_on_session_resumed_callback(self, callback):
        self.on_session_resumed_callbacks.append(callback)
        self.log("added on_session_resumed_callback: " + str(callback.__name__))

    def add_on_ready_callback(self, callback):
        self.on_ready_callbacks.append(callback)
        self.log("added on_ready_callback: " + str(callback.__name__))
    
    def add_on_voice_state_update_callback(self, callback):
        self.on_voice_state_update_callbacks.append(callback)
        self.log("added on_voice_state_update_callback: " + str(callback.__name__))

    def add_on_guild_channel_delete_callback(self, callback):
        self.on_guild_channel_delete_callbacks.append(callback)
        self.log("added on_guild_channel_delete_callback: " + str(callback.__name__))

    def add_on_message_callback(self, callback):
        self.on_message_callbacks.append(callback)
        self.log("added on_message_callback: " + str(callback.__name__))

    def add_on_message_delete_callback(self, callback):
        self.on_message_delete_callbacks.append(callback)
        self.log("added on_message_delete_callback: " + str(callback.__name__))

    # need to add to event logger

    # message events

    def add_on_message_edit_callback(self, callback):
        self.on_message_edit_callbacks.append(callback)
        self.log("added on_message_edit_callback: " + str(callback.__name__))
    

    # reaction events

    def add_on_reaction_add_callback(self, callback):
        self.on_reaction_add_callbacks.append(callback)
        self.log("added on_reaction_add_callback: " + str(callback.__name__))
    
    def add_on_reaction_remove_callback(self, callback):
        self.on_reaction_remove_callbacks.append(callback)
        self.log("added on_reaction_remove_callback: " + str(callback.__name__))

    # invite events

    def add_on_invite_create_callback(self, callback):
        self.on_invite_create_callbacks.append(callback)
        self.log("added on_invite_create_callback: " + str(callback.__name__))
    
    def add_on_invite_delete_callback(self, callback):
        self.on_invite_delete_callbacks.append(callback)
        self.log("added on_invite_delete_callback: " + str(callback.__name__))
    
    #member events

    def add_on_member_join_callback(self, callback):
        self.on_member_join_callbacks.append(callback)
        self.log("added on_member_join_callback: " + str(callback.__name__))

    def add_on_member_remove_callback(self, callback):
        self.on_member_remove_callbacks.append(callback)
        self.log("added on_member_remove_callback: " + str(callback.__name__))

    def add_on_member_update_callback(self, callback):
        self.on_member_update_callbacks.append(callback)
        self.log("added on_member_update_callback: " + str(callback.__name__))
    
    def add_on_member_ban_callback(self, callback):
        self.on_member_ban_callbacks.append(callback)
        self.log("added on_member_ban_callback: " + str(callback.__name__))
    
    def add_on_member_unban_callback(self, callback):
        self.on_member_unban_callbacks.append(callback)
        self.log("added on_member_unban_callback: " + str(callback.__name__))
    
    # guild role events

    def add_on_guild_role_create_callback(self, callback):
        self.on_guild_role_create_callbacks.append(callback)
        self.log("added on_guild_role_create_callback: " + str(callback.__name__))

    def add_on_guild_role_delete_callback(self, callback):
        self.on_guild_role_delete_callbacks.append(callback)
        self.log("added on_guild_role_delete_callback: " + str(callback.__name__))

    def add_on_guild_role_update_callback(self, callback):
        self.on_guild_role_update_callbacks.append(callback)
        self.log("added on_guild_role_update_callback: " + str(callback.__name__))

    # channel events

    def add_on_guild_channel_create_callback(self, callback):
        self.on_guild_channel_create_callbacks.append(callback)
        self.log("added on_guild_channel_create_callback: " + str(callback.__name__))

    def add_on_guild_channel_update_callback(self, callback):
        self.on_guild_channel_update_callbacks.append(callback)
        self.log("added on_guild_channel_update_callback: " + str(callback.__name__))

    def add_on_guild_join_callback(self, callback):
        self.on_guild_join_callbacks.append(callback)
        self.log("added on_guild_join_callback: " + str(callback.__name__))

    def add_on_guild_remove_callback(self, callback):
        self.on_guild_remove_callbacks.append(callback)
        self.log("added on_guild_remove_callback: " + str(callback.__name__))

    # all events

    def add_on_before_any_event_callback(self, callback):
        self.on_before_any_event_callbacks.append(callback)
        self.log("added on_before_any_event_callback: " + str(callback.__name__))
    
    def add_on_after_any_event_callback(self, callback):
        self.on_after_any_event_callbacks.append(callback)
        self.log("added on_after_any_event_callback: " + str(callback.__name__))

    
    # activation method
    def activate(self): #
        self.run(self.secret_key)

    # get bot's secret key
    def get_secret(self):
        return self.secret_key

    # set logger instance
    def set_logger(self, logger):
        self.logger = logger
        
    # get logger instance
    def get_logger(self):
        return self.logger

    # log to logger
    def log(self, message):
        if self.logger is not None:
            self.logger.log(message)
            print(self.logger.remove_emojis(message)) #
        else:
            try:
                print(message)
            except:
                print('failed to print message')
    
    # add features to bot
    def add_features(self, *features):
        self.log('================================================================')
        for feature in features:
            if feature != features[0]:
                self.log('----------------------------------------------------------------')
            self.add_feature(feature)

        self.log('================================================================')

    # add feature to bot
    def add_feature(self, feature):
        # print feature class name
        self.log("| adding feature: " + str(feature)+ ' |')
        if type(self.features) is not dict:
            self.features = {}
        
        self.features[str(feature)] = feature(self)


    def add_scheduler_events(self):
        self.every_hour_callbacks = []
        self.every_5_hours_callbacks = []
        self.every_day_callbacks = []

    @tasks.loop(hours=1)
    async def go_every_hour(self):
        self.log('going over every hour callbacks:')
        self.log('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
        for callback in self.every_hour_callbacks:
            self.log('----------------------------------------')
            self.log('\tactivating\t' + str(callback.__name__) + '()')
            self.log('----------------------------------------')
            await callback()
            
        self.log('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')

    @tasks.loop(hours=5)
    async def go_every_5_hours(self):
        self.log('going over every 5 hours callbacks:')
        self.log('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
        for callback in self.every_5_hours_callbacks:
            self.log('----------------------------------------')
            self.log('\tactivating\t' + str(callback.__name__) + '()')
            self.log('----------------------------------------')
            await callback()
            
        self.log('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')

    @tasks.loop(hours=24)
    async def go_every_day(self):
        self.log('going over every day callbacks:')
        self.log('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
        for callback in self.every_day_callbacks:
            self.log('----------------------------------------')
            self.log('\tactivating\t' + str(callback.__name__) + '()')
            self.log('----------------------------------------')
            await callback()
            
        self.log('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')

    def add_every_hour_callback(self, callback):
        self.every_hour_callbacks.append(callback)
        self.log("added every_hour_callback: " + str(callback.__name__))
    
    def add_every_5_hours_callback(self, callback):
        self.every_5_hours_callbacks.append(callback)
        self.log("added every_5_hours_callback: " + str(callback.__name__))

    def add_every_day_callback(self, callback):
        self.every_day_callbacks.append(callback)
        self.log("added every_day_callback: " + str(callback.__name__))

    async def default_error_handler(self, interaction, error=None):
        embed = discord.Embed(title='You do not have permissions to use this command')
        print(error.with_traceback(None))
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    async def handle_dev_command(self, message): #
        def dict_to_str(my_dict, indent=0):
            result_str = ''
            for key, value in my_dict.items():
                if isinstance(value, dict):
                    result_str += ' ' * indent + f"{key}:\n"
                    result_str += dict_to_str(value, indent+2)
                else:
                    result_str += ' ' * indent + f"{key}: {value}\n"
            return result_str
        content = message.content[len('!devs_command '):]
        if content == 'get_member_db':
            data = dict_to_str(per_id_db.get_all_data(), 4)
            await message.author.send(file=discord.File(io.BytesIO(data.encode()), filename='members_db.txt'))

    
