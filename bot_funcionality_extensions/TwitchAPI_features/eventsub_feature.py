import discord
from discord.ext import tasks
from Interfaces.BotFeature import BotFeature
from DB_instances.generic_config_interface import server_config
from DB_instances.per_id_db import per_id_db
from bot_funcionality_extensions.TwitchAPI_features.twitch_wrapper import twitch_wrapper
from bot_funcionality_extensions.TwitchAPI_features.eventsub_wrapper import eventsub_wrapper
import async_timeout
from dotenv import dotenv_values

config = dotenv_values('.env')


class eventsub_feature(BotFeature):

    initialized = False

    SUBSCRIPTIONS_CONTEXT = 'subscriptions_context'
    STREAM_ANNOUNCEMENET_CHANNEL = 'stream_announcement_channel'

    db_id = 'subscrioption_db'
    def __init__(self, bot):
        super().__init__(bot)
        self.alert_queue = []

        eventsub_wrapper.set_access_data(config['TWITCH_CLIENT_ID'], config['TWITCH_API_SECRET'], config['TWITCH_EVENTSUB_SECRET'])
        bot.add_on_ready_callback(self.start_server)

        @bot.tree.command(name="add_onilne_event", description="Adds an event that will be triggered when the streamer goes online")
        async def add_online_event(interaction : discord.Interaction, twitch_channel_name : str):
            await interaction.response.send_message("Adding online event for channel " + twitch_channel_name, ephemeral=True)
            user_id = twitch_wrapper.get_user_id(twitch_channel_name)
            # make sure that a subscription for this user does not already exist
            db = per_id_db(self.db_id)
            sub_context = db.get_param(self.SUBSCRIPTIONS_CONTEXT)
            if sub_context is None:
                sub_context = {}
            sub_created = False
            subs_data = eventsub_wrapper.get_subscriptions()['data']
            print(subs_data)
            for sub in subs_data:
                print(sub)
                print(sub['type'])
                print(sub['condition']['broadcaster_user_id'])
                print(user_id)
                if sub['type'] == "stream.online" and int(sub['condition']['broadcaster_user_id']) == int(user_id):
                    # add the guild to the list of guilds that will be notified
                    if sub['id'] in sub_context.keys():
                        if type(sub_context[sub['id']]) is list:
                            if interaction.guild.id not in sub_context[sub['id']]:
                                sub_context[sub['id']].append(interaction.guild.id)
                            else:
                                await interaction.followup.send("Channel already added", ephemeral=True)
                                return
                        elif sub_context[sub['id']] != interaction.guild.id:
                            sub_context[sub['id']] = [sub_context[sub['id']], interaction.guild.id]
                        else:
                            sub_context[sub['id']] = [sub_context[sub['id']]]
                    sub_created = True
                    break
            if not sub_created:
                sub = eventsub_wrapper.create_subscription('stream.online', '1', user_id)
                if sub.id in sub_context.keys():
                    if type(sub_context[sub.id]) is list:
                        if interaction.guild.id not in sub_context[sub.id]:
                            sub_context[sub.id].append(interaction.guild.id)
                        else:
                            await interaction.followup.send("Channel already added", ephemeral=True)
                            return
                    elif sub_context[sub.id] != interaction.guild.id:
                        sub_context[sub.id] = [sub_context[sub.id], interaction.guild.id]
                    else:
                        sub_context[sub.id] = [sub_context[sub.id]]
                else:
                    sub_context[sub.id] = [interaction.guild.id]
            await interaction.followup.send("Added online event for channel " + twitch_channel_name, ephemeral=True)
            db.set_params(subscriptions_context=sub_context)
            

        @bot.tree.command(name='remove_online_event', description='Removes an event that will be triggered when the streamer goes online')
        async def remove_online_event(interaction : discord.Interaction, twitch_channel_name : str): #
            await interaction.response.send_message("Removing online event for channel " + twitch_channel_name, ephemeral=True)
            user_id = twitch_wrapper.get_user_id(twitch_channel_name)
            db = per_id_db(self.db_id)
            sub_context = db.get_param(self.SUBSCRIPTIONS_CONTEXT)
            if sub_context is None:
                sub_context = {}
            sub_created = False
            subs_data = eventsub_wrapper.get_subscriptions()['data']
            for sub in subs_data:
                if sub['type'] == "stream.online" and sub['condition']['broadcaster_user_id'] == user_id:
                    # add the guild to the list of guilds that will be notified
                    if sub['id'] in sub_context.keys():
                        if type(sub_context[sub['id']]) is list:
                            if interaction.guild.id in sub_context[sub['id']]:
                                sub_context[sub['id']].remove(interaction.guild.id)
                            else:
                                await interaction.followup.send("Channel not added", ephemeral=True)
                                return
                        elif sub_context[sub['id']] == interaction.guild.id:
                            sub_context[sub['id']] = []
                        else:
                            await interaction.followup.send("Channel not added", ephemeral=True)
                            return
                    if len(sub_context[sub['id']]) == 0:
                        eventsub_wrapper.delete_subscription(sub['id'])
                        del sub_context[sub['id']]
                    db.set_params(subscriptions_context=sub_context)
                    await interaction.followup.send("Removed online event for channel " + twitch_channel_name, ephemeral=True)
                    return
            await interaction.followup.send("Channel not added", ephemeral=True)
            



        @bot.tree.command(name='delete_all_events', description='Removes an event that will be triggered when the streamer goes online')
        async def delete_all_events(interaction : discord.Interaction): #
            await interaction.response.send_message("Removing all events", ephemeral=True)
            eventsub_wrapper.delete_all_subscriptions()
            await interaction.followup.send("Removed all events", ephemeral=True)
            db = per_id_db(self.db_id)
            sub_context = db.get_param(self.SUBSCRIPTIONS_CONTEXT)
            if sub_context is not None:
                db.set_params(subscriptions_context={})

        @bot.tree.command(name='set_stream_announcements', description='Sets the channel where the bot will announce when a streamer goes online')
        async def remove_online_event(interaction : discord.Interaction, channel : discord.TextChannel): #
            guild_db = server_config(interaction.guild.id)
            guild_db.set_params(stream_announcement_channel=channel.id)
            await interaction.response.send_message("Set stream announcements channel to " + channel.mention, ephemeral=True)

        
    def get_stream_online_callback(self, interaction : discord.Interaction):
        async def callback(data):
            self.alert_queue.append((data, interaction))

        return callback

    @tasks.loop(seconds=10)
    async def check_alert_queue(self):
        db = None
        sub_context = None
        while eventsub_wrapper.events_queue:
            if db is None:
                db = per_id_db(self.db_id)
                sub_context = db.get_param(self.SUBSCRIPTIONS_CONTEXT)
                print(sub_context)
                if sub_context is None:
                    sub_context = {}
            subscription, data = eventsub_wrapper.events_queue.pop(0)
            print(subscription, data)
            print(subscription.id, sub_context.keys(), subscription.id in sub_context.keys())
            if subscription.id in sub_context.keys():
                try:
                    # creating embed
                    print('creating embed')
                    username = data['event']['broadcaster_user_name']
                    user_id = data['event']['broadcaster_user_id']
                    streamer_url = 'https://www.twitch.tv/' + username
                    user_info = twitch_wrapper.get_user_info(username)
                    stream_info = twitch_wrapper.get_stream_by_user_name(username)
                    image = stream_info['thumbnail_url'].replace('{width}', '1920').replace('{height}', '1080')
                    embed = discord.Embed(title=stream_info['title'], url=streamer_url, color=0x6441a5)
                    embed.set_image(url=image)
                    embed.set_author(name=username + " is online!", icon_url=user_info['profile_image_url'])
                    print('embed created', 'guilds to notify', sub_context[subscription.id])
                    if type(sub_context[subscription.id]) is not list:
                        sub_context[subscription.id] = [sub_context[subscription.id]]
                    for guild_id in sub_context[subscription.id]:
                        guild_db = server_config(guild_id)
                        channel_id = guild_db.get_param(self.STREAM_ANNOUNCEMENET_CHANNEL)
                        #print(channel_id)
                        if channel_id is None:
                            continue
                        channel = self.bot_client.get_channel(channel_id)
                        #print(channel)
                        if channel is None:
                            continue
                        await channel.send(embed=embed)
                except Exception as e:
                    print(e)
                    continue

    

    async def start_server(self):
        self.check_alert_queue.start()
        eventsub_wrapper.start_server()
    

    
    
