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
from ui_ext.generic_ui_comps import Generic_View
from ui_ext.games.minesweeper import minesweeper
from ui_ext.buttons.role_button import role_button
from ui_ext.buttons.on_off_button import on_off_button
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
        # bot.add_on_before_any_command_callback(self.on_before_any_command_callback)
        # bot.add_on_after_any_event_callback(self.on_after_any_event_callback)
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
        @bot.tree.command(name = 'test_buttons_amount', description='test buttons')
        @app_commands.check(permission_checks.is_admin)
        async def test5(interaction: discord.Interaction):
            await interaction.response.send_message('you asked for it...', ephemeral=True)
            my_view = Generic_View()
            i = 24
            for x in range(i):
                my_view.add_generic_button(label='🚩', style=discord.ButtonStyle.primary, callback=(lambda x, y, z: x.response.send_message('test', ephemeral=True)))
            while i < 1000:
                try:
                    my_view.add_generic_button(label='', emoji='🚩', style=discord.ButtonStyle.primary, callback=(lambda x, y, z: x.response.send_message('test', ephemeral=True)))
                    await interaction.followup.send('test', ephemeral=True, view=my_view)
                    i += 1
                    await asyncio.sleep(0.3)
                except Exception as e:
                    print(i, e)
                    break
        @bot.tree.command(name = 'minesweeper', description='test buttons')
        @app_commands.check(permission_checks.is_admin)
        async def test5(interaction: discord.Interaction):
            await interaction.response.send_message('', view=minesweeper())

        @bot.tree.command(name = 'minesweeper_eph', description='test buttons')
        @app_commands.check(permission_checks.is_admin)
        async def test5(interaction: discord.Interaction):
            await interaction.response.send_message('', view=minesweeper())

        @bot.tree.command(name = 'add_role_button', description='add role button')
        @app_commands.check(permission_checks.is_admin)
        async def test6(interaction: discord.Interaction, role : discord.Role, label: str = None, emoji : str = None):
            await interaction.response.send_message('adding button', ephemeral=True)
            my_view = Generic_View()
            if label is None:
                label = role.name
            my_view.add_item(role_button(label=label, role_id=role.id, style=discord.ButtonStyle.primary, bot=self.bot_client, emoji=emoji))
            await interaction.followup.send('test', view=my_view)

        @bot.tree.command(name = 'add_on_off_button', description='add on off button')
        @app_commands.check(permission_checks.is_admin)
        async def test7(interaction: discord.Interaction, label: str = None, emoji : str = None):
            await interaction.response.send_message('adding button', ephemeral=True)
            my_view = Generic_View()
            if label is None:
                label = 'test'
            my_view.add_item(on_off_button(label=label, style=discord.ButtonStyle.primary, emoji=emoji, callback=self.on_off_callback))
            await interaction.followup.send('test', view=my_view)

    async def on_after_any_event_callback(self, name, *args, **kwargs):
        print(name, args, kwargs)

    async def on_off_callback(self, interaction, value : bool) -> bool:
        await interaction.response.send_message(f'existing value: {value}', ephemeral=True)
        return not value

    async def on_before_any_command_callback(self, name, *args, **kwargs):
        print(name, args, kwargs)