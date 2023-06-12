class demi_response:
    def __init__(self, message):
        self.message = message
        self.done = False
    async def send_message(self, content='', embed = None, embeds= None, ephemeral = False, view = None):
        await self.message.reply(content, embed = embed, embeds=embeds, view = view)
        self.done = True

    async def edit_message(self, content='', embed = None, embeds= None, view = None):
        await self.message.edit(content, embed = embed, embeds=embeds, view = view)
        self.done = True

    async def send_modal(self, modal):
        await self.message.reply('Modals (forms) are not supported on prefix commands, please use the slash command instead')
        self.done = True

    async def defer(self):
        self.done = True
    
    def is_done(self):
        return self.done