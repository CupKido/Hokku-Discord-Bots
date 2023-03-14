# Hokku-Discord-Bots
A simple architecture that allows loading and unloading features from discord bots

The system is made out of a few main parts:

## Generic Bot

  The generic bot class is a class that allow you to sign up onto its events (mostly events caused by discord - discord event),
  so you can get called even when outside the generic bot's class
  
  #### parameters of constructor function:
  
    secret_key - your bot's token
    
    db_method (optional) - 'J' if you want to use json file for your database, or 'M' if you want to use MongoDB
      Default - 'J'
      
    config_uri (optional) - what path to use for either db or uri for MongoDB server
      Default - None
      
    alert_when_online (optional) - whether to notify all guilds that the bot is ready and active
      Default - False
    
  
  To make a function get called when an event happens, 
  you need to add it to the event's callbacks list, 
  by calling the GenericBot's Method:
      
      add_<name of event>
      
  * notice that all functions added to events callbacks must be **async functions** since they're called with **'await'** 
  
### List of supported events:

  Client events:

  * on_ready_callback

  * on_session_resumed_callback

  * on_guild_join_callback

  * on_guild_remove_callback

  message events:

  * on_message_callback

  * on_message_delete_callback

  * on_message_edit_callback

  invite events:

  * on_invite_create_callback

  * on_invite_delete_callback

  member events:

  * on_voice_state_update_callback

  * on_member_remove_callback

  * on_member_update_callback

  * on_member_ban_callback

  * on_member_unban_callback

  guild role events:

  * on_guild_role_create_callback

  * on_guild_role_delete_callback

  * on_guild_role_update_callback

  channel events:

  * on_guild_channel_create_callback

  * on_guild_channel_update_callback

  * on_guild_channel_delete_callback

  scheduler events:

  * every_hour_callback

  * every_5_hours_callback

  * every_day_callback
  
  
## Bot Features
  
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
  
## The Main File 
  The main function is the actual python file we run on our machine.
  On our main function, we will create our generic bot instance, 
  and add into it all the features that we'd like to load, 
  by using the **'add_features'** method for a **few** features or the **'add_feature'** method for a **single** feature, 
  and sending the feature's class instance as a parameter.
  
  After that, we will use the **'activate'** method of the GenericBot to start the bot.
  
  There are 2 ways to create a main file.
  
  #### First way (more simple):
  
  You can either use the "framework" way, by filling up the 'main.py' file
  first - import the features you want to use, then continue by filling up the functions 'get_token', 'get_db_method' and 'add_features' with your code.
  then run the 'main_framework.py' file.
  
  Code example for 'main.py':
  
    from bot_funcionality_extensions.example_feature_class import example_feature_class

    def get_token():
        # return your discord bot token
        return <bot token>
        pass

    def get_db_method():
        # return 'J' for json or 'M' for mongo
        return 'J'
        pass

    def add_features(new_generic_bot):
        # add features to the bot with the following syntax:
        # new_generic_bot.add_features(example_feature_class, example_feature_class2, ...)
        new_generic_bot.add_features(example_feature_class)
        pass

  #### Second way (more flexible):
  
  You can also create your own main file, and inside it:
  
  * import necessary features
  
  * create a bot
  
  * add features
  
  * activate
  
  Then run your own file.
  
  Code example:
  
    from bot_funcionality_extensions.example_feature_class import example_feature_class
    
    def main():
      ExampleBot = GenericBot_client(<Bot Token>, <db_method>, <config_uri>, <alert_when_online>)
      ExampleBot.add_features(example_feature_class)
      ExampleBot.activate()
    main()
      


