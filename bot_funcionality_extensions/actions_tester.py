import discord
import nacl
from discord.ext import commands
from discord import app_commands
import permission_checks
from Interfaces.IGenericBot import IGenericBot
import asyncio
from Interfaces.BotFeature import BotFeature
import requests
from io import BytesIO

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
        @app_commands.check(permission_checks.is_admin)
        async def join_a_vc(interaction: discord.Interaction, channel : discord.VoiceChannel):
            await interaction.response.send_message('joining vc...', ephemeral=True)
            self.voice_clients[interaction.guild.id] = await channel.connect()
            self.voice_clients[interaction.guild.id].play(discord.FFmpegPCMAudio('data_base/actions_tester/songJoJo.mp3'), after=lambda e: print('done'))
        
        @bot.tree.command(name = 'leave_vc', description='leave a vc')
        @app_commands.check(permission_checks.is_admin)
        async def leave_a_vc(interaction: discord.Interaction):
            await interaction.response.send_message('leaving vc...', ephemeral=True)
            await self.voice_clients[interaction.guild.id].disconnect()

        @bot.tree.command(name = 'send', description='sends a message')
        @app_commands.check(permission_checks.is_admin)
        async def send_a_message(interaction: discord.Interaction, message : str):
            await interaction.channel.send(message)
            await interaction.response.send_message('sent message', ephemeral=True)

        @bot.tree.command(name = 'test', description='test')
        @app_commands.check(permission_checks.is_admin)
        async def test(interaction: discord.Interaction):
            embed1= discord.Embed(title="test1", description="test", color=0x00ff00)
            embed2= discord.Embed(title="test2", description="test", color=0x00ff00)
            embed3= discord.Embed(title="test3", description="test", color=0x00ff00, timestamp=discord.utils.utcnow())
            embeds = [embed1, embed2, embed3]
            await interaction.response.send_message('test', embeds=embeds, ephemeral=True)

        @bot.tree.command(name = 'copy_profile', description='test2')
        @app_commands.check(permission_checks.is_admin)
        async def test2(interaction: discord.Interaction, user : discord.Member):
            p_pfp = await self.bot_client.user.display_avatar.read()    
            n_pfp = await user.display_avatar.read()
            await self.bot_client.user.edit(avatar=n_pfp, username=user.display_name) 
            await interaction.response.send_message('copied pfp, saving previous', ephemeral=True)
            with open('data_base/actions_tester/previous_pfp.png', 'wb+') as f:
                f.write(p_pfp)

        @bot.tree.command(name = 'get_pfp', description='test3')
        @app_commands.check(permission_checks.is_admin)
        async def test3(interaction: discord.Interaction, user : discord.User):
            await interaction.response.send_message('getting pfp', ephemeral=True)
            pfp = await user.display_avatar.read()
            with open('data_base/actions_tester/pfp.png', 'wb+') as f:
                f.write(pfp)
            # send pfp as file
            message = await interaction.user.send('got pfp, deleting in 30 seconds', files=[discord.File('data_base/actions_tester/pfp.png')])
            await asyncio.sleep(30)
            await message.delete()
            
        
        @bot.tree.command(name = 'delete_last_message', description='test4')
        async def test4(interaction: discord.Interaction):
            await interaction.response.send_message('deleting last message', ephemeral=True)
            async for message in interaction.channel.history(limit=2):
                if message.author == self.bot_client.user:
                    await message.delete()
                    break

        @bot.tree.command(name = 'test2', description='test5')
        @app_commands.check(permission_checks.is_admin)
        async def test5(interaction: discord.Interaction, user : discord.User):
            await interaction.response.send_message('test', ephemeral=True)
            pfp = await interaction.user.display_avatar.read()

            url = "https://discord.com/api/v10/users/" + str(self.bot_client.user.id)
            
            headers = {
                "Authorization": "Bot " + self.bot_client.get_secret(),
                "Content-Type": "application/json"
            }
            
            payload = {
                "avatar": BytesIO(pfp)
            }
            # get reply from discord
            response = requests.patch(url, headers=headers, files=payload)
            print(response.text)
            print(response.status_code)
            print(response)