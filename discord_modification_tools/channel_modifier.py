import discord

async def set_readonly(channel, role = None):
    if channel is None:
        return
    if role == None:
        role = discord.utils.get(channel.guild.roles, name = "@everyone")
    await channel.set_permissions(role, send_messages=False, read_messages=True, create_public_threads=False, create_private_threads=False)

async def remove_readonly(channel, role = None):
    if channel is None:
        return
    if role == None:
        role = discord.utils.get(channel.guild.roles, name = "@everyone")
    await channel.set_permissions(role, send_messages=None, read_messages=None, create_public_threads=None, create_private_threads=None)

async def give_management(channel : discord.VoiceChannel, role = None):
    if channel is None:
        return
    # if role is None:
    #     role = channel.guild.default_role
    await channel.set_permissions(role, manage_channels=True, move_members=True,
                                   connect=True, speak=True, view_channel=True)

async def allow_vc(channel : discord.VoiceChannel, role = None):
    if channel is None:
        return
    if role == None:
        role = discord.utils.get(channel.guild.roles, name = "@everyone")
    await channel.set_permissions(role, connect=True, speak=True, view_channel=True)

async def publish_vc(channel : discord.VoiceChannel, role = None):
    if channel is None:
        return
    if role == None:
        role = discord.utils.get(channel.guild.roles, name = "@everyone")
    await channel.set_permissions(role, connect=None, speak=None, view_channel=None)

async def private_vc(channel : discord.VoiceChannel, role = None):
    if channel is None:
        return
    if role == None:
        role = discord.utils.get(channel.guild.roles, name = "@everyone")
    await channel.set_permissions(role, connect=False, speak=False, view_channel=False)