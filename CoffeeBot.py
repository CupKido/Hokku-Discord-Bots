import discord
from discord import app_commands
from server_config_interface import server_config
secret_key = ''
with open('token.txt', 'r') as f:
    secret_key = f.read().split("\n")[2]


class CoffeeBot_client(discord.Client):
    def __init__(self, alert_when_online : bool = False):
        super().__init__(intents = discord.Intents.all())
        self.tree = app_commands.CommandTree(self)
        self.synced = False
        self.added = False
        self.alert_when_online = alert_when_online
        self.on_ready_callbacks = []

    async def on_ready(self):
        await self.wait_until_ready()
        # sent message to channel with id 123456789
        if not self.synced:
            print('=================================\nsyncing commands tree to discord')
            await self.tree.sync()
            self.synced = True
            print('synced \
            \n=================================')
        print('im active on: ')
        for guild in self.guilds:
            if self.alert_when_online:
                guildID = guild.id
                channel = self.get_channel(int(server_config.get_specific_announcement_channel(guildID)))
                await channel.send(f'im active, my name is {self.user}')
            print('\t' + str(guild.name))
        for callback in self.on_ready_callbacks:
            await callback()


    def add_on_ready_callback(self, callback):
        self.on_ready_callbacks.append(callback)
    
    def activate(self): #
        self.run(secret_key)
