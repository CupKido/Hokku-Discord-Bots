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
    def __init__(self, bot : IGenericBot):
        super().__init__(bot)
        self.voice_clients = {}
        @bot.tree.command(name = 'join_vc', description='join a vc')
        @commands.has_permissions(administrator=True)
        async def join_a_vc(interaction: discord.Interaction, channel : discord.VoiceChannel):
            self.voice_clients[interaction.guild.id] = await channel.connect()
            await interaction.response.send_message('joined vc', ephemeral=True)
            self.voice_clients[interaction.guild.id].play(discord.FFmpegPCMAudio('data_base/actions_tester/songJoJo.mp3'), after=lambda e: print('done'))
        
        @bot.tree.command(name = 'leave_vc', description='leave a vc')
        @commands.has_permissions(administrator=True)
        async def leave_a_vc(interaction: discord.Interaction):
            await self.voice_clients[interaction.guild.id].disconnect()
            await interaction.response.send_message('left vc', ephemeral=True)

        @bot.tree.command(name = 'send', description='sends a message')
        @commands.has_permissions(administrator=True)
        async def send_a_message(interaction: discord.Interaction, message : str):
            await interaction.channel.send(message)
            await interaction.response.send_message('sent message', ephemeral=True)

        

        #TODO: move basic features to a separate feature