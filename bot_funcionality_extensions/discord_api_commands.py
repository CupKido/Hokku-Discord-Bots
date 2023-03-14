import discord
from discord.ext import commands
from Interfaces.IGenericBot import IGenericBot
from Interfaces.BotFeature import BotFeature

class discord_api_commands(BotFeature):
    def __init__(self, bot : IGenericBot): 
        super().__init__(bot)
        @bot.tree.command(name = 'send_to', description='sends a message to a user')
        @commands.has_permissions(administrator=True)
        async def send_a_message_to_a_user(interaction: discord.Interaction, user : discord.User, message : str):
            try:
                await user.send(message)
                await interaction.response.send_message('sent message', ephemeral=True)
            except Exception as e:
                await interaction.response.send_message('failed to send message, ' + str(e), ephemeral=True)
                # print exception details
                

        @bot.tree.command(name = 'send_to_by_id', description='sends a message to a user')
        @commands.has_permissions(administrator=True)
        async def send_a_message_to_a_user_by_id(interaction: discord.Interaction, user_id : str, message : str):
            try:
                user = await self.bot_client.fetch_user(int(user_id))
                await user.send(message)
                await interaction.response.send_message('sent message', ephemeral=True)
            except Exception as e:
                await interaction.response.send_message('failed to send message, ' + str(e), ephemeral=True)
        
        @bot.tree.command(name = 'get_user_id', description='gets a user id')
        @commands.has_permissions(administrator=True)
        async def get_user_id(interaction: discord.Interaction, user : discord.User):
                await interaction.response.send_message(user.name + ': ' + str(user.id), ephemeral=True)
                await interaction.response.send_message('sent message', ephemeral=True)
        
        