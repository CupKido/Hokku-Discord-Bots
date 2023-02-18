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
        self.bot_client.add_on_message_delete_callback(self.on_message_delete)
        self.bot_client.add_on_message_edit_callback(self.on_message_edit)
        self.bot_client.add_on_invite_create_callback(self.on_invite_create)
        self.bot_client.add_on_invite_delete_callback(self.on_invite_delete)
        self.bot_client.add_on_member_join_callback(self.on_member_join)
        self.bot_client.add_on_member_remove_callback(self.on_member_remove)
        self.bot_client.add_on_member_update_callback(self.on_member_update)
        self.bot_client.add_on_member_ban_callback(self.on_member_ban)
        self.bot_client.add_on_member_unban_callback(self.on_member_unban)
        self.bot_client.add_on_guild_role_create_callback(self.on_guild_role_create)
        self.bot_client.add_on_guild_role_delete_callback(self.on_guild_role_delete)
        self.bot_client.add_on_guild_role_update_callback(self.on_guild_role_update)
        self.bot_client.add_on_guild_channel_create_callback(self.on_guild_channel_create)
        self.bot_client.add_on_guild_channel_update_callback(self.on_guild_channel_update)
        self.class_name = 'event_logger'
        @bot_client.tree.command(name = 'get_todays_event_logs', description='get todays event logs')
        async def get_todays_event_logs(interaction: discord.Interaction):
            if interaction.guild is None:
                await interaction.response.send_message('this command is only available on servers', ephemeral=True)
                return
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message('you are not an admin', ephemeral=True)
                return
            guild_logs = self.logger.get_guild_logs(interaction.guild.id)
            if not guild_logs:
                await interaction.response.send_message('no logs found', ephemeral=True)
            else:
                event_logs = '\n'.join([x[len(type(self).__name__ +": "):] for x in guild_logs.split('\n') if x.startswith(type(self).__name__)])
                if len(event_logs) < 2000:
                    await interaction.response.send_message(event_logs, ephemeral=True)
                else:
                    # send as file
                    await interaction.response.send_message('logs are too long, sending as file on dms', ephemeral=True)
                    await interaction.user.send(file=discord.File(io.BytesIO(event_logs.encode()), filename='event_logs.txt'))


    async def on_ready(self):
        self.log("on_ready")

    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            self.log_guild("on_voice_state_update. member name: " + member.name + 
            ". before: None. after: " + after.channel.name,
            member.guild)
        elif before.channel is not None and after.channel is None:
            self.log_guild("on_voice_state_update. member name: " + member.name + 
            ". before: " + before.channel.name + ". after: None",
            member.guild)
        elif before.channel is not None and after.channel is not None:
            self.log_guild("on_voice_state_update. member name: " + member.name + 
                ". before: " + before.channel.name + ". after: " + after.channel.name,
                member.guild)


        if channel is not None:
            self.log_guild("on_guild_channel_delete. channel name: " + channel.name, channel.guild)

        pass

    async def on_session_resumed(self):
        self.log("on_session_resumed")

    async def on_guild_join(self, guild):
        self.log("on_guild_join " + guild.name)

    async def on_message(self, message):
        # check if message is not None
        try:
            if message is not None:
                # check if message is from bot
                if message.author != self.bot_client.user:
                    self.log_guild("on_message. length = " + str(len(message.content)), message.guild)
        except:
            pass
    
    async def on_message_delete(self, message):
        try:
            if message is not None:
                # check if message is from bot
                if message.author != self.bot_client.user:
                    self.log_guild("on_message_deleted. length = " + str(len(message.content)), message.guild)
        except:
            pass

    async def on_message_edit(self, before, after):
        try:
            if before is not None and after is not None:
                # check if message is from bot
                if before.author != self.bot_client.user:
                    self.log_guild("on_message_edit. before length = " + str(len(before.content)) + ". after length = " + str(len(after.content)), before.guild)
        except:
            pass
    
    async def on_invite_create(self, invite):
        self.log("on_invite_create")
    
    async def on_invite_delete(self, invite):
        self.log("on_invite_delete")

    async def on_member_join(self, member):
        self.log("on_member_join " + member.name)

    async def on_member_remove(self, member):
        self.log("on_member_remove " + member.name)
    
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            self.log_guild(before.display_name + " changed his name to " + after.display_name, before.guild.id)
        self.log("on_member_update " + before.name + " " + after.name)

    async def on_member_ban(self, member): 
        self.log("on_member_ban " + member.name)
    
    async def on_member_unban(self, member):
        self.log("on_member_unban " + member.name)
    
    async def on_guild_role_create(self, role):
        self.log("guild_role_create " + role.name)

    async def on_guild_role_delete(self, role):
        self.log("guild_role_delete " + role.name)
    
    async def on_guild_role_update(self, before, after):
        self.log("guild_role_update " + before.name + " to " + after.name)

    async def on_guild_channel_create(self, channel):
        self.log("guild_channel_create " + channel.name)

    async def on_guild_channel_delete(self, channel):
        
        self.log("guild_channel_delete " + channel.name)
    
    async def on_guild_channel_update(self, before, after):
        self.log("guild_channel_update " + before.name + " to " + after.name)



    def log(self, message):
        # print(message)
        self.logger.log_instance(message, self)
    
    def log_guild(self, message, guild):
        if self.logger is not None:
            self.logger.log_guild_instance(message, guild.id, self)

    