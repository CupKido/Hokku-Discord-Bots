import discord
from discord import app_commands
from Interfaces.IGenericBot import IGenericBot
import asyncio
from DB_instances.generic_config_interface import server_config
from bot_funcionality_extensions.logger import logger
from discord.ext import commands, tasks
import time

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




class GenericBot_client(IGenericBot):
    def __init__(self, secret_key, db_method='M', config_uri = None, alert_when_online : bool = False):
        # bot init
        super().__init__(intents = discord.Intents.all())
        server_config.set_method(db_method, config_uri)
        self.tree = app_commands.CommandTree(self)
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
        # adding event callbacks support
        self.add_scheduler_events()
        self.add_event_callback_support()



        @self.tree.command(name = 'get_invite_link', description='get invite link for this bot')
        async def get_invite_link(interaction):
            await interaction.response.send_message(f'https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot', ephemeral=True)
    
        @self.tree.command(name = 'get_guild_config', description='get guild config')
        @commands.has_permissions(administrator=True)
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

    async def on_ready(self):
        # running on_ready callbacks
        await self.wait_until_ready()
        #syncing commands tree to discord
        for callback in self.on_ready_callbacks:
            await callback()
        
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
        @self.event
        async def on_guild_join(guild):
            # sync commands tree to discord guild
            await self.tree.sync(guild=guild)
            self.log('bot joined guild: ' + str(guild.name) + ' (' + str(guild.id) + ')')
            for callback in self.on_guild_join_callbacks:
                await callback(guild)

    def add_event_callback_support(self):
        self.on_voice_state_update_callbacks = []
        self.on_ready_callbacks = []
        self.on_session_resumed_callbacks = []

        self.on_message_callbacks = []
        self.on_message_delete_callbacks = []
        self.on_message_edit_callbacks = []

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

        # every time a member moves to a different voice channel
        @self.event
        async def on_voice_state_update(member, before, after):
            for callback in self.on_voice_state_update_callbacks:
                await callback(member, before, after)

        @self.event
        async def on_guild_channel_delete(channel):
            for callback in self.on_guild_channel_delete_callbacks:
                await callback(channel)

        @self.event
        async def on_resumed():
            self.log("session resumed")
            for callback in self.on_session_resumed_callbacks:
                # print callback type
                self.log('activating: ' + str(callback))
                # start callback
                await callback()

        @self.event
        async def on_message(message):
            for callback in self.on_message_callbacks:
                await callback(message)

        @self.event
        async def on_message_edit(before, after):
            for callback in self.on_message_edit_callbacks:
                await callback(before, after)


        @self.event
        async def on_invite_create(invite):
            for callback in self.on_invite_create_callbacks:
                await callback(invite)
        
        @self.event
        async def on_invite_delete(invite):
            for callback in self.on_invite_delete_callbacks:
                await callback(invite)



        @self.event
        async def on_member_join(member):
            for callback in self.on_member_join_callbacks:
                await callback(member)
        
        @self.event
        async def on_member_remove(member):
            for callback in self.on_member_remove_callbacks:
                await callback(member)
        
        @self.event
        async def on_member_update(before, after):
            for callback in self.on_member_update_callbacks:
                await callback(before, after)

        @self.event
        async def on_member_ban(member):
            for callback in self.on_member_ban_callbacks:
                await callback(member)

        @self.event
        async def on_member_unban(member):
            for callback in self.on_member_unban_callbacks:
                await callback(member)

        @self.event
        async def on_guild_role_create(role):
            for callback in self.on_guild_role_create_callbacks:
                await callback(role)

        @self.event
        async def on_guild_role_delete(role):
            for callback in self.on_guild_role_delete_callbacks:
                await callback(role)

        @self.event
        async def on_guild_role_update(before, after):
            for callback in self.on_guild_role_update_callbacks:
                await callback(before, after)

        @self.event
        async def on_guild_channel_create(channel):
            for callback in self.on_guild_channel_create_callbacks:
                await callback(channel)
        
        @self.event
        async def on_message_delete(message):
            for callback in self.on_message_delete_callbacks:
                await callback(message)

        @self.event
        async def on_guild_channel_update(before, after):
            for callback in self.on_guild_channel_update_callbacks:
                await callback(before, after)
        @self.event
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

    def activate(self): #
        self.run(self.secret_key)

    def get_secret(self):
        return self.secret_key

    def set_logger(self, logger):
        self.logger = logger
        
    def get_logger(self):
        return self.logger

    def log(self, message):
        if self.logger is not None:
            self.logger.log(message)
            print(self.logger.remove_emojis(message)) #
        else:
            try:
                print(message)
            except:
                print('failed to print message')
    
    def add_features(self, *features):
        self.log('================================================================')
        for feature in features:
            if feature != features[0]:
                self.log('----------------------------------------------------------------')
            self.add_feature(feature)

        self.log('================================================================')

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