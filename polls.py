import discord
import json
import asyncio

active_polls = {}
async def create_gamemap_poll(interaction: discord.Interaction, game : discord.Role, poll_id : int, close_in : float, only_vc : bool = False, vc_channel : discord.VoiceChannel = None):
    # create poll
    # start poll
    maps = get_game_maps(game)
    poll_dict = {}
    active_polls[poll_id] = {}
    active_polls[poll_id]["voters"] = {}
    active_polls[poll_id]["game"] = game.name
    active_polls[poll_id]["only_vc"] = only_vc
    active_polls[poll_id]["server"] = interaction.guild_id
    if only_vc:
        active_polls[poll_id]["vc_channel"] = vc_channel.id
    response_msg = '```' + 'Map poll for ' + game.name + \
    f'\nPlease use /vote_map, use poll id {str(poll_id)} or react with the matching number:'
    for x in range(len(maps)):
        response_msg += '\n\t' + str(x) + ': ' + str(maps[x])
        poll_dict[str(x)] = 0
    active_polls[poll_id]["votes"] = poll_dict
    response_msg += '```'
    await interaction.response.send_message(response_msg)
    poll_message = interaction.channel.last_message
    active_polls[poll_id]["message"] = poll_message.id
    # add reactions to poll
    for x in range(len(maps)):
        await poll_message.add_reaction(num_to_emoji(x))
    # wait for votes
    await asyncio.sleep(close_in * 60)
    # delete poll message
    await poll_message.delete()
    winners = []
    # close poll
    maxs = max(active_polls[poll_id]["votes"].values())
    votes = active_polls[poll_id]["votes"]
    for x in active_polls[poll_id]["votes"].keys():
        if votes[x] == maxs:
            winners.append(x)
    # get winner
    winners_maps = [maps[int(x)] for x in winners]
    if maxs == 0:
        await interaction.channel.send('No one voted!')
    elif len(winners_maps) == 1:
        await interaction.channel.send('The winner is: ' + winners_maps[0])
    elif len(winners_maps) > 1:
        await interaction.channel.send('The winners are: ' + ', '.join(winners_maps))
  
    # announce winner
    # delete poll
    del active_polls[poll_id]
    return

async def vote_map(interaction: discord.Interaction, poll_id : int, vote : int):
    # vote
    vote = str(vote)
    if active_polls[poll_id]["only_vc"]:
        if interaction.user.voice.channel.id != active_polls[poll_id]["vc_channel"]:
            interaction.response.send_message('You must be in the voice channel to vote!')
            return
    if poll_id in active_polls.keys():
        if vote in active_polls[poll_id]["votes"].keys():
            if interaction.user.id in active_polls[poll_id]["voters"].keys():
                active_polls[poll_id]["votes"][active_polls[poll_id]["voters"][interaction.user.id]] -= 1
            active_polls[poll_id]["votes"][vote] += 1
            active_polls[poll_id]["voters"][interaction.user.id] = vote
            await interaction.response.send_message('Vote registered!')
        else:
            await interaction.response.send_message('Invalid vote!')
    else:
        await interaction.response.send_message('Invalid poll id!')
    return

def is_active_poll(message : discord.Message):
    # check if poll is active
    active_polls_messages = [[active_polls[x]["message"], x] for x in active_polls.keys()]
    for x in active_polls_messages:
        if message.id == x[0]:
            return x[1]
    return False

def get_game_maps(game : discord.Role):
    # get all maps for game
    with open('./data_base/games_info.json', 'r') as f:
        games_info = json.load(f)
    return games_info[game.name.lower()]['maps']

async def handle_reaction(reaction, user, poll_id):
    #make sure reaction is not from bot
    if user.bot:
        return
    if poll_id:
        if active_polls[poll_id]["only_vc"]:
            if user.voice.channel.id != active_polls[poll_id]["vc_channel"]:
                return
        vote = str(emoji_to_num(reaction.emoji))
        if vote in active_polls[poll_id]["votes"].keys():
            if user.id in active_polls[poll_id]["voters"].keys():
                active_polls[poll_id]["votes"][active_polls[poll_id]["voters"][user.id]] -= 1
                for x in reaction.message.reactions:
                    if x != reaction:
                        await x.remove(user)
            active_polls[poll_id]["votes"][vote] += 1
            active_polls[poll_id]["voters"][user.id] = vote
            print(f'{user.name} voted for {vote} in poll {poll_id}')
            # await reaction.message.channel.send('Vote registered!')

def emoji_to_num(emoji):
    return {
        '0️⃣': 0,
        '1️⃣': 1,
        '2️⃣': 2,
        '3️⃣': 3,
        '4️⃣': 4,
        '5️⃣': 5,
        '6️⃣': 6,
        '7️⃣': 7,
        '8️⃣': 8,
        '9️⃣': 9,
        '🔟': 10,
    }[emoji]

def num_to_emoji(num):
    return {
        0: '0️⃣',
        1: '1️⃣',
        2: '2️⃣',
        3: '3️⃣',
        4: '4️⃣',
        5: '5️⃣',
        6: '6️⃣',
        7: '7️⃣',
        8: '8️⃣',
        9: '9️⃣',
        10: '🔟',
    }[num]