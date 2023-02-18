import discord
from discord import app_commands
import asyncio
from DB_instances.generic_config_interface import server_config
class GenericBot_client(discord.Client):
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
        self.logger = None 
        # bot secret key
        self.secret_key = secret_key
        # adding event callbacks support
        self.add_event_callback_support()
    
    

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
                await callback(after)


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