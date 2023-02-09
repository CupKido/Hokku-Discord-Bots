import discord

class event_logger:
    def __init__(self, bot_client):
        self.bot_client = bot_client
        self.logger = bot_client.get_logger()
        
        self.logger.log('event_logger extension loading...')

        self.bot_client.add_on_ready_callback(self.on_ready)
        self.bot_client.add_on_voice_state_update_callback(self.on_voice_state_update)
        self.bot_client.add_on_guild_channel_delete_callback(self.on_guild_channel_delete)
        self.bot_client.add_on_session_resumed_callback(self.on_session_resumed)
        self.bot_client.add_on_message_callback(self.on_message)
        @bot_client.tree.command(name = 'get_todays_event_logs', description='get todays event logs')
        async def get_todays_event_logs(interaction: discord.Interaction):
            event_logs = '\n'.join([x for x in self.logger.get_logs().split('\n') if x.startswith('event_logger')])
            await interaction.response.send_message(event_logs, ephemeral=True)

    async def on_ready(self):
        self.log("on_ready")

    async def on_voice_state_update(self, member, before, after):
        #self.log("on_voice_state_update")
        pass

    async def on_guild_channel_delete(self, channel):
        self.log("on_guild_channel_delete")

        pass

    async def on_session_resumed(self):
        self.log("on_session_resumed")

    async def on_message(self, message):
        self.log("on_message. length = " + str(len(message.content)))
    
    def log(self, message):
        # print(message)
        self.logger.log_instance(message, self)

    