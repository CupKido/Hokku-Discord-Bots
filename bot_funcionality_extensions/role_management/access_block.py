import discord 
from discord.ext import commands
from Interfaces.BotFeature import BotFeature

class access_block_feature(BotFeature):
    ACCESS_BLOCKED = 'access_blocked' # whether access is currently blocked
    IS_OWNER = 'is_owner' # whether only owner can block access
    IS_CHAINED = 'is_chained' # whether the allowed users can allow other users to use the bot
    ALLOWED_USERS = 'allowed_users' # list of users that can use the bot
    ALLOWED_ROLES = 'allowed_roles' # list of roles that can use the bot

    def __init__(self, bot):
        super().__init__(bot)
        self.feature_collection = bot.db.get_collection_instance('BotAccessBlock')
        bot.add_on_before_any_command_callback(self.can_use)
        @bot.generic_command(name = 'block_access', description='block access to bot commands')
        @commands.has_permissions(administrator=True)
        async def block_access(interaction: discord.Interaction, is_chained: bool = False):
            guild_data = self.feature_collection.get(interaction.guild.id)
            if self.ACCESS_BLOCKED in guild_data.keys() and type(guild_data[self.ACCESS_BLOCKED]) is bool:
                if guild_data[self.ACCESS_BLOCKED]:
                    if guild_data[self.IS_OWNER]:
                        if interaction.user.id != interaction.guild.owner_id:
                            await interaction.response.send_message('only owner can turn off access block', ephemeral=True)
                            return
                guild_data[self.ACCESS_BLOCKED] = not guild_data[self.ACCESS_BLOCKED]
            else:
                guild_data[self.ACCESS_BLOCKED] = True
            if interaction.user.id == interaction.guild.owner_id:
                guild_data[self.IS_OWNER] = True
            else:
                guild_data[self.IS_OWNER] = False
            guild_data[self.IS_CHAINED] = is_chained
            self.feature_collection.set(interaction.guild.id, guild_data)
            await interaction.response.send_message('Access block status - ' + str(guild_data[self.ACCESS_BLOCKED]), 
                                                    ephemeral=True)

        @bot.generic_command(name = 'allow_user', description='allow a user to use the bot')
        async def allow_user(interaction: discord.Interaction, user: discord.User):
            guild_data = self.feature_collection.get(interaction.guild.id)
            if not await self.can_modify(interaction, guild_data):
                return
            if self.ALLOWED_USERS not in guild_data.keys() or guild_data[self.ALLOWED_USERS] is None or type(guild_data[self.ALLOWED_USERS]) is not list:
                guild_data[self.ALLOWED_USERS] = []
            if user.id in guild_data[self.ALLOWED_USERS]:
                await interaction.response.send_message('user already allowed', ephemeral=True)
                return
            guild_data[self.ALLOWED_USERS].append(user.id)
            self.feature_collection.set(interaction.guild.id, guild_data)
            await interaction.response.send_message('user allowed', ephemeral=True)
                    
        @bot.generic_command(name = 'allow_role', description='allow a role to use the bot')
        async def allow_role(interaction: discord.Interaction, role: discord.Role):
            guild_data = self.feature_collection.get(interaction.guild.id)
            if not await self.can_modify(interaction, guild_data):
                return
            if self.ALLOWED_ROLES not in guild_data.keys() or guild_data[self.ALLOWED_ROLES] is None or type(guild_data[self.ALLOWED_ROLES]) is not list:
                guild_data[self.ALLOWED_ROLES] = []
            if role.id in guild_data[self.ALLOWED_ROLES]:
                await interaction.response.send_message('role already allowed', ephemeral=True)
                return
            guild_data[self.ALLOWED_ROLES].append(role.id)
            self.feature_collection.set(interaction.guild.id, guild_data)
            await interaction.response.send_message('role allowed', ephemeral=True)

    async def can_modify(self, interaction, guild_data):
        if guild_data[self.IS_CHAINED]:
            if interaction.user.id in guild_data[self.ALLOWED_USERS]:
                return True
            # check if user has a role that is allowed
            role_found = False
            for role in interaction.user.roles:
                if role.id in guild_data[self.ALLOWED_ROLES]:
                    return True
                    break
            if not role_found:
                await interaction.response.send_message('only allowed users can allow access', ephemeral=True)
                return False
        if guild_data[self.IS_OWNER]:
            if interaction.user.id != interaction.guild.owner_id:
                await interaction.response.send_message('only owner can allow access', ephemeral=True)
                return False
        
        # else check if user is admin
        elif not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message('only admin can allow access', ephemeral=True)
            return False
        return True
        
    async def can_use(self, name, interaction, **params):
        guild_data = self.feature_collection.get(interaction.guild.id)
        if self.ACCESS_BLOCKED in guild_data.keys() and type(guild_data[self.ACCESS_BLOCKED]) is bool:
            if guild_data[self.ACCESS_BLOCKED]:
                if interaction.user.id == interaction.guild.owner_id:
                    return True
                if not guild_data[self.IS_OWNER]:
                    if interaction.user.guild_permissions.administrator:
                        return True
                if self.ALLOWED_USERS not in guild_data.keys() or guild_data[self.ALLOWED_USERS] is None or type(guild_data[self.ALLOWED_USERS]) is not list:
                    guild_data[self.ALLOWED_USERS] = []
                if interaction.user.id in guild_data[self.ALLOWED_USERS]:
                    return True
                if self.ALLOWED_ROLES not in guild_data.keys() or guild_data[self.ALLOWED_ROLES] is None or type(guild_data[self.ALLOWED_ROLES]) is not list:
                    guild_data[self.ALLOWED_ROLES] = []
                for role in interaction.user.roles:
                    if role.id in guild_data[self.ALLOWED_ROLES]:
                        return True
                if not interaction.response.is_done():
                    await interaction.response.send_message('access to command is blocked', ephemeral=True)
                else:
                    await interaction.followup.send('access to command is blocked', ephemeral=True)
                return False
        return True
