import discord

async def set_readonly(channel, role = None):
    if role == None:
        role = channel.guild.default_role
    await channel.edit(sync_permissions=True)
    await channel.set_permissions(channel.guild.default_role, send_messages=False, read_messages=True, create_public_threads=False, create_private_threads=False)

async def remove_readonly(channel, role = None):
    if role == None:
        role = channel.guild.default_role
    await channel.edit(sync_permissions=True)
    await channel.set_permissions(channel.guild.default_role, send_messages=None, read_messages=None, create_public_threads=None, create_private_threads=None)