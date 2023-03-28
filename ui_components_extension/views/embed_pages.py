import discord
import math
class embed_pages(discord.ui.View):
    def __init__(self, embeds, timeout=None, embed_title=None, title='', items_per_page=10):
        super().__init__(timeout=timeout)
        if items_per_page is None:
            max_items = 10
        else:
            max_items = 9
        if items_per_page > max_items:
            self.items_per_page = max_items
        else:
            self.items_per_page = items_per_page

        self.embed_title = embed_title
        self.title = title
        self.embeds = embeds
        self.current_page = 0
        self.message = None
        self.last_page = float(len(self.embeds)) / float(self.items_per_page) - 1
        self.last_page = int(math.ceil(self.last_page))
        
    
    async def send(self, interaction, ephemeral=False):
        if self.message is None:
            self.message = await interaction.response.send_message(content=self.title, 
                                                                   embeds=self.get_current_page_embeds(), 
                                                                   view=self, 
                                                                   ephemeral=ephemeral)

    def get_current_page_embeds(self):
        res = []
        if self.embed_title is not None:
            res.append(self.embed_title)
        for i in range(self.current_page * self.items_per_page, (self.current_page + 1) * self.items_per_page):
            if i >= len(self.embeds):
                break
            res.append(self.embeds[i])
        return res

    @discord.ui.button(label='Previous' ,custom_id='previous')
    async def previous(self, interaction, button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embeds=self.get_current_page_embeds())
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label='Next' ,custom_id='next')
    async def next(self, interaction, button):
        if self.current_page < self.last_page:
            self.current_page += 1
            await interaction.response.edit_message(embeds=self.get_current_page_embeds())
        else:
            await interaction.response.defer()
    