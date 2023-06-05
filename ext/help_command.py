import discord
from Interfaces.BotFeature import BotFeature
from ui_components_extension.views.embed_pages import embed_pages
class help_command(BotFeature):
    def __init__(self, bot):
        super().__init__(bot)
        
        @self.bot_client.tree.command(name='help', description='Get info about available commands')
        async def help_command(interaction):
            await self.on_help_command(interaction)

    async def on_help_command(self, interaction):
            embed_title = discord.Embed(title='Help', 
                                        description='\n**Bot\'s prefix is: \'' + 
                                        self.bot_client.command_prefix + '\'**' + 
                                        '\nAvailable commands for ' + interaction.user.mention)
            owner = self.bot_client.get_user(self.bot_client.owner_id)
            if owner is None:
                owner = self.bot_client.get_user(427464593351114754)
            if owner is not None:
                embed_title.set_footer(icon_url=owner.avatar.url, text='Bot created by ' + 
                                       owner.name + '#' + owner.discriminator)
            else:
                embed_title.set_footer(icon_url=self.bot_client.user.avatar.url)
            embeds = []
            for x in self.bot_client.tree.get_commands():
                if await x._check_can_run(interaction):
                    embed = discord.Embed(title='/' + x.qualified_name, description=x.description, color=0x22ffaa)
                    embed.set_footer(text='__________________________________________________________________')
                    embeds.append(embed)
            pages = embed_pages(embeds=embeds, embed_title=embed_title, items_per_page=5)
            await pages.send(interaction, ephemeral=True)
