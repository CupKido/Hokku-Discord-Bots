# a feature that lets you add roles to users by reacting to a message.
# admin options would be:
# add reaction role by message id
# remove reaction role by message id
# add reaction role to last message in channel


import discord
from Interfaces.BotFeature import BotFeature
from discord.ui import View
from ui_ext.buttons.role_button import role_button
from ui_ext.generic_ui_comps import Generic_Modal, Generic_View
import permission_checks
import ui_ext.ui_tools as ui_tools
from discord import app_commands

class reaction_roles(BotFeature):

    REACTION_ROLES_LIST = 'reaction_roles_list'
    # reaction role structure: [{'message_id': message_id, 'reaction_roles': [{'role_id' : role_id, 'emoji' : 'emoji'}...]}...]

    def __init__(self, bot):
        super().__init__(bot)
        self.feature_collection = bot.db.get_collection_instance('ReactionRoles')
        
        bot.add_on_reaction_add_callback(self.on_reaction_add)
        bot.add_on_reaction_remove_callback(self.on_reaction_remove)
        @bot.generic_command(name = 'add_reaction_role', description='add a reaction role to the message')
        @app_commands.check(permission_checks.is_admin)
        async def add_reaction_role(interaction: discord.Interaction, role: discord.Role, message_id : str, emoji: str):
            # check if message exists
            await interaction.response.defer()
            message = await interaction.channel.fetch_message(message_id)
            if message is None:
                await interaction.followup.send('Message not found', ephemeral=True)
                return
            # make sure reaction role doesn't already exist
            guild_data = self.feature_collection.get(interaction.guild.id)
            if self.REACTION_ROLES_LIST not in guild_data.keys():
                guild_data[self.REACTION_ROLES_LIST] = []
            
            for reaction_role in guild_data[self.REACTION_ROLES_LIST]:
                if reaction_role['message_id'] == message_id:
                    for role_data in reaction_role['reaction_roles']:
                        if role_data['role_id'] == role.id:
                            await interaction.followup.send('Reaction role already exists', ephemeral=True)
                            return
                    break
            # add reaction role
            try:
                await message.add_reaction(emoji)
            except discord.errors.HTTPException:
                await interaction.followup.send('Emoji not found', ephemeral=True)
                return
            role_stored = False
            if len(guild_data[self.REACTION_ROLES_LIST]) == 0:
                guild_data[self.REACTION_ROLES_LIST].append({'message_id' : message_id, 'reaction_roles' : [{'role_id' : role.id, 'emoji' : emoji}]})
                role_stored = True
            for reaction_role in guild_data[self.REACTION_ROLES_LIST]:
                if reaction_role['message_id'] == message_id:
                    reaction_role['reaction_roles'].append({'role_id' : role.id, 'emoji' : emoji})
                    role_stored = True
                    break
            if not role_stored:
                guild_data[self.REACTION_ROLES_LIST].append({'message_id' : message_id, 'reaction_roles' : [{'role_id' : role.id, 'emoji' : emoji}]})
                role_stored = True

            self.feature_collection.set(interaction.guild.id, guild_data)
            await interaction.followup.send('Reaction role added', ephemeral=True) 
            await self.log_guild(f"Reaction role added: {role.name} to message {message_id}", interaction.guild.id)

            pass


        @bot.generic_command(name = 'remove_reaction_role', description='remove a reaction role from the message')
        @app_commands.check(permission_checks.is_admin)
        async def remove_reaction_role(interaction: discord.Interaction, role: discord.Role, message_id : int):
            # check if message exists
            await interaction.response.defer()
            message = await interaction.channel.fetch_message(message_id)
            if message is None:
                await interaction.followup.send('Message not found', ephemeral=True)
                return
            # make sure reaction role doesn't already exist
            guild_data = self.feature_collection.get(interaction.guild.id)
            if self.REACTION_ROLES_LIST not in guild_data.keys():
                await interaction.followup.send('Reaction role not found', ephemeral=True)
            reaction_role = None
            for reaction_role in guild_data[self.REACTION_ROLES_LIST]:
                if reaction_role['message_id'] == message_id:
                    for role_data in reaction_role['reaction_roles']:
                        if role_data['role_id'] == role.id:
                            reaction_role = role_data
                            break
                    break
            if reaction_role is None:
                await interaction.followup.send('Reaction role not found', ephemeral=True)
                return
            # remove reaction role
            try:
                await message.remove_reaction(reaction_role['emoji'])
                guild_data[self.REACTION_ROLES_LIST].remove(reaction_role)
                self.feature_collection.set(interaction.guild.id, guild_data)
                await interaction.followup.send('Reaction role removed', ephemeral=True)
                await self.log_guild(f"Reaction role removed: {role.name} ({role.id}) from message {message_id}", interaction.guild.id)
            except discord.errors.HTTPException:
                await interaction.followup.send('Emoji not found', ephemeral=True)
                return

    async def on_reaction_add(self, reaction, user):
        if user.bot or user.id == reaction.message.guild.owner_id:
            return
        guild_data = self.feature_collection.get(reaction.message.guild.id)
        if self.REACTION_ROLES_LIST not in guild_data.keys():
            return
        for reaction_role in guild_data[self.REACTION_ROLES_LIST]:
            if str(reaction.message.id) == reaction_role['message_id']:
                for role_data in reaction_role['reaction_roles']:
                    if role_data['emoji'] == reaction.emoji:
                        role = reaction.message.guild.get_role(role_data['role_id'])
                        await user.add_roles(role)
                        await self.log_guild(f"Reaction role added: {role.name} ({role.id}) to {user.name} ({user.id})", reaction.message.guild.id)
                        return
                break

    async def on_reaction_remove(self, reaction, user):
        if user.bot or user.id == reaction.message.guild.owner_id:
            return
        guild_data = self.feature_collection.get(reaction.message.guild.id)
        if self.REACTION_ROLES_LIST not in guild_data.keys():
            return
        for reaction_role in guild_data[self.REACTION_ROLES_LIST]:
            if str(reaction.message.id) == reaction_role['message_id']:
                for role_data in reaction_role['reaction_roles']:
                    if role_data['emoji'] == reaction.emoji:
                        role = reaction.message.guild.get_role(role_data['role_id'])
                        await user.remove_roles(role)
                        await self.log_guild(f"Reaction role removed: {role.name} ({role.id}) from {user.name} ({user.id})", reaction.message.guild.id)
                        return
                break