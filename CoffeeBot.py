import discord
from discord import app_commands
from discord.ext import commands
import views
import modals
from server_config_interface import server_config
import channel_modifier
import random
secret_key = ''
with open('token.txt', 'r') as f:
    secret_key = f.read().split("\n")[2]


class discord_client(discord.Client):
    def __init__(self, alert_when_online : bool = False):
        super().__init__(intents = discord.Intents.all())
        self.tree = app_commands.CommandTree(self)
        self.synced = False
        self.added = False
        self.alert_when_online = alert_when_online

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

client = discord_client()

@client.tree.command(name = 'choose_creation_channel', description='choose a channel for creationg new voice channels')
async def choose_creation_channel(interaction: discord.Interaction, channel : discord.TextChannel):
    try:
        # get server config
        this_server_config = server_config(interaction.guild.id)
        if this_server_config.get_creation_vc_channel() != ' ':
            await channel_modifier.set_writable(client.get_channel(int(this_server_config.get_creation_vc_channel())))
        # set announcement channel
        this_server_config.set_creation_vc_channel(channel.id)
        await channel_modifier.set_readonly(channel)
        await interaction.response.send_message(f'\"{channel.name}\" was set as vc creation channel')

    except Exception as e:
        print(str(e))
        await interaction.response.send_message('error')


@client.tree.command(name = 'choose_static_message', description='choose a static message for vc creation channel')
async def choose_static_message(interaction: discord.Interaction, message : str):
    try:
        # get server config
        this_server_config = server_config(interaction.guild.id)

        if this_server_config.get_creation_vc_channel() == ' ':
            await interaction.response.send_message('please set a creation channel first')
            return

        # set message
        await interaction.response.send_message(f'\"{message}\" was set as static message')

        # get creation channel
        creation_channel = client.get_channel(int(this_server_config.get_creation_vc_channel()))

        # embed = discord.Embed(title = 'Instant vc creation', description = message)

        await creation_channel.send(content = message, view = views.InsantButtonView(create_new_channel))

        # add view to embed
        # view = views.MyView()

        
        # add buttons to embed
        # buttons = []
        # for i in range(1, 11):
        #     buttons.append(app_commands.ActionRow(app_commands.Button(label = str(i), custom_id = str(i))))
        # await creation_channel.send('choose a number of users to create a vc for', components = buttons)


    except Exception as e:
        print(str(e))
        await interaction.response.send_message('error')


async def create_new_channel(interaction):
    print('presenting modal')
    thisModal = modals.InstantModal(title="Modal via Button")
    thisModal.set_callback_func(button_pressed)
    await interaction.response.send_modal(thisModal)

async def button_pressed(interaction):
    print('button pressed')

def activate():
    client.run(secret_key)