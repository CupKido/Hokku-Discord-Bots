from Interfaces.IGenericBot import IGenericBot
from GenericBot import GenericBot_client
import discord
from DB_instances.generic_config_interface import server_config
from discord.ext import commands
from ui_components_extension.generic_ui_comps import Generic_View, Generic_Modal
import ui_components_extension.ui_tools as ui_tools
# a feature with 'confess' command
class confessions:
    CONFESSIONS_CHANNEL = 'confessions_channel'
    REPORT_COUNT = 'report_count'
    def __init__(self, bot):
        self.bot_client = bot

        @bot.tree.command(name = 'set_confess_channel', description='set a channel for confessions')
        @commands.has_permissions(administrator=True)
        async def set_confess_channel(interaction: discord.Interaction, channel : discord.TextChannel,
                                       report_count : int = 3):
            this_server_config = server_config(interaction.guild.id)
            this_server_config.set_params(confessions_channel=channel.id)
            if report_count < 1:
                report_count = 1
            this_server_config.set_params(report_count=report_count)
            await interaction.response.send_message('set confessions channel, ' + \
                                                    'report count until message delete: ' + str(report_count),
                                                    ephemeral=True)

        @bot.tree.command(name = 'confess', description='confess your thoughts')
        async def confess(interaction: discord.Interaction, message : str):
            this_server_config = server_config(interaction.guild.id)
            channel_id = this_server_config.get_param(confessions.CONFESSIONS_CHANNEL)
            if channel_id == None:
                await interaction.response.send_message('confessions channel is not set', ephemeral=True)
                return
            channel = self.bot_client.get_channel(channel_id)
            if channel is None:
                await interaction.response.send_message('confessions channel is not set', ephemeral=True)
                return
            embed = discord.Embed(title='Anonymous Confession', description=message, color=0x00ff00)
           
            
            message = await channel.send(embed=embed)
            await self.add_options_buttons(message)
            await interaction.response.send_message('sent confession', ephemeral=True)
    
    async def reply(self, interaction, button, view):
        message_id = button.value['message']
        this_modal = Generic_Modal(title='Reply to confession')
        this_modal.add_input(label = 'Enter reply:', placeholder='your reply')
        this_modal.add_input(label = 'Message ID:', placeholder='Message ID', default=str(message_id))
        this_modal.set_value(message_id)
        this_modal.set_callback(self.send_reply)
        await interaction.response.send_modal(this_modal)

    async def send_reply(self, interaction):
        reply = ui_tools.get_modal_value(interaction, 0)
        message_id = ui_tools.get_modal_value(interaction, 1)
        message = await self.bot_client.get_message(message_id, interaction.channel, 50)
        if message is None:
            await interaction.response.send_message('failed to find message', ephemeral=True)
            return
        message = await message.reply(reply)
        await self.add_options_buttons(message)
        await interaction.response.defer(ephemeral=True)
    
    async def add_options_buttons(self, message):
        my_view = Generic_View()
        my_view.add_generic_button(label=' Reply',
                                    style= ui_tools.string_to_color('green'),
                                    callback = self.reply,
                                    emoji='🙋🏻‍♂️', value={'message': message.id})
        my_view.add_generic_button(label=' Report',
                                    style= ui_tools.string_to_color('red'),
                                    callback = self.report,
                                    emoji='🚨', value={'message': message.id, 'count':0})
        await message.edit(view=my_view)

    async def report(self, interaction, button, view):
        message_id = button.value['message']
        count = int(button.value['count'])
        count += 1
        button.value['count'] = count 
        this_server_config = server_config(interaction.guild.id)
        if count == int(this_server_config.get_param(confessions.REPORT_COUNT)):
            message = await self.bot_client.get_message(message_id, interaction.channel, 50)
            if message is None:
                await interaction.response.defer(ephemeral=True)
                return
            await message.delete()
        await interaction.response.send_message('reported message', ephemeral=True)
    
