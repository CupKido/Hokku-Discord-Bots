import discord
import asyncio
import datetime
from discord.ext import commands
from discord import app_commands
import permission_checks
from Interfaces.BotFeature import BotFeature
from DB_instances.generic_config_interface import server_config
from DB_instances.per_id_db import per_id_db


class active_study_rooms(BotFeature):

    ACTIVE_STUDY_ROOMS = 'active_study_rooms'
    LAST_KICK_DATE = 'last_kick_date'
    KICKS_COUNT = 'kicks_count'
    IS_USER_BANNED = 'is_user_banned'
    BANNED_ROLE_ID = 'banned_role_id'
    ban_minutes = 1.5
    seconds_before_warning = 1
    minutes_after_warning = 0.1
    kicks_untill_ban = 2

    def __init__(self, client):
        super().__init__(client)

        client.add_on_voice_state_update_callback(self.on_voice_state_update)

        @client.tree.command(name='add_study_room', description='add a study room')
        @app_commands.check(permission_checks.is_admin)
        async def add_study_room(interaction, channel: discord.VoiceChannel):
            this_server_config = server_config(interaction.guild.id)
            active_study_rooms_list = this_server_config.get_param(
                self.ACTIVE_STUDY_ROOMS)
            if active_study_rooms_list is None:
                active_study_rooms_list = []
            active_study_rooms_list.append(channel.id)
            this_server_config.set_params(
                active_study_rooms=active_study_rooms_list)
            await interaction.response.send_message(f'added {channel.name} to study rooms', ephemeral=True)

        @client.tree.command(name='remove_study_room', description='remove a study room')
        @app_commands.check(permission_checks.is_admin)
        async def remove_study_room(interaction, channel: discord.VoiceChannel):
            this_server_config = server_config(interaction.guild.id)
            active_study_rooms_list = this_server_config.get_param(
                self.ACTIVE_STUDY_ROOMS)
            if active_study_rooms_list is None:
                active_study_rooms_list = []
            try:
                active_study_rooms_list.remove(channel.id)
            except:
                await interaction.response.send_message(f'{channel.name} is not a study room', ephemeral=True)
                return
            this_server_config.set_params(
                active_study_rooms=active_study_rooms_list)
            await interaction.response.send_message(f'removed {channel.name} from study rooms', ephemeral=True)

        @client.tree.command(name='list_study_rooms', description='list all study rooms')
        @app_commands.check(permission_checks.is_admin)
        async def list_study_rooms(interaction):
            this_server_config = server_config(interaction.guild.id)
            active_study_rooms_list = this_server_config.get_param(
                self.ACTIVE_STUDY_ROOMS)
            if active_study_rooms_list is None:
                active_study_rooms_list = []
            await interaction.response.send_message(f'{active_study_rooms_list}', ephemeral=True)

        @client.tree.command(name='set_banned_role', description='set the role to give to banned users')
        @app_commands.check(permission_checks.is_admin)
        async def set_banned_role(interaction, role: discord.Role):
            this_server_config = server_config(interaction.guild.id)
            this_server_config.set_params(banned_role_id=role.id)
            await interaction.response.send_message(f'set banned role to {role.name}', ephemeral=True)

        @client.tree.command(name='check_ban', description='check if a user is banned, and how long until he can join again')
        @app_commands.check(permission_checks.is_admin)
        async def check_ban(interaction):
            member_db = per_id_db(interaction.user.id)
            is_user_banned = member_db.get_param(self.IS_USER_BANNED)
            if is_user_banned is None:
                is_user_banned = False
            if is_user_banned:
                last_kick_date = member_db.get_param(self.LAST_KICK_DATE)
                if last_kick_date is None:
                    last_kick_date = {'year': 2000, 'month': 1,
                                    'day': 1, 'hour': 1, 'minute': 1}
                last_kick_date = datetime.datetime(last_kick_date['year'],
                                                last_kick_date['month'],
                                                last_kick_date['day'],
                                                last_kick_date['hour'],
                                                last_kick_date['minute'])
                now = datetime.datetime.now()
                seconds_left = (self.ban_minutes * 60) - \
                    (now - last_kick_date).total_seconds()
                if seconds_left <= 0:
                    await self.clear_ban(interaction.user, member_db, server_config(interaction.guild.id))
                    is_user_banned = False
                else:
                    minutes_left = seconds_left / 60
                    seconds_left = seconds_left % 60
                    await interaction.response.send_message(f'{interaction.user.mention} is banned, has to wait {int(minutes_left)} minutes and {int(seconds_left)} seconds before joining again.', 
                                                            ephemeral=True)
            if not is_user_banned:
                await interaction.response.send_message(f'{interaction.user.name} is not banned', ephemeral=True)
                return
            

    async def on_voice_state_update(self, member, before, after):
        # check if user is not a bot
        if member.bot:
            return

        try:
            this_server_config = server_config(member.guild.id)
            active_study_rooms_list = this_server_config.get_param(
                self.ACTIVE_STUDY_ROOMS)
            if active_study_rooms_list is None:
                active_study_rooms_list = []

            # check if user is in a voice channel and if the channel is a study room
            if after.channel is not None and after.channel.id in active_study_rooms_list:
                member_db = per_id_db(member.id)

                # check if last kick was more than 15 minutes ago, if so reset kicks count
                last_kick_date = member_db.get_param(self.LAST_KICK_DATE)
                if last_kick_date is None:
                    last_kick_date = {'year': 2000, 'month': 1,
                                      'day': 1, 'hour': 1, 'minute': 1}
                last_kick_date = datetime.datetime(last_kick_date['year'],
                                                   last_kick_date['month'],
                                                   last_kick_date['day'],
                                                   last_kick_date['hour'],
                                                   last_kick_date['minute'])
                now = datetime.datetime.now()
                if (now - last_kick_date).total_seconds() > self.ban_minutes * 60:
                    # reset kicks count 
                    await self.clear_ban(member, member_db, this_server_config)

                # set channel to send messages to
                channel = after.channel

                # check if user was kicked before, if not sets kicks count to 0
                if member_db.get_param(self.KICKS_COUNT) is None:
                    self.clear_kicks(member_db)

                # check if user is banned
                elif member_db.get_param(self.KICKS_COUNT) >= self.kicks_untill_ban:
                    # kick user
                    await self.temp_ban(member, member_db, this_server_config)
                    return

                # wait seconds_before_warning seconds
                await asyncio.sleep(self.seconds_before_warning)

                # check if users camera is on
                if member.voice.self_video or member.voice.self_stream:
                    return
                # warn user
                await channel.send(f'{member.mention} Please turn on your camera or live stream.' +
                                   '\nIf you will not turn on your camera or live stream, ' +
                                   f'you will be kicked from the voice channel in {self.minutes_after_warning} minutes.')
                # wait minutes_after_warning minutes
                await asyncio.sleep(self.minutes_after_warning * 60)

                # check if users camera and livestream not on, if so kick user
                if after.channel is not None and after.channel.id in active_study_rooms_list and not member.voice.self_video and not member.voice.self_stream:
                    await member.move_to(None)
                    await channel.send(f'{member.mention} was kicked for not turning on their camera or live stream.')
                    # update kicks count
                    kicks_count = member_db.get_param(self.KICKS_COUNT)
                    if kicks_count is None:
                        kicks_count = 0
                    kicks_count += 1
                    # update last kick date
                    now = datetime.datetime.now()
                    member_db.set_params(last_kick_date={'year': now.year, 'month': now.month, 'day': now.day, 'hour': now.hour, 'minute': now.minute},
                                         kicks_count=kicks_count)
                    if kicks_count >= self.kicks_untill_ban:
                        # kick user
                        await self.temp_ban(member, member_db, this_server_config)
                        return

        except Exception as e:
            print(e)

    async def temp_ban(self, user, member_db, this_server_config):
        await user.move_to(None)
        banned_role_id = this_server_config.get_param(self.BANNED_ROLE_ID)
        if banned_role_id is None:
            return
        is_user_banned = member_db.get_param(self.IS_USER_BANNED)
        if is_user_banned is not None:
            if is_user_banned:
                return
        member_db.set_params(is_user_banned=True)
        banned_role = user.guild.get_role(banned_role_id)
        await user.add_roles(banned_role)
        await user.send(f'You have been banned from the study rooms for {self.ban_minutes} minutes.' +
                        '\nUse command /check_ban to check in how much time your ban will get removed.')

        await asyncio.sleep(self.ban_minutes * 60)
        await self.clear_ban(user, member_db, this_server_config)

    async def clear_ban(self, user, member_db, this_server_config):
        banned_role_id = this_server_config.get_param(self.BANNED_ROLE_ID)
        if banned_role_id is None:
            return
        banned_role = user.guild.get_role(banned_role_id)
        await user.remove_roles(banned_role)
        member_db.set_params(is_user_banned=False)
        self.clear_kicks(member_db)
    
    def clear_kicks(self, member_db):
        member_db.set_params(kicks_count=0)

    