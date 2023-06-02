import discord
import math
class embed_pages(discord.ui.View):
    def __init__(self, embeds, timeout=None, embed_title=None, title='', items_per_page=10, add_numbering=False, get_thumb=None):
        super().__init__(timeout=timeout)
        if embed_title is None:
            max_items = 10
        else:
            max_items = 9
        if items_per_page > max_items:
            self.items_per_page = max_items
        else:
            self.items_per_page = items_per_page

        self.embed_title = embed_title
        self.original_title = title
        self.embeds = embeds
        self.current_page = 0
        self.message = None
        self.last_page = float(len(self.embeds)) / float(self.items_per_page) - 1
        self.last_page = int(math.ceil(self.last_page))
        self.add_numbering = add_numbering
        self.get_thumb = get_thumb
        self.loaded_thumbs = []
        if add_numbering:
            for i in range(len(self.embeds)):
                this_embed = self.embeds[i]
                this_embed.set_footer(text=((this_embed.footer.text + ' | ') if this_embed.footer is not None and this_embed.footer.text is not None else '') + str(i+1) + '/' + str(len(self.embeds)))
        
    
    async def send(self, interaction, ephemeral=False, followup=False, views=[]):
        if self.message is None:
            if self.embed_title is not None:
                title = self.original_title
            else:
                title = str(self.current_page+1) + '/' + str(self.last_page + 1) + '\n' + self.original_title
            for view in views:
                for item in view.children:
                    self.add_item(item)
            if followup:
                self.message = await interaction.followup.send(content=title, 
                                                                embeds=self.get_current_page_embeds(), 
                                                                view=self, 
                                                                ephemeral=ephemeral)
            else:
                self.message = await interaction.response.send_message(content=title, 
                                                                        embeds=self.get_current_page_embeds(), 
                                                                        view=self, 
                                                                        ephemeral=ephemeral)

    def get_current_page_embeds(self):
        res = []
        if self.embed_title is not None:
            self.embed_title.set_author(name=str(self.current_page+1) + '/' + str(self.last_page + 1))
            res.append(self.embed_title)

        for i in range(self.current_page * self.items_per_page, (self.current_page + 1) * self.items_per_page):
            if i >= len(self.embeds):
                break
            if self.get_thumb is not None:
                if i not in self.loaded_thumbs:
                    self.embeds[i].set_thumbnail(url=self.get_thumb(self.embeds[i]))
                    self.loaded_thumbs.append(i)
            res.append(self.embeds[i])
        return res

    @discord.ui.button(label='Previous' ,custom_id='previous')
    async def previous(self, interaction, button):
        if self.current_page > 0:
            self.current_page -= 1
            if self.embed_title is not None:
                await interaction.response.edit_message(embeds=self.get_current_page_embeds())
            else:
                title = str(self.current_page+1) + '/' + str(self.last_page + 1) + '\n' + self.original_title
                await interaction.response.edit_message(content=title, embeds=self.get_current_page_embeds())
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label='Next' ,custom_id='next')
    async def next(self, interaction, button):
        if self.current_page < self.last_page:
            self.current_page += 1
            if self.embed_title is not None:
                await interaction.response.edit_message(embeds=self.get_current_page_embeds())
            else:
                title = str(self.current_page+1) + '/' + str(self.last_page + 1) + '\n' + self.original_title
                await interaction.response.edit_message(content=title, embeds=self.get_current_page_embeds())
        else:
            await interaction.response.defer()
    