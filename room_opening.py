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
            await interaction.response.send_message(f'\"{channel.name}\" was set as vc creation channel', ephemeral = True)

        except Exception as e:
            print(str(e))
            await interaction.response.send_message('error', ephemeral = True)

    @client.tree.command(name = 'set_closing_timer', description='set a timer for closing a vc after creation in case no one joins')
    async def set_closing_timer(interaction: discord.Interaction, timer : int):
        try:
            # get server config
            this_server_config = server_config(interaction.guild.id)

            # set timer
            this_server_config.set_vc_closing_timer(timer)
            await interaction.response.send_message(f'\"{timer}\" was set as closing timer', ephemeral = True)

        except Exception as e:
            print(str(e))
            await interaction.response.send_message('error', ephemeral = True) 

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
                await interaction.response.send_message('please set a creation channel first', ephemeral = True)
                return
            this_server_config.set_static_message(message)

            # set message
            await interaction.response.send_message(f'\"{message}\" was set as static message', ephemeral = True)

            # get creation channel
            creation_channel = client.get_channel(int(this_server_config.get_creation_vc_channel()))

            embed = discord.Embed(title = 'Instant vc creation', description = message)
            
            message = await creation_channel.send(embed = embed, view = views.InsantButtonView(create_new_channel_button))
            this_server_config.set_static_message_id(message.id)


        except Exception as e:
            print(str(e))
            await interaction.response.send_message('error', ephemeral = True)

    @client.event
    async def on_voice_state_update(member, before, after):
        # check if before channel is empty
        if before.channel is not None and len(before.channel.members) == 0:
            # check if channel is active
            if before.channel.guild.id in active_channels.keys() and before.channel.id in active_channels[before.channel.guild.id].keys():
                # delete channel
                active_channels[before.channel.guild.id].pop(before.channel.id)
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
                        await msg.edit(content = msg.content, view = views.InsantButtonView(create_new_channel_button))


            

async def create_new_channel_button(interaction):
    print('presenting modal')
    flag = True
    # if rooms are open for this guild
    if interaction.guild.id in active_channels.keys():
        # check if user has active channel
        if interaction.user.id in active_channels[interaction.guild.id].keys():
            # edit channel
            channel = bot_client.get_channel(active_channels[interaction.guild.id][interaction.user.id])
            thisModal = modals.InstantModal(title="Edit channel")
            thisModal.set_callback_func(change_channel_details)
            thisModal.set_fields(channel.name, channel.user_limit, channel.bitrate)
            # thisModal.set_pre_fileds(channel.name, channel.user_limit, channel.bitrate)
            flag = False
    if flag:
        category = interaction.channel.category
        thisModal = modals.InstantModal(title="Create new channel")
        thisModal.set_callback_func(create_new_channel)
        thisModal.set_fields()
    await interaction.response.send_modal(thisModal)

async def change_channel_details(interaction):

    # get chosen values from modal
    # get name
    name = get_modal_value(interaction, 0)
    if name == '':
        name = f'{interaction.user.name}\'s office'

    # get users limit
    users_amount = get_modal_value(interaction, 1)
    if users_amount == '':
        users_amount = None
    else:
        users_amount = int(users_amount)

    # get bitrate
    bitrate = get_modal_value(interaction, 2)
    if bitrate == '':
        bitrate = None
    else:
        # transform to kb
        bitrate = int(bitrate) * 1000

    channel = bot_client.get_channel(active_channels[interaction.guild.id][interaction.user.id])
    await channel.edit(name = name, user_limit = users_amount, bitrate = bitrate)
    await interaction.response.send_message(f'\"{channel.name}\" was edited', ephemeral = True)
    return 

async def create_new_channel(interaction):
    
    # get chosen values from modal
    # get name
    name = get_modal_value(interaction, 0)
    if name == '':
        name = f'{interaction.user.name}\'s office'

    # get users limit
    users_amount = get_modal_value(interaction, 1)
    if users_amount == '':
        users_amount = None
    else:
        users_amount = int(users_amount)

    # get bitrate
    bitrate = get_modal_value(interaction, 2)
    if bitrate == '':
        bitrate = None
    else:
        # transform to kb
        bitrate = int(bitrate) * 1000

    


    # get vc creation channel
    this_server_config = server_config(interaction.guild.id)
    creation_channel = bot_client.get_channel(int(this_server_config.get_creation_vc_channel()))

    # get category
    category = creation_channel.category

    


    # create vc in category
    new_channel = await category.create_voice_channel(name = name, user_limit = users_amount, bitrate = bitrate)
    #new_channel.permissions_synced = True

    # add vc to active channels list
    if not interaction.guild.id in active_channels.keys(): 
        active_channels[interaction.guild.id] = {}
    active_channels[interaction.guild.id][interaction.user.id] = new_channel.id

    if not users_amount is None:
        await interaction.response.send_message(f'created a vc for {users_amount} users', ephemeral = True)
    else:
        await interaction.response.send_message(f'created a vc for unlimited users', ephemeral = True)
    # start timer
    await asyncio.sleep(this_server_config.get_vc_closing_timer())
    if new_channel.id in active_channels[new_channel.guild.id].values():
        if len(new_channel.members) == 0:
            # delete channel
            active_channels[new_channel.guild.id].pop(interaction.user.id)
            print(f'deleted {new_channel.name} channel after {this_server_config.get_vc_closing_timer()} seconds due to inactivity')
            try:
                await new_channel.delete()
            except:
                print('could not delete channel')
                pass

    # respond to interaction


def get_modal_value(interaction, index): #
    return interaction.data['components'][index]['components'][0]['value']