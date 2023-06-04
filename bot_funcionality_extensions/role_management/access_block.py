import discord 
from discord.ext import commands
from Interfaces.BotFeature import BotFeature
from ui_components_extension.generic_ui_comps import Generic_View, mode_styles
from ui_components_extension import ui_tools
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

        @bot.generic_command(name = 'block_access_menu', description='block access menu')
        async def block_access_menu(interaction: discord.Interaction):
            await interaction.response.send_message('block access menu', ephemeral=True, view=await self.get_block_access_menu(interaction))
    
        @bot.generic_command(name = 'allow_role', description='allow a role to use the bot')
        async def allow_role(interaction: discord.Interaction, role: discord.Role):
            guild_data = self.feature_collection.get(interaction.guild.id)
            if not await self.can_modify(interaction, guild_data):
                await interaction.response.send_message('you cannot modify this', ephemeral=True)
                return
            if self.ALLOWED_ROLES not in guild_data.keys() or guild_data[self.ALLOWED_ROLES] is None or type(guild_data[self.ALLOWED_ROLES]) is not list:
                guild_data[self.ALLOWED_ROLES] = []
            if role.id in guild_data[self.ALLOWED_ROLES]:
                await interaction.response.send_message('role already allowed', ephemeral=True)
                return
            guild_data[self.ALLOWED_ROLES].append(role.id)
            self.feature_collection.set(interaction.guild.id, guild_data)
            await interaction.response.send_message('role allowed', ephemeral=True)

    async def allow_user_selector_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_data = self.feature_collection.get(interaction.guild.id)
        if self.ALLOWED_USERS not in guild_data.keys() or guild_data[self.ALLOWED_USERS] is None or type(guild_data[self.ALLOWED_USERS]) is not list:
            guild_data[self.ALLOWED_USERS] = []
        for user in interaction.data['values']:
            if user not in guild_data[self.ALLOWED_USERS]:
                guild_data[self.ALLOWED_USERS].append(user)
                await interaction.followup.send(f'<@{user}> user allowed', ephemeral=True)
            else:
                await interaction.followup.send(f'<@{user}> user already allowed', ephemeral=True)
        self.feature_collection.set(interaction.guild.id, guild_data)
  
    async def allow_role_selector_callback(self, interaction: discord.Interaction, select, view):
        selected_role = ui_tools.get_select_values(interaction)[0]
        guild_data = self.feature_collection.get(interaction.guild.id)
        if self.ALLOWED_ROLES not in guild_data.keys() or guild_data[self.ALLOWED_ROLES] is None or type(guild_data[self.ALLOWED_ROLES]) is not list:
            guild_data[self.ALLOWED_ROLES] = []
        if selected_role not in guild_data[self.ALLOWED_ROLES]:
            guild_data[self.ALLOWED_ROLES].append(selected_role)
            await interaction.followup.send(f'<@&{selected_role}> role allowed', ephemeral=True)
        else:
            await interaction.followup.send(f'<@&{selected_role}> role already allowed', ephemeral=True)
        self.feature_collection.set(interaction.guild.id, guild_data)
        await interaction.response.edit_message(view=await self.get_block_access_menu(interaction))

    
    async def block_access_button_callback(self, interaction: discord.Interaction, button, view):
        guild_data = self.feature_collection.get(interaction.guild.id)
        if self.ACCESS_BLOCKED in guild_data.keys() and type(guild_data[self.ACCESS_BLOCKED]) is bool:
            guild_data[self.ACCESS_BLOCKED] = not guild_data[self.ACCESS_BLOCKED]
        else:
            guild_data[self.ACCESS_BLOCKED] = button.value
        button.style=mode_styles.get_on_off(guild_data[self.ACCESS_BLOCKED])
        self.feature_collection.set(interaction.guild.id, guild_data)
        await interaction.response.edit_message(view=view)

    async def chain_access_button_callback(self, interaction: discord.Interaction, button, view):
        guild_data = self.feature_collection.get(interaction.guild.id)
        if self.IS_CHAINED in guild_data.keys() and type(guild_data[self.IS_CHAINED]) is bool:
            guild_data[self.IS_CHAINED] = not guild_data[self.IS_CHAINED]
        else:
            guild_data[self.IS_CHAINED] = button.value
        button.style=mode_styles.get_on_off(guild_data[self.IS_CHAINED])
        self.feature_collection.set(interaction.guild.id, guild_data)
        await interaction.response.edit_message(view=view)

    async def disallow_user_selector_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_data = self.feature_collection.get(interaction.guild.id)
        if self.ALLOWED_USERS not in guild_data.keys() or guild_data[self.ALLOWED_USERS] is None or type(guild_data[self.ALLOWED_USERS]) is not list:
            guild_data[self.ALLOWED_USERS] = []
        for user in interaction.data['values']:
            if user in guild_data[self.ALLOWED_USERS]:
                guild_data[self.ALLOWED_USERS].remove(user)
                await interaction.followup.send(f'<@{user}> user removed', ephemeral=True)
            else:
                await interaction.followup.send(f'<@{user}> user already out', ephemeral=True)
        self.feature_collection.set(interaction.guild.id, guild_data)

    async def disallow_role_selector_callback(self, interaction: discord.Interaction, select, view):
        selected_role = ui_tools.get_select_values(interaction)[0]
        guild_data = self.feature_collection.get(interaction.guild.id)
        if self.ALLOWED_ROLES not in guild_data.keys() or guild_data[self.ALLOWED_ROLES] is None or type(guild_data[self.ALLOWED_ROLES]) is not list:
            guild_data[self.ALLOWED_ROLES] = []
        if selected_role in guild_data[self.ALLOWED_ROLES]:
            guild_data[self.ALLOWED_ROLES].remove(selected_role)
            await interaction.followup.send(f'<@&{selected_role}> role removed', ephemeral=True)
        else:
            await interaction.followup.send(f'<@&{selected_role}> role already out', ephemeral=True)
        self.feature_collection.set(interaction.guild.id, guild_data)
        
        await interaction.response.edit_message(view=await self.get_block_access_menu(interaction))


    async def set_owner_only_button_callback(self, interaction: discord.Interaction, button, view):
        guild_data = self.feature_collection.get(interaction.guild.id)
        if self.IS_OWNER in guild_data.keys() and type(guild_data[self.IS_OWNER]) is bool:
            guild_data[self.IS_OWNER] = not guild_data[self.IS_OWNER]
        else:
            guild_data[self.IS_OWNER] = button.value
        button.style=mode_styles.get_on_off(guild_data[self.IS_OWNER])
        self.feature_collection.set(interaction.guild.id, guild_data)
        await interaction.response.edit_message(view=view)

    def can_modify(self, interaction, guild_data):
        if guild_data[self.IS_CHAINED]:
            if interaction.user.id in guild_data[self.ALLOWED_USERS]:
                return True
            # check if user has a role that is allowed
            role_found = False
            for role in interaction.user.roles:
                if role.id in guild_data[self.ALLOWED_ROLES]:
                    return True
            if not role_found:
                return False
        if guild_data[self.IS_OWNER]:
            if interaction.user.id != interaction.guild.owner_id:
                return False
        
        # else check if user is admin
        elif not interaction.user.guild_permissions.administrator:
            return False
        return True
        
    async def get_block_access_menu(self, interaction):
        my_view = Generic_View()
        guild_data = self.feature_collection.get(interaction.guild.id)
        access_blocked = guild_data[self.ACCESS_BLOCKED]
        is_owner = guild_data[self.IS_OWNER]
        is_chained = guild_data[self.IS_CHAINED]
        if not is_owner and interaction.user.guild_permissions.administrator or interaction.user.id == interaction.guild.owner_id:
            my_view.add_generic_button(label='block access', 
                                        style=mode_styles.get_on_off(access_blocked), 
                                        value=access_blocked, 
                                        callback=self.block_access_button_callback)
            my_view.add_generic_button(label='chain access', style=mode_styles.get_on_off(is_chained), 
                                        value=is_chained, callback=self.chain_access_button_callback)
        
        if self.can_modify(interaction, guild_data):
            my_view.add_user_selector(placeholder='allow user', min_values=0, callback=self.allow_user_selector_callback)
            options = [{'label': role.name, 'value': role.id, 'description' : ''} for role in interaction.guild.roles][:25]
            my_view.add_generic_select(placeholder='allow role', min_values=0, max_values=1, options=options, callback=self.allow_role_selector_callback)

        if not is_owner and interaction.user.guild_permissions.administrator or interaction.user.id == interaction.guild.owner_id:
            my_view.add_user_selector(placeholder='disallow user', min_values=0, callback=self.disallow_user_selector_callback)
            options = [{'label': role.name, 'value': role.id, 'description' : ''} for role in interaction.guild.roles][:25]
            my_view.add_generic_select(placeholder='select role', min_values=0, max_values=1, options=options, callback=self.disallow_role_selector_callback)

        if interaction.user.id == interaction.guild.owner_id:
            my_view.add_generic_button(label='set owner only', style=mode_styles.get_on_off(is_owner), value=is_owner, callback=self.set_owner_only_button_callback)
        
        return my_view

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
