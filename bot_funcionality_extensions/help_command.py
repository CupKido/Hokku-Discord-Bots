import discord
from Interfaces.BotFeature import BotFeature

class help_command(BotFeature):
    def __init__(self, bot):
        super().__init__(bot)
        
        bot.add_on_ready_callback(self.on_help_command)

    async def on_help_command(self):

        @self.bot_client.tree.command(name='help', description='Get info about available commands')
        async def help_command(interaction):
            message = 'Available commands:\n'
            for x in self.bot_client.tree.get_commands():
                if await x._check_can_run(interaction.user):
                    message += '\nCommand: /' + x.qualified_name + '\nDescription: ' + x.description + '\n'
            await interaction.response.send_message(message, ephemeral=True)
