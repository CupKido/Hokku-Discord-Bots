import discord
from discord import app_commands
from discord.ext import commands
from server_config_interface import server_config
import random
import polls
secret_key = ''
with open('token.txt', 'r') as f:
    secret_key = f.read().split("\n")[1]


class discord_client(discord.Client):
    def __init__(self, alert_when_online : bool):
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
            print('synced\n=================================')
        print('im active on: ')
        for x in self.guilds:
            guildID = x.id
            await check_guild_in_db(x)
            if self.alert_when_online:
                channel = self.get_channel(int(server_config.get_specific_announcement_channel(guildID)))
                await channel.send(f'im active, my name is {self.user}')
            print('\t' + str(x.name))
            print('bot is not up')
            
        await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "Cheetah pics"))
        

client = discord_client(False)

async def check_guild_in_db(guild):
    this_server_config = server_config(guild.id)
    this_server_config.confirm_announcement_channel(guild)
    this_server_config.confirm_log_channel(guild)

async def check_has_role(role : str, member : discord.Member):
    if role in [x.name for x in member.roles]:
        return True
    else:
        return False

# slash commands

@client.tree.command(name = 'ping', description = "Check if the bot is online.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('pong! im alive ya know')

@client.tree.command(name = 'set_announcements', description = "sets this channel as the announcements channel")
async def ping(interaction: discord.Interaction):
    try:
        # get server config
        this_server_config = server_config(interaction.guild.id)
        # set announcement channel
        this_server_config.set_announcement_channel(interaction.channel.id)
        await interaction.response.send_message('channel set as announcements channel')
    except:
        await interaction.response.send_message('error')

@client.tree.command(name = 'set_log', description = "sets this channel as the log channel")
async def set_log(interaction: discord.Interaction):
    try:
        # get server config
        this_server_config = server_config(interaction.guild.id)
        # set announcement channel
        this_server_config.set_log_channel(interaction.channel.id)
        await interaction.response.send_message('channel set as log channel')
    except:
        await interaction.response.send_message('error')

@client.tree.command(name = 'help', description = "shows help message")
async def help(interaction: discord.Interaction):
    #treee = client.tree._get_all_commands()
    all_commands = []
    for x in client.tree._get_all_commands():
        if x.name != 'help':
            all_commands.append(x)
    
    help_msg = '```' + 'Our bot\'s commands are:\n' + '\n'.join([('\t\"/' + str(x.name) + '\": ' + str(x.description) + '') for x in all_commands]) + \
        '\n\t\"/help\": to get more info about a specific command' + '```'
    await interaction.response.send_message(help_msg)


@client.tree.command(name = 'choose_creation_channel', description='choose a channel for creationg new voice channels')


@client.tree.command(name = 'spam', description = "spam a message")
async def spam(interaction: discord.Interaction, message: str, amount: int):
    if not await check_has_role('Tester', interaction.user):
        await interaction.response.send_message('you dont have permission to use this command')
        return
    if amount > 100:
        await interaction.response.send_message('bruh, fr? ' + str(amount) + ' times \"' + message + '\"?\nthats way too much, aint no way im doin that.')
        return
    elif amount == 0:
        await interaction.response.send_message('\"\t\"\nyou happy now?')
        return
    elif amount < 0:
        await interaction.response.send_message('bruh, fr? ' + str(amount) + ' times \"' + message + '\"?\nhow the hell am i supposed to do that?.')
        return
    else:
        await interaction.response.send_message('ok, here we go')
    for x in range(amount):
        await interaction.channel.send(message)
    await interaction.channel.send('done spamming, can i go now?')

@client.tree.command(name = 'create_map_poll', description = "creates a poll for which map to play next")
async def create_map_poll(interaction: discord.Interaction, game : discord.Role, close_in : float, poll_id : int = random.randint(10000, 99999), only_vc : bool = False, vc_channel : discord.VoiceChannel = None):
    if not await check_has_role('Tester', interaction.user):
        await interaction.response.send_message('you dont have permission to use this command')
        return
    if close_in > 60:
        await interaction.response.send_message('bruh, fr? ' + str(close_in) + ' minutes?\nthats way too much, aint no way im doin that.')
        return
    elif close_in <= 0:
        await interaction.response.send_message('please enter a positive number')
        return
        rand
        await interaction.response.send_message('ok, here we go')
    await polls.create_gamemap_poll(interaction, game, poll_id, close_in, only_vc, vc_channel)

@client.tree.command(name = 'vote_map', description = "vote for a map")
async def vote_map(interaction: discord.Interaction, poll_id : int, map : int):
    await polls.vote_map(interaction, poll_id, map)

@client.tree.command(name = 'alert_the_valley', description = "dsadasdasdsa")
async def alert_the_valley(interaction: discord.Interaction, msg : str):
    if not await check_has_role('Tester', interaction.user):
        await interaction.response.send_message('you dont have permission to use this command')
        return
    guilds_by_name = [(x.name, x) for x in client.guilds]
    for x in guilds_by_name:
        if x[0] == 'Silicon Valley':
            channel = x[1].text_channels[0]
            await channel.send(msg)
    await interaction.response.send_message('done')


@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    message = reaction.message # our embed
    poll_id = polls.is_active_poll(message)
    if poll_id:
        await polls.handle_reaction(reaction, user, poll_id)


@client.event
async def on_guild_join(guild: discord.guild):
    print('joined')
    await check_guild_in_db(guild)
    channel = client.get_channel(int(server_config.get_specific_announcement_channel(guild.id)))
    await channel.send(f'seems like a nice server, thanks for inviting me!\nI\'m {client.user}, im a bot made by @misa#1335 and @CupKido#0001\nuse /help to see my commands')




def activate():
    client.run(secret_key)