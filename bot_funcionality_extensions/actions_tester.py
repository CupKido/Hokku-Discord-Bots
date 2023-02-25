import discord
import nacl
from discord.ext import commands
from Interfaces.IGenericBot import IGenericBot


class actions_tester:
    def __init__(self, client : IGenericBot):
        self.bot_client = client
        self.voice_clients = {}
        @client.tree.command(name = 'join_vc', description='join a vc')
        @commands.has_permissions(administrator=True)
        async def join_a_vc(interaction: discord.Interaction, channel : discord.VoiceChannel):
            self.voice_clients[interaction.guild.id] = await channel.connect()
            await interaction.response.send_message('joined vc', ephemeral=True)
        
        @client.tree.command(name = 'leave_vc', description='leave a vc')
        @commands.has_permissions(administrator=True)
        async def leave_a_vc(interaction: discord.Interaction):
            await self.voice_clients[interaction.guild.id].disconnect()
            await interaction.response.send_message('left vc', ephemeral=True)