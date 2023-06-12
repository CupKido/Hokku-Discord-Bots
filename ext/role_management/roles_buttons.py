# a feature that lets you add roles to users by clicking on a button.
# admin options would be:
# - create role message - adding description etc.
# - add/remove role buttons from the message.
# code will maintain the roles message and add/remove buttons as needed.
# for maintainance purposes, the code will also maintain a list 
# of all the roles that are currently in the message in the server's db.
import discord 
from discord.ext import commands
from Interfaces.BotFeature import BotFeature
from discord.ui import View
from ui_ext.buttons.role_button import role_button
from ui_ext.generic_ui_comps import Generic_Modal, Generic_View
import permission_checks
import ui_ext.ui_tools as ui_tools
from discord import app_commands

class roles_buttons(BotFeature):

    ROLES_MESSAGE_ID = 'roles_message_id'
    ROLES_MESSAGE_CHANNEL_ID = 'roles_message_channel_id'
    BUTTON_ROLES_LIST = 'button_roles_list'
    # button role structure: {'role_id': role_id, 'title': 'title', 'emoji': 'emoji'}
    ROLEBUTTONSDB = 'RolesButtonsDB'
    ADDED_SERVERS_LIST = 'added_servers_list'
    def __init__(self, bot):
        super().__init__(bot)
        self.feature_collection = bot.db.get_collection_instance('RolesButtons')
        
        # take care of maintainance
        bot.add_on_ready_callback(self.maintain_buttons)
        bot.add_on_session_resumed_callback(self.maintain_buttons)
        bot.add_every_5_hours_callback(self.maintain_buttons)


        # add commands
        @bot.tree.command(name = 'create_button_roles', description='create buttons roles message')
        @app_commands.check(permission_checks.is_admin)
        async def create_button_roles(interaction: discord.Interaction, channel: discord.TextChannel):
            if channel is None:
                await interaction.response.send_message('Channel not found')
                return
            my_modal = Generic_Modal(title='Roles Buttons message')
            my_modal.add_input(label='Message title', placeholder='Message title', max_length=100, required=True)
            my_modal.add_input(label='Message description', placeholder='Message description', max_length=100, required=False, long=True)
            my_modal.set_callback(self.create_button_roles_modal_callback)
            await interaction.response.send_modal(my_modal)
            guild_data = self.feature_collection.get(interaction.guild.id)
            guild_data[self.ROLES_MESSAGE_CHANNEL_ID] = channel.id
            self.feature_collection.set(interaction.guild.id, guild_data)

        @bot.tree.command(name = 'add_button_role', description='add a button role to the message')
        @app_commands.check(permission_checks.is_admin)
        async def add_button_role(interaction: discord.Interaction, role: discord.Role, label: str, emoji: str = None):
            await interaction.response.defer()
            features_data = self.feature_collection.get(self.ROLEBUTTONSDB)
            if self.ADDED_SERVERS_LIST not in features_data:
                features_data[self.ADDED_SERVERS_LIST] = []
            if interaction.guild.id not in features_data[self.ADDED_SERVERS_LIST]:
                features_data[self.ADDED_SERVERS_LIST].append(interaction.guild.id)
            self.feature_collection.set(self.ROLEBUTTONSDB, features_data)
            guild_data = self.feature_collection.get(interaction.guild.id)
            if self.BUTTON_ROLES_LIST not in guild_data:
                guild_data[self.BUTTON_ROLES_LIST] = []
            guild_data[self.BUTTON_ROLES_LIST].append({'role_id': role.id, 'title': label, 'emoji': emoji})
            self.feature_collection.set(interaction.guild.id, guild_data)
            await self.maintain_buttons_for_guild(interaction.guild.id)
            await interaction.followup.send('Role added successfully', ephemeral=True)
            await self._log_guild(f'Role {role.name} added to the roles message', interaction.guild.id)
    
        @bot.tree.command(name = 'remove_button_role', description='remove a button role from the message')
        @app_commands.check(permission_checks.is_admin)
        async def remove_button_role(interaction: discord.Interaction):
            guild_data = self.feature_collection.get(interaction.guild.id)
            if self.BUTTON_ROLES_LIST not in guild_data or guild_data[self.BUTTON_ROLES_LIST] is None or type(guild_data[self.BUTTON_ROLES_LIST]) is not list:
                await interaction.response.send_message('No button roles found', ephemeral=True)
                return
            options = [{'label' : role_data['title'], 'description':'', 'value' : role_data['role_id']} for role_data in guild_data[self.BUTTON_ROLES_LIST]]
            my_view = Generic_View()
            my_view.add_generic_select(placeholder='Select role to remove', options=options, min_values=1, max_values=1, callback=self.remove_button_role_callback)
            await interaction.response.send_message('Select role to remove', view=my_view, ephemeral=True)

    async def remove_button_role_callback(self, interaction, select, view):
        selected_role_id = select.values[0]
        selected_role_title = select.options[0].label
        guild_data = self.feature_collection.get(interaction.guild.id)
        guild_data[self.BUTTON_ROLES_LIST] = [role_data for role_data in guild_data[self.BUTTON_ROLES_LIST] if role_data['role_id'] != selected_role_id and role_data['title'] != selected_role_title]
        self.feature_collection.set(interaction.guild.id, guild_data)
        await self.maintain_buttons_for_guild(interaction.guild.id)
        await interaction.response.send_message('Role removed successfully', ephemeral=True)
        await self._log_guild(f"Role {selected_role_title} ({selected_role_id}) removed from the roles message", interaction.guild.id)


    async def create_button_roles_modal_callback(self, interaction):
        message_title = ui_tools.get_modal_value(interaction, 0)
        message_description = ui_tools.get_modal_value(interaction, 1)
        await interaction.response.defer()
        guild_data = self.feature_collection.get(interaction.guild.id)
        channel = self.bot_client.get_channel(guild_data[self.ROLES_MESSAGE_CHANNEL_ID])
        if channel is None:
            await interaction.followup.send('Channel not found')
            return
        message = await channel.send(embed=discord.Embed(title=message_title, description=message_description))
        guild_data[self.ROLES_MESSAGE_ID] = message.id
        self.feature_collection.set(interaction.guild.id, guild_data)
        await interaction.followup.send('Roles message created successfully', ephemeral=True)


    async def maintain_buttons(self):
        feature_data = self.feature_collection.get(self.ROLEBUTTONSDB)
        if self.ADDED_SERVERS_LIST not in feature_data:
            feature_data[self.ADDED_SERVERS_LIST] = []
        for guild_id in feature_data[self.ADDED_SERVERS_LIST]:
            await self.maintain_buttons_for_guild(guild_id)

    async def maintain_buttons_for_guild(self, guild_id):
        guild_data = self.feature_collection.get(guild_id)
        # make sure the guild has all the needed data
        if self.ROLES_MESSAGE_ID not in guild_data.keys() or guild_data[self.ROLES_MESSAGE_ID] is None\
            or self.ROLES_MESSAGE_CHANNEL_ID not in guild_data.keys() or guild_data[self.ROLES_MESSAGE_CHANNEL_ID] is None\
            or self.BUTTON_ROLES_LIST not in guild_data.keys() or guild_data[self.BUTTON_ROLES_LIST] is None:
                return
        if type(guild_data[self.BUTTON_ROLES_LIST]) is not list:
            return

        # get the guild and the channel
        guild = self.bot_client.get_guild(guild_id)
        if guild is None:
            return
        channel = guild.get_channel(guild_data[self.ROLES_MESSAGE_CHANNEL_ID]) 
        if channel is None:
            return
        # get the message
        message = await channel.fetch_message(guild_data[self.ROLES_MESSAGE_ID])
        if message is None:
            return
        my_view = View(timeout=None)
        # get the roles and create buttons
        for role_data in guild_data[self.BUTTON_ROLES_LIST]:
            role = guild.get_role(role_data['role_id'])
            if role is None:
                continue
            my_view.add_item(role_button(label=role_data['title'], 
                                            emoji=role_data['emoji'], 
                                            role_id=role_data['role_id'],
                                            style=discord.ButtonStyle.primary))
        # add the view to the message
        await message.edit(content=message.content, embeds=message.embeds, view=my_view)

    




