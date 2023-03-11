class prefix_translator():
    
    def __init__(self, bot):
        self.bot = bot
        bot.add_on_ready_callback(self.on_ready)
        self.commands = {}

    async def on_ready(self):
        
        self.bot.add_on_message_callback(self.on_message)
        for x in self.bot.tree.get_commands():
            if len(x.parameters) != 0: continue
            print(x)
            self.commands[x.qualified_name] = x._callback

        print('Prefix translator is ready')
    
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.startswith('!'):
            command_name = message.content.split(' ')[0][1:]
            
            if command_name in self.commands.keys():
                try:
                    await self.commands[command_name]({'interaction': {'response': {'send' : message.channel.send}}})
                    return
                except Exception as e:
                    print(e)
                    await message.channel.send('Command failed')
                await message.channel.send('Command not found')
