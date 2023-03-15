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
  
      <GenericBot instance>.add_<name of event>_callback(<name of function to add>)
      
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
  
  A bot feature is a python class that inherits from the BotFeature class, 
  that represents a functionality a bot might preform.
  The class recieves a Generic Bot instance as an argument on its constructor (__init__ func).
  Inside it's constructor, it can sign onto events, and add commmands to the bot

  You, as a developer, are supposed to create your own features.
  An example for a feature that prints hi every hour, and adds a ping command:
  
    from Interfaces.BotFeature import BotFeature
    
    class example_feature(BotFeature):
      def __init__(self, bot : IGenericBot):
        super.__init__(bot)
        bot.add_every_hour_callback(self.say_hi)
        @bot.tree.command(name = 'ping', description='respond to ping')
        async def pong(interaction)
          await interaction.response.send_message('pong!')

      async def say_hi(self):
        print('Hi, an hour has passed')
  
  ### Existing features:
  * room opening
  * confessions
  * actions tester
  * event logger
  * discord api commands
  
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
  
  ##### Code example for 'main.py':
  
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
  
  ##### Code example:
  
    from bot_funcionality_extensions.example_feature_class import example_feature_class
    
    def main():
      ExampleBot = GenericBot_client(<Bot Token>, <db_method>, <config_uri>, <alert_when_online>)
      ExampleBot.add_features(example_feature_class)
      ExampleBot.activate()
    main()

# Generic UI components
  during the making of the bot, we've created an easy to use classes for the discord UI, with the following elements:
  * Buttons
  * Select lists
  * Modals (forms)
  
  ## Generic View
  A class that inherits from the "view" object, that is added to messsages in order to attach a button or a select list.
  You may simply create a GenericView object, with its constructor - 
  
    my_view = Generic_View()
      
  then, when sending a message, and the 'view' parameter, like this:
  
    channel.send(<your message>, view = my_view)
  
  ## Generic Button
  In order to add a button to your view, you need to use the "add_generic_button" method of the Generic_View class.
  ### Parameters:
  
  * label (str)
  * style (discord.ButtonStyle)
  * emoji (str)
  * callback (function)
  * value (any)
 
  ### Code Example:
    my_view = Generic_View()
    gen_view.add_generic_button(label = '<your label>',
                                    style = ui_tools.string_to_color('<color>'),
                                    callback = <your func>,
                                    emoji= '<your emoji>'
                                    )
    channel.send('<your message>', view = my_view)
    
  ## Generic Select
  A UI element that lets the user choose multiple choices from a list.
  The Select can be created with the "add_generic_select" method of the "Generic_View" class.
  
  ### Parameters:
  
  * placeholder (str) - text displayed when nothing is chosen
  * min_values (int) - min values chosen at the same time
  * max_values (int) - max values chosen at the same time
  * callback (function) - function that gets called when the selection is changed
  
    arguments: 
    
    (self, interaction : Discord.Interaction, select : Generic_Select, view : Generic_View)
    
  * options (list) - a list of all the options the select list will contain, 
    each item is a dictionary object structured like this:
    
    {'label' : '<item's label>', 'description' : '<item's description>', 'value' : <item's value>}
    
    you could use the 'value' key to store data related to that choice, 
    that will be later used to process the action that is needed to be taken.
    
  ### Code Example:
    limit_options = [{'label' : 'Unlimited',
                    'description' : '',
                    'value' : 0}] + [
                        {'label' : x,
                        'description' : '',
                        'value' : x}
                         for x in range(1, 25)
                    ]
    gen_view = Generic_View()
    gen_view.add_generic_select(placeholder='<your placeholder>', options=<options list>,
                                 min_values=<you min value>, max_values=<your max value>, callback=<your callback>)
  * note you can only add up to 25 options, if you want to add a user select list, look below
  
  ### Getting selected options
  
  You can find the values selected on the "interaction.data['values']", which contains a list of all values selected by the user.
  
  note that you can only extract the "value" parameter of the option!
  
  if you've inserted None to the value key of the option, itll insert the label as the value variable instead.
  
  ## User Selector
  
  ### Code Example:
  
    gen_view.add_user_selector(placeholder='👋 Add Users', callback=<your func>)
    
  ## UI tools module
  
  The ui tools module contains a few function that can assist you when working with discord's ui component.
  So far the module contains these functions:
  * string_to_color(color : str) - returns the "discord.ButtonStyle" equivalent of the color, so you can use simple color names when programming.
  * color_to_string(color : discord.ButtonStyle) - does the opposite of "string_to_color"
   
    supported colors are: 
    
    red, green, blue, yellow, white, black
    
  * get_modal_value(interaction : discord.Interaction, index : int) - assuming the interaction contains data from filled module, 
  returns the value inserted in the "index" number of TextInput box
  
  


# Useful Links
* discord api documentation:
  https://discordpy.readthedocs.io/en/stable/api.html


