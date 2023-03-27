import discord

def is_admin(interaction):
    if type(interaction.channel) is discord.channel.PartialMessageable or type(interaction.channel) is discord.channel.DMChannel:
        return True
    return interaction.user.guild_permissions.administrator