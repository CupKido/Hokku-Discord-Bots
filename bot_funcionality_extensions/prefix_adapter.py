from Interfaces.BotFeature import BotFeature


#########################################
# This class is a temporary solution to #
# allow the bot to use the old prefix   #
# commands.                             #
# NOTE: this feature only supports      # 
# commands with no parameters!          #
#########################################

class prefix_adapter(BotFeature):
    prefix = '!'
    def __init__(self, bot):
        super().__init__(bot)
        bot.add_on_ready_callback(self.on_ready)
        self.commands = {}

    async def on_ready(self):
           
        self.bot_client.add_on_message_callback(self.on_message)
        for x in self.bot_client.tree.get_commands():
            if len(x.parameters) != 0: continue
            print(x.qualified_name)

            self.commands[x.qualified_name] = (x._callback, x._check_can_run)

        print('Prefix translator is ready')
    
    


    async def on_message(self, message):
        if message.author == self.bot_client.user:
            return
        if len(message.content) < 2:
            return
        if message.content.startswith(prefix_adapter.prefix):
            command_name = message.content.split(' ')[0][len(prefix_adapter.prefix):]
            
            if command_name in self.commands.keys():
                interaction = interaction_temp(message)
                if await self.commands[command_name][1](interaction):
                    try:
                        # await message.reply('Command found, yet not supported, please use the slash comma instead')
                        await self.commands[command_name][0](interaction)
                        return
                    except Exception as e:
                        print(e)
                        await message.channel.send('Command failed')
                        return
                else:
                    await self.bot_client.error_handler(interaction)
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
        await self.message.reply(content, embed = embed, embeds=embeds, view = view)

    async def edit_message(self, content='', embed = None, embeds= None, view = None):
        await self.message.edit(content, embed = embed, embeds=embeds, view = view)

    async def send_modal(self, modal):
        await self.message.reply('Modals (forms) are not supported on prefix commands, please use the slash command instead')

    async def defer(self):
        pass