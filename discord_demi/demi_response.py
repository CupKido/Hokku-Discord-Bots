class demi_response:
    def __init__(self, message):
        self.message = message

    async def send_message(self, content='', embed = None, embeds= None, ephemeral = False, view = None):
        await self.message.reply(content, embed = embed, embeds=embeds, view = view)

    async def edit_message(self, content='', embed = None, embeds= None, view = None):
        await self.message.edit(content, embed = embed, embeds=embeds, view = view)

    async def send_modal(self, modal):
        await self.message.reply('Modals (forms) are not supported on prefix commands, please use the slash command instead')

    async def defer(self):
        pass