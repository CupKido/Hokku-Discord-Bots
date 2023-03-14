# Hokku-Discord-Bots
A simple architecture that allows loading and unloading features from discord bots
The system is made out of a few main parts:

# Generic Bot #

  The generic bot class is a class that allow you to sign up onto its events (mostly events caused by discord - discord event),
  so you can get called even when outside the generic bot's class

  To make a function get called when an event happens, 
  you need to add it to the event's callbacks list, 
  by calling the GenericBot's Method:
      add_<name of event>
  * notice that all functions added to events callbacks must be async functions *
  List of supported events:

    # Client events:

      on_ready_callback
      on_session_resumed_callback
      on_guild_join_callback
      on_guild_remove_callback

    # message events:

      on_message_callback
      on_message_delete_callback
      on_message_edit_callback

    # invite events:

      on_invite_create_callback
      on_invite_delete_callback

    # member events:
      on_voice_state_update_callback
      on_member_remove_callback
      on_member_update_callback
      on_member_ban_callback
      on_member_unban_callback

    # guild role events:

      on_guild_role_create_callback
      on_guild_role_delete_callback
      on_guild_role_update_callback

    # channel events:

      on_guild_channel_create_callback
      on_guild_channel_update_callback
      on_guild_channel_delete_callback

    # scheduler events:

      every_hour_callback
      every_5_hours_callback
      every_day_callback
  
  
# Features #
  
  A feature is a python class, is a class that inherits from the BotFeature class.
  The class recieves a Generic Bot instance as an argument on its constructor (__init__ func).
  Inside it's constructor, it can sign onto events, and add commmands to the bot

  An example for a feature that prints hi every hour, and adds a ping command:
    class example_feature:
      def __init__(self, bot : IGenericBot):
        super.__init__(bot)
        bot.add_every_hour_callback(self.say_hi)
        @bot.tree.command(name = 'ping', description='respond to ping')
        async def pong(interaction)
          await interaction.response.send_message('pong!')

      async def say_hi(self):
        print('Hi, an hour has passed')
  
# The Main function #
  


