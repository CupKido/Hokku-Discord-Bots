import discord 
import datetime
from discord.ext import commands
from discord import app_commands
import permission_checks
from Interfaces.BotFeature import BotFeature
from Interfaces.IGenericBot import IGenericBot
from ui_ext.generic_ui_comps import Generic_View, Generic_Modal
# from DB_instances.per_id_db import per_id_db
# from DB_instances.generic_config_interface import server_config
from DB_instances.DB_instance import General_DB_Names

per_id_db = None
server_config = None
class activity_notifier(BotFeature):
    default_minimum_members = 4
    default_minimum_time = 30
    MINIMUM_MEMBERS = 'minimum_members'
    MINIMUM_TIME = 'minimum_time'
    SERVERS_NOTIFICATIONS = 'servers_notifications'
    USERS_NOTIFICATIONS = 'users_notifications'
    LAST_ACTIVITY_NOTIFICATION_DATE = 'last_activity_notification_date'
    DISABLE_ACTIVITY_NOTIFICATION = 'disable_activity_notification'
    IS_DND = 'is_dnd'

    NOTIFIED_MEMBERS = 'notified_members'
    ALLOW_SPECIFIC_MEMBER_NOTIFICATIONS = 'allow_specific_member_notifications'

    def __init__(self, bot: IGenericBot):
        global per_id_db, server_config
        super().__init__(bot)
        self.bot_client.add_on_voice_state_update_callback(self.notify_relevant_members)

        per_id_db = bot.db.get_collection_instance('ActivityNotifierFeature').get_item_instance
        server_config = bot.db.get_collection_instance(General_DB_Names.Servers_data.value).get_item_instance
        
        @self.bot_client.tree.command(name = 'activity_menu', description = 'Get a menu for activity notifications')
        async def activity_menu(interaction):
            my_view = self.get_activity_menu(interaction.user)
            embed = discord.Embed(title = 'Activity Notifications Menu', description = 'Choose what you want to be notified for', color = 0x4444ff)
            await interaction.response.send_message(embed = embed, view = my_view, ephemeral = True)

        # @self.bot_client.tree.command(name = 'set_minimum_time', description = 'set minimum minutes between activity notifications')
        # async def set_minimum_time_command(interaction, min_time : int):
        #     if min_time < 0:
        #         await interaction.response.send_message('Time must be positive', ephemeral = True)
        #         return
        #     if min_time > 100000:
        #         await interaction.response.send_message('Time must be less than 100000', ephemeral = True)
        #         return
        #     self.set_minimum_time(min_time, interaction.user)
        #     await interaction.response.send_message('Minimum time between notifications set to ' + str(min_time), ephemeral = True)

        @self.bot_client.tree.command(name = 'disable_notifications_for_me', description = 'Disables the option for other members to get notified when you become active')
        async def disable_notifications_for_me_command(interaction):
            member_db = per_id_db(interaction.user.id)
            member_db.set_params(disable_activity_notification=(not member_db.get_param(self.DISABLE_ACTIVITY_NOTIFICATION)))

        @self.bot_client.tree.command(name = 'allow_user_notifications', description = 'allow users to get notified when an other specific user gets on vc')
        @app_commands.check(permission_checks.is_admin)
        async def allow_specific_user_notifications_command(interaction):
            this_server_config = server_config(interaction.guild.id)
            this_server_config.set_params(allow_specific_member_notifications=(not this_server_config.get_param(self.ALLOW_SPECIFIC_MEMBER_NOTIFICATIONS)))
            await interaction.response.send_message('Allow specific member notifications set to ' + str(this_server_config.get_param(self.ALLOW_SPECIFIC_MEMBER_NOTIFICATIONS)), ephemeral = True)


    def get_activity_menu(self, member):
        my_view = Generic_View()
        this_server_config = server_config(member.guild.id)
        member_db = per_id_db(member.id)
        is_dnd = member_db.get_param(self.IS_DND)
        if is_dnd is None:
            is_dnd = False
            member_db.set_params(is_dnd=False)
        notified_members_list = this_server_config.get_param(self.NOTIFIED_MEMBERS)
        if notified_members_list is None:
            notified_members_list = []
        if member.id in notified_members_list:
            my_view.add_generic_button(label='Stop Notifications', style=discord.ButtonStyle.red, callback=self.stop_notifications)
        else:
            my_view.add_generic_button(label='Start Notifications', style=discord.ButtonStyle.green, callback=self.start_notifications)
        if is_dnd:
            my_view.add_generic_button(label='Stop DND', style=discord.ButtonStyle.red, callback=self.stop_dnd_callback)
        else:
            my_view.add_generic_button(label='Start DND', style=discord.ButtonStyle.green, callback=self.start_dnd_callback)
        my_view.add_generic_select(placeholder='Minimum Members for notification', min_values=1, max_values=1, options=[{'label': str(i), 'description' : '', 'value': str(i)} for i in range(1, 25)], callback=self.set_minimum_members_callback)
        
        time_options = [{'label': str(i*10), 'description' : 'minutes', 'value': str(i*10)} for i in range(0, 6)] + \
                        [{'label': str(i), 'description' : 'hours', 'value': str(i*60)} for i in range(1, 12)] + \
                        [{'label': str(i), 'description' : 'days', 'value': str(i*60*24)} for i in range(1, 8)]
        
        my_view.add_generic_select(placeholder='Minimum Time between notifications', min_values=1, max_values=1, options=time_options, callback=self.set_minimum_time_callback)
        if this_server_config.get_param(self.ALLOW_SPECIFIC_MEMBER_NOTIFICATIONS):
            my_view.add_user_selector(placeholder='Notify Me About', callback=self.set_users_notifications_callback)

        return my_view
    
    async def notify_relevant_members(self, member, before, after):
        if before.channel == after.channel:
            return
        if after.channel is None:
            return 
        active_members_count = self.get_members_in_voice_for_guild(member.guild)
        this_server_config = server_config(member.guild.id)
        notified_members_list = this_server_config.get_param(self.NOTIFIED_MEMBERS)
        if notified_members_list is None or len(notified_members_list) == 0:
            return
        active_server_embed = self.get_active_server_embed(member.guild, active_members_count)
        for notified_member in notified_members_list:
            the_member = member.guild.get_member(notified_member)
            if the_member is None:
                continue
            # continue if the member is in a voice channel in the server
            if the_member.voice is not None:
                if the_member.voice.channel.guild.id == member.guild.id:
                    continue
            

            member_db = per_id_db(notified_member)
            # continue if the member is dnd
            if member_db.get_param(self.IS_DND):
                continue
            # continue if the member timeouts have not passed
            if not self.check_if_notification_is_relevant(member_db):
                continue

            servers_notifications_list = member_db.get_param(self.SERVERS_NOTIFICATIONS)
            # continue if the member is not notified for this server
            if servers_notifications_list is None:
                continue
            if str(member.guild.id) not in servers_notifications_list.keys():
                continue
            
            # get the list of members to notify for this member
            to_notify_members_list = member_db.get_param(self.USERS_NOTIFICATIONS)
            if to_notify_members_list is None:
                to_notify_members_list = []

            # get minimum numbers of members for notification
            min_members = servers_notifications_list[str(member.guild.id)]
            if min_members is None:
                member_db.set_params(minimum_members = self.default_minimum_members)
                min_members = self.default_minimum_members

            # alert the member if the server is active
            if active_members_count >= min_members:
                await the_member.send(embed = active_server_embed)
                self.update_last_notification_for_member(member_db)
                return
            # alert the member if he is in the list of members to notify
            elif str(member.id) in to_notify_members_list and this_server_config.get_param(self.ALLOW_SPECIFIC_MEMBER_NOTIFICATIONS):
                # continue if the member disabled notifications for himself
                if per_id_db(member.id).get_param(self.DISABLE_ACTIVITY_NOTIFICATION):
                    continue
                await the_member.send(embed = self.get_member_is_active_embed(member))
                self.update_last_notification_for_member(member_db)
                self._log_guild("Notifying " + str(the_member) + " about " + str(member) + " joining a voice channel", member.guild.id)
                return
                


    def check_if_notification_is_relevant(self, member_db):
        min_time = member_db.get_param(self.MINIMUM_TIME)
        if min_time is None:
            member_db.set_params(minimum_time = self.default_minimum_time)
            min_time = self.default_minimum_time
        now = datetime.datetime.now()
        last_notification_date_dict = member_db.get_param(self.LAST_ACTIVITY_NOTIFICATION_DATE)
        if last_notification_date_dict is None:
            return True
        last_notification_date = datetime.datetime(last_notification_date_dict['year'], 
                                                                 last_notification_date_dict['month'], 
                                                                 last_notification_date_dict['day'], 
                                                                 last_notification_date_dict['hour'], 
                                                                 last_notification_date_dict['minute'])
        if ((now - last_notification_date).total_seconds() / 60) > min_time:
            return True
        return False


    def get_members_in_voice_for_guild(self, guild): 
        members_in_voice = 0
        for channel in guild.voice_channels:
            members_in_voice += len(channel.members)
        return members_in_voice

    def get_active_server_embed(self, guild, active_members_count):
        embed = discord.Embed(title = f'You\'re missing out!', 
                              description = 'There are currently ' + str(active_members_count) + f' active members the {guild.name} server. Come quickly!',
                              color = 0x00ff00)
        if guild.icon is None:
            embed.set_footer(text=guild.name)
        else:
            embed.set_footer(text=guild.name, icon_url=guild.icon.url)
        return embed

    def get_member_is_active_embed(self, member):
        embed = discord.Embed(title = f'{member.name} is active!',
                                description = f'{member.name} is currently in a voice channel on the {member.guild.name} server. Come quickly!',
                                color = 0x00ff00)
        if member.guild.icon is None:
            embed.set_footer(text=member.guild.name)
        else:
            embed.set_footer(text=member.guild.name, icon_url=member.guild.icon.url)
        return embed

    def update_last_notification_for_member(self, member_db):
        now = datetime.datetime.now()
        last_notification_date = {'year' : now.year, 'month' : now.month, 'day' : now.day, 'hour' : now.hour, 'minute' : now.minute}
        member_db.set_params(last_activity_notification_date = last_notification_date)



    ####################
    # Button Callbacks #
    ####################

    async def stop_notifications(self, interaction, button, view):
        this_server_config = server_config(interaction.user.guild.id)
        notified_members_list = this_server_config.get_param(self.NOTIFIED_MEMBERS)
        if notified_members_list is None:
            return
        if interaction.user.id in notified_members_list:
            notified_members_list.remove(interaction.user.id)
            this_server_config.set_params(notified_members = notified_members_list)
        member_db = per_id_db(interaction.user.id)
        servers_notifications_list = member_db.get_param(self.SERVERS_NOTIFICATIONS)
        if servers_notifications_list is None:
            return
        if interaction.user.guild.id in servers_notifications_list.keys():
            del servers_notifications_list[interaction.user.guild.id]
            member_db.set_params(servers_notifications = servers_notifications_list)
        await interaction.response.edit_message(view = self.get_activity_menu(interaction.user))

    async def start_notifications(self, interaction, button, view):
        this_server_config = server_config(interaction.user.guild.id)
        notified_members_list = this_server_config.get_param(self.NOTIFIED_MEMBERS)
        if notified_members_list is None:
            notified_members_list = []
        if interaction.user.id not in notified_members_list:
            notified_members_list.append(interaction.user.id)
            this_server_config.set_params(notified_members = notified_members_list)
        member_db = per_id_db(interaction.user.id)
        servers_notifications_list = member_db.get_param(self.SERVERS_NOTIFICATIONS)
        if servers_notifications_list is None:
            servers_notifications_list = {}
        if interaction.user.guild.id not in servers_notifications_list:
            servers_notifications_list[interaction.user.guild.id] = self.default_minimum_members
            member_db.set_params(servers_notifications = servers_notifications_list)
        await interaction.response.edit_message(view = self.get_activity_menu(interaction.user))

    async def stop_dnd_callback(self, interaction, button, view):
        member_db = per_id_db(interaction.user.id)
        member_db.set_params(is_dnd = False)
        await interaction.response.edit_message(view = self.get_activity_menu(interaction.user))

    async def start_dnd_callback(self, interaction, button, view):
        member_db = per_id_db(interaction.user.id)
        member_db.set_params(is_dnd = True)
        await interaction.response.edit_message(view = self.get_activity_menu(interaction.user))

    ####################
    # Select Callbacks #
    ####################

    async def set_minimum_members_callback(self, interaction, select, view):
        chosen_option = int(select.values[0])
        self.set_minimum_members(chosen_option, interaction.user)
        await interaction.response.send_message('Minimum members to notify you has been set to ' + str(chosen_option), ephemeral = True)

    async def set_minimum_time_callback(self, interaction, select, view):
        chosen_option = int(select.values[0])
        self.set_minimum_time(chosen_option, interaction.user)
        await interaction.response.send_message('Minimum time between notifications has been set to ' + str(chosen_option) + ' minutes', ephemeral = True)

    async def set_users_notifications_callback(self, interaction):
        if len(interaction.data['values']) == 0: 
            await interaction.response.defer(ephemeral = True)
            return
        
        user_id = interaction.data['values'][0]
        if per_id_db(user_id).get_param(self.DISABLE_ACTIVITY_NOTIFICATION):
            await interaction.response.send_message('This user has disabled activity notifications', ephemeral = True)
            return
        member_db = per_id_db(interaction.user.id)
        mems_list = member_db.get_param(self.USERS_NOTIFICATIONS)
        if mems_list is None:
            mems_list = []
        if user_id in mems_list:
            mems_list.remove(user_id)
            await interaction.response.send_message('You will no longer be notified when ' + str(interaction.user.guild.get_member(int(user_id))) + ' joins a voice channel', ephemeral = True)
        else:
            mems_list.append(user_id)
            await interaction.response.send_message('You will now be notified when ' + str(interaction.user.guild.get_member(int(user_id))) + ' joins a voice channel', ephemeral = True)
        member_db.set_params(users_notifications = mems_list)

    ####################

    def set_minimum_time(self, minimum_time, member):
        member_db = per_id_db(member.id)
        member_db.set_params(minimum_time = minimum_time)

    def set_minimum_members(self, minimum_members, member):
        member_db = per_id_db(member.id)
        sevrer_nots = member_db.get_param(self.SERVERS_NOTIFICATIONS)
        if sevrer_nots is None:
            sevrer_nots = {}
        sevrer_nots[str(member.guild.id)] = minimum_members
        member_db.set_params(servers_notifications = sevrer_nots)




'''
A person will be able to open a menu on a server which will be hidden from everyone else.
The menu will give him options for enabling or disabling notifications for certain events,
as well as minimum amount of users required for the event to be notified about.
they will also be able to choose minimum amount of time that has to pass before they get notified again.
they will also be able to get notified when a specific user joins a voice channel.
'''