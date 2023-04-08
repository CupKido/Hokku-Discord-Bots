import discord
from Interfaces.BotFeature import BotFeature
from DB_instances.generic_config_interface import server_config
from bot_funcionality_extensions.TwitchAPI_features.twitch_wrapper import twitch_wrapper
from bot_funcionality_extensions.TwitchAPI_features.eventsub_wrapper import eventsub_wrapper
from dotenv import dotenv_values
config = dotenv_values('.env')


class eventsub_feature(BotFeature):
    initialized = False
    def __init__(self, bot):
        super().__init__(bot)
        eventsub_wrapper.set_access_data(config['TWITCH_CLIENT_ID'], config['TWITCH_API_SECRET'], config['TWITCH_EVENTSUB_SECRET'])
        bot.add_on_ready_callback(self.start_server)

        @bot.tree.command(name="add_onilne_event", description="Adds an event that will be triggered when the streamer goes online")
        async def add_online_event(interaction : discord.Interaction, twitch_channel_name : str):
            await interaction.response.send_message("Adding online event for channel " + twitch_channel_name, ephemeral=True)
            user_id = twitch_wrapper.get_user_id(twitch_channel_name)
            eventsub_wrapper.create_subscription('stream.online', '1', user_id, self.get_stream_online_callback(interaction))
            await interaction.followup.send("Added online event for channel " + twitch_channel_name, ephemeral=True)

        @bot.tree.command(name='delete_all_events', description='Removes an event that will be triggered when the streamer goes online')
        async def remove_online_event(interaction : discord.Interaction): #
            await interaction.response.send_message("Removing all events", ephemeral=True)
            eventsub_wrapper.delete_all_subscriptions()
            await interaction.followup.send("Removed all events", ephemeral=True)

    def get_stream_online_callback(self, interaction : discord.Interaction):
        async def callback(data):
            #print('data: ', data)
            # try:
                username = data['event']['broadcaster_user_name']
                user_id = data['event']['broadcaster_user_id']
                streamer_url = 'https://www.twitch.tv/' + username
                user_info = twitch_wrapper.get_user_info(username)
                stream_info = twitch_wrapper.get_stream_by_user_name(username)
                image = stream_info['thumbnail_url'].replace('{width}', '1920').replace('{height}', '1080')
                embed = discord.Embed(title=stream_info['title'], url=streamer_url, color=0x6441a5)
                embed.set_thumbnail(url=image)
                embed.set_image(url=image)
                embed.set_author(name=username + " is online!", icon_url=user_info['profile_image_url'])
                await interaction.guild.text_channels[0].send(embed=embed)
            # except Exception as e:
            #     print(e)

        return callback

    async def start_server(self):
        eventsub_wrapper.start_server()
    

    
    
