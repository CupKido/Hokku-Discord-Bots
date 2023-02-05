import discord

async def set_readonly(channel):
    await channel.edit(sync_permissions=True)
    await channel.set_permissions(channel.guild.default_role, send_messages=False, read_messages=True, create_public_threads=False, create_private_threads=False)

async def set_writable(channel):
    await channel.edit(sync_permissions=True)
    await channel.set_permissions(channel.guild.default_role, send_messages=True, read_messages=True, create_public_threads=True, create_private_threads=True)