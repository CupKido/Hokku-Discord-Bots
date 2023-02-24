import discord
from Interfaces.IGenericBot import IGenericBot
from discord.ext import commands
import io
class event_logger:
    def __init__(self, bot_client : IGenericBot):
        self.bot_client = bot_client
        self.logger = bot_client.get_logger()
        
        self.logger.log('event_logger extension loading...')

        # bot events

        self.bot_client.add_on_ready_callback(self.on_ready)
        self.bot_client.add_on_session_resumed_callback(self.on_session_resumed)

        # message events

        self.bot_client.add_on_message_callback(self.on_message)
        self.bot_client.add_on_message_delete_callback(self.on_message_delete)
        self.bot_client.add_on_message_edit_callback(self.on_message_edit)

        # invite events
        self.bot_client.add_on_invite_create_callback(self.on_invite_create)
        self.bot_client.add_on_invite_delete_callback(self.on_invite_delete)

        # members events

        self.bot_client.add_on_member_join_callback(self.on_member_join)
        self.bot_client.add_on_member_remove_callback(self.on_member_remove)
        self.bot_client.add_on_member_update_callback(self.on_member_update)
        self.bot_client.add_on_member_ban_callback(self.on_member_ban)
        self.bot_client.add_on_member_unban_callback(self.on_member_unban)

        # roles events

        self.bot_client.add_on_guild_role_create_callback(self.on_guild_role_create)
        self.bot_client.add_on_guild_role_delete_callback(self.on_guild_role_delete)
        self.bot_client.add_on_guild_role_update_callback(self.on_guild_role_update)

        # channels events
        self.bot_client.add_on_guild_channel_create_callback(self.on_guild_channel_create)
        self.bot_client.add_on_guild_channel_delete_callback(self.on_guild_channel_delete)
        self.bot_client.add_on_guild_channel_update_callback(self.on_guild_channel_update)

        # vc events
        self.bot_client.add_on_voice_state_update_callback(self.on_voice_state_update)

        # bot in guild events
        self.bot_client.add_on_guild_join_callback(self.on_guild_join)
        # self.bot_client.add_on_guild_remove_callback(self.on_guild_remove)


        self.class_name = 'event_logger'
        #@bot_client.tree.command(name = 'get_todays_event_logs', description='get todays event logs')
        #@commands.has_permissions(administrator=True)
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

    # bot events

    async def on_ready(self):
        self.log("on_ready")




        

    async def on_session_resumed(self):
        self.log("on_session_resumed")

    # bot in guild events

    async def on_guild_join(self, guild):
        self.log("on_guild_join " + guild.name)

    async def on_guild_remove(self, guild):
        self.log("on_guild_remove " + guild.name)

    # members events

    async def on_message(self, message):
        # check if message is not None
        try:
            if message is not None:
                # check if message is from bot
                if message.author != self.bot_client.user:
                    await self.log_guild("on_message. length = " + str(len(message.content)), message.guild)
        except:
            pass
    
    async def on_message_delete(self, message):
        try:
            if message is not None:
                # check if message is from bot
                if message.author != self.bot_client.user:
                    await self.log_guild("on_message_deleted. length = " + str(len(message.content)), message.guild)
        except:
            pass

    async def on_message_edit(self, before, after):
        try:
            if before is not None and after is not None:
                # check if message is from bot
                if before.author != self.bot_client.user:
                    await self.log_guild("on_message_edit. before length = " + str(len(before.content)) + ". after length = " + str(len(after.content)), before.guild)
        except:
            pass
    
    # invite events

    async def on_invite_create(self, invite):
        await self.log_guild("on_invite_create", invite.guild)
    
    async def on_invite_delete(self, invite):
        await self.log_guild("on_invite_delete", invite.guild)

    # members events

    async def on_member_join(self, member):
        await self.log_guild("on_member_join " + member.name, member.guild)

    async def on_member_remove(self, member):
        await self.log_guild("on_member_remove " + member.name, member.guild)
    
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            await self.log_guild(before.display_name + " changed his name to " + after.display_name, before.guild)

    async def on_member_ban(self, member): 
        await self.log_guild("on_member_ban " + member.name, member.guild)
    
    async def on_member_unban(self, member):
        await self.log_guild("on_member_unban " + member.name, member.guild)
    
    # roles events

    async def on_guild_role_create(self, role):
        await self.log_guild("guild_role_create " + role.name, role.guild)

    async def on_guild_role_delete(self, role):
        await self.log_guild("guild_role_delete " + role.name, role.guild)
    
    async def on_guild_role_update(self, before, after):
        await self.log_guild("guild_role_update " + before.name + " to " + after.name, before.guild)

    # channels events

    async def on_guild_channel_create(self, channel):
        await self.log_guild("guild_channel_create " + channel.name, channel.guild)

    async def on_guild_channel_delete(self, channel):
        if channel is not None:
            await self.log_guild("on_guild_channel_delete. channel name: " + channel.name, channel.guild)
    
    async def on_guild_channel_update(self, before, after):
        await self.log_guild("guild_channel_update " + before.name + " to " + after.name, before.guild)

    # vc events

    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            await self.log_guild("on_voice_state_update. member name: " + member.name + 
            ". before: None. after: " + after.channel.name,
            member.guild)
        elif before.channel is not None and after.channel is None:
            await self.log_guild("on_voice_state_update. member name: " + member.name + 
            ". before: " + before.channel.name + ". after: None",
            member.guild)
        elif before.channel is not None and after.channel is not None:
            await self.log_guild("on_voice_state_update. member name: " + member.name + 
                ". before: " + before.channel.name + ". after: " + after.channel.name,
                member.guild)

    def log(self, message):
        # print(message)
        self.logger.log_instance(message, self)
    
    async def log_guild(self, message, guild):
        if self.logger is not None:
            await self.logger.log_guild_instance(message, guild.id, self)

    