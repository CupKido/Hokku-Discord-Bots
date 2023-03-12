import discord
import nacl
from discord.ext import commands
from Interfaces.IGenericBot import IGenericBot
import asyncio
from Interfaces.BotFeature import BotFeature

##################################
# a feature for simulating a     #
# user to test results of        #
# actions of other features.     #
# for example, joins to chosen   #
# vc and plays a song to         # 
# simulate a user.               #
##################################
# WARNING: this feature is cant  #
# be used in a production bot,   #
# as it can be used to spam      #
# ALSO, this feature cant use    #
# any commands of other bots,    #
# as well as its own commands!   #
##################################


class actions_tester(BotFeature):
    def __init__(self, client : IGenericBot):
        super().__init__(client)
        self.voice_clients = {}
        @client.tree.command(name = 'join_vc', description='join a vc')
        @commands.has_permissions(administrator=True)
        async def join_a_vc(interaction: discord.Interaction, channel : discord.VoiceChannel):
            self.voice_clients[interaction.guild.id] = await channel.connect()
            await interaction.response.send_message('joined vc', ephemeral=True)
            self.voice_clients[interaction.guild.id].play(discord.FFmpegPCMAudio('data_base/actions_tester/songJoJo.mp3'), after=lambda e: print('done'))
        
        @client.tree.command(name = 'leave_vc', description='leave a vc')
        @commands.has_permissions(administrator=True)
        async def leave_a_vc(interaction: discord.Interaction):
            await self.voice_clients[interaction.guild.id].disconnect()
            await interaction.response.send_message('left vc', ephemeral=True)

        @client.tree.command(name = 'send', description='sends a message')
        @commands.has_permissions(administrator=True)
        async def send_a_message(interaction: discord.Interaction, message : str):
            await interaction.channel.send(message)
            await interaction.response.send_message('sent message', ephemeral=True)

        @client.tree.command(name = 'send_to', description='sends a message to a user')
        @commands.has_permissions(administrator=True)
        async def send_a_message_to_a_user(interaction: discord.Interaction, user : discord.User, message : str):
            try:
                await user.send(message)
                await interaction.response.send_message('sent message', ephemeral=True)
            except Exception as e:
                await interaction.response.send_message('failed to send message, ' + str(e), ephemeral=True)
                # print exception details
                

        @client.tree.command(name = 'send_to_by_id', description='sends a message to a user')
        @commands.has_permissions(administrator=True)
        async def send_a_message_to_a_user_by_id(interaction: discord.Interaction, user_id : str, message : str):
            try:
                user = await self.bot_client.fetch_user(int(user_id))
                await user.send(message)
                await interaction.response.send_message('sent message', ephemeral=True)
            except Exception as e:
                await interaction.response.send_message('failed to send message, ' + str(e), ephemeral=True)
        
        @client.tree.command(name = 'get_user_id', description='gets a user id')
        @commands.has_permissions(administrator=True)
        async def get_user_id(interaction: discord.Interaction, user : discord.User):
                await interaction.response.send_message(user.name + ': ' + str(user.id), ephemeral=True)
                await interaction.response.send_message('sent message', ephemeral=True)

        #TODO: move basic features to a separate feature