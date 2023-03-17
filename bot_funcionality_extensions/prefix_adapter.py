from Interfaces.BotFeature import BotFeature


#########################################
# This class is a temporary solution to #
# allow the bot to use the old prefix   #
# commands.                             #
# NOTE: this feature only supports      # 
# commands with no parameters!          #
#########################################

class prefix_adapter(BotFeature):
    
    def __init__(self, bot):
        super().__init__(bot)
        bot.add_on_ready_callback(self.on_ready)
        self.commands = {}

    async def on_ready(self):
        
        self.bot_client.add_on_message_callback(self.on_message)
        for x in self.bot_client.tree.get_commands():
            if len(x.parameters) != 0: continue
            print(x.qualified_name)
            self.commands[x.qualified_name] = x._callback

        print('Prefix translator is ready')
    
    async def on_message(self, message):
        if message.author == self.bot_client.user:
            return

        if message.content.startswith('!'):
            command_name = message.content.split(' ')[0][1:]
            
            if command_name in self.commands.keys():
                try:
                    # await message.reply('Command found, yet not supported, please use the slash comma instead')
                    await self.commands[command_name](interaction_temp(message))
                    return
                except Exception as e:
                    print(e)
                    await message.channel.send('Command failed')
            else:
                await message.channel.send('Command not found')

class interaction_temp:
    def __init__(self, message):
        self.response = response_temp(message)
        self.message = message
        self.user = message.author
        self.channel = message.channel
        self.guild = message.guild

class response_temp:
    def __init__(self, message):
        self.message = message

    async def send_message(self, content='', embed = None, embeds= None, ephemeral = False, view = None):
        await self.message.channel.send(content, embed = embed, embeds=embeds, view = view)

    async def edit_message(self, content='', embed = None, embeds= None, view = None):
        await self.message.edit(content, embed = embed, embeds=embeds, view = view)

    async def send_modal(self, modal):
        await self.message.reply('Modals are not supported, please use the slash command instead')

    async def defer(self):
        pass