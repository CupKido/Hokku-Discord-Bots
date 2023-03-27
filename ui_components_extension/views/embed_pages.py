import discord

class embed_pages(discord.ui.View):
    def __init__(self, embeds, timeout=None, embed_title=None, title='', items_per_page=10):
        super().__init__(timeout=timeout)
        if embed_pages is None:
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
        self.add_item(discord.ui.Button(label='Previous', custom_id='previous'))
        self.add_item(discord.ui.Button(label='Next', custom_id='next'))
    
    async def send(self, interaction):
        if self.message is None:
            interaction.response.send_message(content=self.title, embeds=await self.get_current_page_embeds(), view=self)

    async def get_current_page_embeds(self):
        res = []
        if self.embed_title is not None:
            res += self.embed_title
        for i in range(self.current_page * self.items_per_page, (self.current_page + 1) * self.items_per_page):
            if i >= len(self.embeds):
                break
            res += self.embeds[i]
        return res

    @discord.ui.button(custom_id='previous')
    async def previous(self, button, interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.message.edit(embeds=await self.get_current_page_embeds())
    
    @discord.ui.button(custom_id='next')
    async def next(self, button, interaction):
        if self.current_page < len(self.embeds) // self.items_per_page:
            self.current_page += 1
            await self.message.edit(embeds=await self.get_current_page_embeds())
    