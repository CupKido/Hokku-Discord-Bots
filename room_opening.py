import discord
import discord
from discord import app_commands
from discord.ext import commands
import views
import modals
import asyncio
import threading
import tasks
from server_config_interface import server_config
import channel_modifier

bot_client = ''

active_channels = {}

def AddFuncs(client):
    global bot_client
    bot_client = client
    bot_client.add_on_ready_callback(on_ready_callback)
    # client.tree.add_command(name = 'choose_creation_channel', description='choose a channel for creationg new voice channels', callback = choose_creation_channel)
    # client.tree.add_command(name = 'choose_static_message', description='choose a static message for vc creation channel', callback = choose_static_message)
    @client.tree.command(name = 'choose_creation_channel', description='choose a channel for creationg new voice channels')
    async def choose_creation_channel(interaction: discord.Interaction, channel : discord.TextChannel):
        try:
            # get server config
            this_server_config = server_config(interaction.guild.id)
            if this_server_config.get_creation_vc_channel() != ' ':
                await channel_modifier.remove_readonly(client.get_channel(int(this_server_config.get_creation_vc_channel())))
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

            #check if channel exists
            try:
                channnel = interaction.guild.fetch_channel(this_server_config.get_creation_vc_channel())
            except:
                this_server_config.set_creation_vc_channel(' ')

            # check if channel is set, and if not, exits
            if this_server_config.get_creation_vc_channel() == ' ':
                await interaction.response.send_message('please set a creation channel first')
                return
            this_server_config.set_static_message(message)

            # set message
            await interaction.response.send_message(f'\"{message}\" was set as static message')

            # get creation channel
            creation_channel = client.get_channel(int(this_server_config.get_creation_vc_channel()))

            embed = discord.Embed(title = 'Instant vc creation', description = message)
            
            message = await creation_channel.send(embed = embed, view = views.InsantButtonView(create_new_channel))
            this_server_config.set_static_message_id(message.id)


        except Exception as e:
            print(str(e))
            await interaction.response.send_message('error')

    @client.event
    async def on_voice_state_update(member, before, after):
        # check if before channel is empty
        if before.channel is not None and len(before.channel.members) == 0:
            # check if channel is active
            if before.channel.id in active_channels[before.channel.guild.id]:
                # delete channel
                active_channels[before.channel.guild.id].remove(before.channel.id)
                print(f'deleted {before.channel.name} channel because it was empty')
                await before.channel.delete()

async def on_ready_callback():
    # get all guilds
    for guild in bot_client.guilds:
        # get all channels
        this_server_config = server_config(guild.id)
        creation_channel = this_server_config.get_creation_vc_channel()
        static_message = this_server_config.get_static_message()
        static_message_id = this_server_config.get_static_message_id()
        if  creation_channel != ' ' and static_message != ' ' and static_message_id != ' ':
            creation_channel = bot_client.get_channel(int(this_server_config.get_creation_vc_channel()))
            if creation_channel is not None:
                async for msg in creation_channel.history(limit=50):
                    if msg.id == static_message_id:
                        await msg.edit(content = msg.content, view = views.InsantButtonView(create_new_channel))


            

async def create_new_channel(interaction):
    print('presenting modal')
    thisModal = modals.InstantModal(title="Modal via Button")
    thisModal.set_callback_func(button_pressed)
    await interaction.response.send_modal(thisModal)

async def button_pressed(interaction):
    # get vc creation channel
    this_server_config = server_config(interaction.guild.id)
    creation_channel = bot_client.get_channel(int(this_server_config.get_creation_vc_channel()))

    # get category
    category = creation_channel.category

    name = interaction.data['components'][0]['components'][0]['value']
    if name == '':
        name = f'{interaction.user.name}\'s office'
    # get chosen values from modal
    users_amount = interaction.data['components'][1]['components'][0]['value']
    if users_amount == '':
        users_amount = None
    else:
        users_amount = int(users_amount)

    # get bitrate
    bitrate = interaction.data['components'][2]['components'][0]['value']
    if bitrate == '':
        bitrate = None
    else:
        # transform to kb
        bitrate = int(bitrate) * 1000


    # create vc in category
    new_channel = await category.create_voice_channel(name = name, user_limit = users_amount, bitrate = bitrate)
    #new_channel.permissions_synced = True

    # add vc to active channels list
    if not interaction.guild.id in active_channels.keys(): 
        active_channels[interaction.guild.id] = []
    active_channels[interaction.guild.id].append(new_channel.id)

    if not users_amount is None:
        await interaction.response.send_message(f'created a vc for {users_amount} users')
    else:
        await interaction.response.send_message(f'created a vc for unlimited users')
    message = interaction.channel.last_message
    await asyncio.sleep(5)
    await message.delete()
    # start timer
    await asyncio.sleep(25)
    if new_channel.id in active_channels[new_channel.guild.id]:
        if len(new_channel.members) == 0:
            # delete channel
            active_channels[new_channel.guild.id].remove(new_channel.id)
            print(f'deleted {new_channel.name} channel after 30 seconds due to inactivity')
            try:
                await new_channel.delete()
            except:
                print('could not delete channel')
                pass

    # respond to interaction


