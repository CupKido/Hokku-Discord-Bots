from Interfaces.BotFeature import BotFeature
import discord
from Interfaces.IGenericBot import IGenericBot

class watching_members_feature(BotFeature):
    def __init__(self, bot: IGenericBot):
        super().__init__(bot)
        self.bot_client.add_on_ready_callback(self.update_presence)
        self.bot_client.add_on_member_join_callback(self.update_presence_member)
        self.bot_client.add_on_member_remove_callback(self.update_presence_member)
        self.bot_client.add_on_guild_join_callback(self.update_presence_guild)
    async def on_ready(self):
        await self.update_presence()
    
    async def update_presence_member(self, member):
        await self.update_presence()
        
    async def update_presence_guild(self, guild):
        await self.update_presence()

    async def update_presence(self):
        await self.bot_client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, 
                                                                          name = f'{len(self.bot_client.users)} Members on {len(self.bot_client.guilds)} Servers'))