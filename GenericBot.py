import discord
from discord import app_commands
from DB_instances.server_config_interface import server_config
class GenericBot_client(discord.Client):
    def __init__(self, secret_key, alert_when_online : bool = False):
        super().__init__(intents = discord.Intents.all())
        self.tree = app_commands.CommandTree(self)
        self.synced = False
        self.added = False
        self.alert_when_online = alert_when_online
        self.logger = None 
        self.secret_key = secret_key
        self.add_event_callback_support()
    
    def set_logger(self, logger):
        self.logger = logger

    async def on_ready(self):
        await self.wait_until_ready()
        self.log('bot is ready')
        #syncing commands tree to discord
        if not self.synced:
            self.log('=================================\nsyncing commands tree to discord')
            await self.tree.sync()
            self.synced = True
            self.log('synced \
            \n=================================')
        # printing active guilds
        self.log('im active on: ')
        for guild in self.guilds:
            if self.alert_when_online:
                guildID = guild.id
                channel = self.get_channel(int(server_config.get_specific_announcement_channel(guildID)))
                await channel.send(f'im active, my name is {self.user}')
            self.log('\t' + str(guild.name))
        # running on_ready callbacks
        for callback in self.on_ready_callbacks:
            await callback()

    def add_event_callback_support(self):
        self.on_voice_state_update_callbacks = []
        self.on_ready_callbacks = []
        self.on_guild_channel_delete_callbacks = []
        self.on_session_resumed_callbacks = []
        self.on_message_callbacks = []
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

    def add_on_session_resumed_callback(self, callback):
        self.on_session_resumed_callbacks.append(callback)
        self.log("added on_session_resumed_callback: " + str(callback))

    def add_on_ready_callback(self, callback):
        self.on_ready_callbacks.append(callback)
        self.log("added on_ready_callback: " + str(callback))
    
    def add_on_voice_state_update_callback(self, callback):
        self.on_voice_state_update_callbacks.append(callback)
        self.log("added on_voice_state_update_callback: " + str(callback))

    def add_on_guild_channel_delete_callback(self, callback):
        self.on_guild_channel_delete_callbacks.append(callback)
        self.log("added on_guild_channel_delete_callback: " + str(callback))

    def add_on_message_callback(self, callback):
        self.on_message_callbacks.append(callback)
        self.log("added on_message_callback: " + str(callback))

    def activate(self): #
        self.run(self.secret_key)

    def get_secret(self):
        return self.secret_key
    
    def log(self, message):
        print(message)
        if self.logger is not None:
            self.logger.log(message)