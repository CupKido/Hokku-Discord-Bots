import discord
import io
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
            guild_logs = self.logger.get_guild_logs(interaction.guild.id)
            if not guild_logs:
                await interaction.response.send_message('no logs found', ephemeral=True)
            else:
                event_logs = '\n'.join([x for x in guild_logs.split('\n') if x.startswith('event_logger')])
                if len(event_logs) < 2000:
                    await interaction.response.send_message(event_logs, ephemeral=True)
                else:
                    # send as file
                    await interaction.response.send_message('logs are too long, sending as file on dms', ephemeral=True)
                    await interaction.user.send(file=discord.File(io.BytesIO(event_logs.encode()), filename='event_logs.txt'))


    async def on_ready(self):
        self.log("on_ready")

    async def on_voice_state_update(self, member, before, after):
        
        self.log_guild("on_voice_state_update. member name: " + member.name + 
            ". before: " + before.channel.name + ". after: " + after.channel.name,
            member.guild)
        pass

    async def on_guild_channel_delete(self, channel):
        if channel is not None:
            self.log_guild("on_guild_channel_delete. channel name: " + channel.name, channel.guild)

        pass

    async def on_session_resumed(self):
        self.log("on_session_resumed")

    async def on_message(self, message):
        # check if message is not None
        if message is not None:
            # check if message is from bot
            if message.author != self.bot_client.user:
                self.log_guild("on_message. length = " + str(len(message.content)), message.guild)
    
    def log(self, message):
        # print(message)
        self.logger.log_instance(message, self)
    
    def log_guild(self, message, guild):
        if self.logger is not None:
            self.logger.log_guild_instance(message, guild.id, self)

    