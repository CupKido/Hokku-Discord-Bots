import discord
from abc import abstractmethod
from discord import app_commands

class IGenericBot(discord.Client):

    @abstractmethod
    async def on_ready(self):
        pass

    @abstractmethod
    async def get_message(self, message_id, channel : discord.TextChannel, limit : int):
        pass

    @abstractmethod
    def add_on_session_resumed_callback(self, callback):
        pass

    @abstractmethod
    def add_on_ready_callback(self, callback):
        pass

    @abstractmethod
    def add_on_voice_state_update_callback(self, callback):
        pass

    @abstractmethod
    def add_on_guild_channel_delete_callback(self, callback):
        pass

    @abstractmethod
    def add_on_message_callback(self, callback):
        pass

    @abstractmethod
    def add_on_message_delete_callback(self, callback):
        pass

    @abstractmethod
    def add_on_message_edit_callback(self, callback):
        pass

    @abstractmethod
    def add_on_invite_create_callback(self, callback):
        pass

    @abstractmethod
    def add_on_invite_delete_callback(self, callback):
        pass

    @abstractmethod
    def add_on_member_join_callback(self, callback):
        pass

    @abstractmethod
    def add_on_member_remove_callback(self, callback):
        pass

    @abstractmethod
    def add_on_member_update_callback(self, callback):
        pass

    @abstractmethod
    def add_on_member_ban_callback(self, callback):
        pass

    @abstractmethod
    def add_on_member_unban_callback(self, callback):
        pass

    @abstractmethod
    def add_on_guild_role_create_callback(self, callback):
        pass

    @abstractmethod
    def add_on_guild_role_delete_callback(self, callback):
        pass

    @abstractmethod
    def add_on_guild_role_update_callback(self, callback):
        pass

    @abstractmethod
    def add_on_guild_channel_create_callback(self, callback):
        pass

    @abstractmethod
    def add_on_guild_channel_update_callback(self, callback):
        pass

    @abstractmethod
    def add_on_guild_join_callback(self, callback):
        pass

    @abstractmethod
    def add_on_guild_remove_callback(self, callback):
        pass

    @abstractmethod
    def add_every_hour_callback(self, callback):
        pass

    @abstractmethod
    def add_every_5_hours_callback(self, callback):
        pass

    @abstractmethod
    def add_every_day_callback(self, callback):
        pass

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def get_secret(self):
        pass

    @abstractmethod
    def set_logger(self, logger):
        pass

    @abstractmethod
    def get_logger(self):
        pass

    @abstractmethod
    def log(self, message):
        pass