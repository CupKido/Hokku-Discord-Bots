from Interfaces.BotFeature import BotFeature
from discord_demi.demi_interaction import demi_interaction

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
        prefix_adapter.prefix = bot.command_prefix
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
        # make sure message starts with prefix, which means it is a command
        if message.content.startswith(prefix_adapter.prefix):
            command_name = message.content.split(' ')[0][len(prefix_adapter.prefix):]
            
            if command_name in self.commands.keys():
                interaction = demi_interaction(message)
                # make sure command is allowed to run
                if await self.commands[command_name][1](interaction):
                    coro = self.commands[command_name][0]
                    params = {}
                    try:
                        # make sure command is not blocked
                        # call relevant callbacks
                        call_coro : bool = True
                        for callback in self.bot_client.on_before_any_command_callbacks:
                            value : bool = await callback(coro.__name__, interaction, **params)
                            if value is not None and type(value) is bool:
                                if not value:
                                    call_coro : bool = False
                        if call_coro:
                            await self.commands[command_name][0](interaction)
                            for callback in self.bot_client.on_after_any_command_callbacks:
                                await callback(coro.__name__, interaction, **params)
                        return
                    except Exception as e:
                        self._log(str(e))
                        if message.channel is not None:
                            await message.channel.send('Command failed')
                else:
                    await self.bot_client.error_handler(interaction=interaction)  



