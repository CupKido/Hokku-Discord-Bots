# Hokku-Discord-Bots
A simple framework that allows creating, loading and unloading features from discord bots, very similar to discord Cogs

### The framework is made out of a few main parts:

-   [Generic Bot](#generic-bot)
    -   [Supported Events](#list-of-supported-events)
-   [Bot Features](#bot-features)
    -   [Existing Features](#existing-features)
    -   [Logging](#logging)
    -   [Loggers](#loggers)
-   [The Main File](#the-main-file)
    -   [Framework Way](#first-way)
    -   [Custom Way](#second-way)

### Available tools:

-   [Generic UI components](#generic-ui-components)
    -   [Generic View](#generic-view)
    -   [Generic Button](#generic-button)
    -   [Generic Select](#generic-select)
    -   [User Selector](#user-selector)
    -   [Generic Modal](#generic-modal)
-   [UI tools module](#ui-tools-module)
- [View Components](#view-components)
    
    
    
    
[Useful Links](#useful-links)

## Generic Bot

  The generic bot class is a class that allow you to sign up onto its events (mostly events caused by discord - discord event),
  so you can get called even when outside the generic bot's class.
  
  #### parameters of constructor function:
  
  * secret_key - your bot's token

  * db_method- a [DB_Methods](#db-instance) instance. In case you chose MongoDB then make sure to set enviorment variable "MONGO_DB_CONNECTION_STRING" as your           connection string
  
  * db_name - what DB to use inside the DB server/files
  
  * alert_when_online (optional) - whether to notify all guilds that the bot is ready and active
  
    Default - False
    
  The generic bot also has a logger feature and a db instance built into it;
  * [bot.db](#db-instance)
  * [bot.logger](#logger-feature)
  
  To make a function get called when an event happens, 
  you need to add it to the event's callbacks list, 
  by calling the GenericBot's Method:
  
      <GenericBot instance>.add_<name of event>_callback(<name of function to add>)
      
  * notice that all functions added to events callbacks must be **async functions** since they're called with **'await'** 
  
  
  
### List of supported events

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
  
  All events:
  
  * on_before_any_event_callbacks
  
  * on_after_any_event_callbacks
  
  
## Bot Features
  
  A bot feature is a python class that inherits from the BotFeature class, 
  that represents a functionality a bot might preform.
  The class recieves a Generic Bot instance as an argument on its constructor (__init__ func).
  Inside it's constructor, it can sign onto events, and add commmands to the bot

  You, as a developer, are supposed to create your own features for your needs.
  
  #### Code Example:
  
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
  
  ### Logging
  
  The bot feature also has an async protected logging methods:
  
  _log(meesage : str) - for logging logs related to the bot
  
  _log_guild(message : str, guild_id : int) - for logging logs that are about actions that are related to the guild. if log channel is set by an adming, all guild   logs       will be sent in it
  
  # Loggers
  
  Loggers are class that implement the ILogger abstract class, that can be added to the bot.
  when creating a logging method inside, make sure to use the "logging_function" decorator of the ILogger class,
  that makes sure to alert all observers about the log.
  
  The "logging_function" takes one parameter of the "log_type" enum class, which as for now contains the values:
  * system_log
  * system_guild_log
  * feature_log
  * feature_guild_log
  
  In addition, observers can be added to loggers with the "add_log_observer" method of "ILogger", that receives:
  * logtype : log_type
  * callback : function
  
  ### Existing features:
  * room opening - lets you to have a dynamic server
  * confessions - lets you confess in a chosen confession channel
  * actions tester - tool that helps you test actions of other bots
  * event logger - tool that lets you see the logs of the past day
  * discord api commands - lets you use some basic api command
  * prefix_adapter - adapts all commands without parameters to prefix commands
  * to do list - lets each user access a to do list that is saved on the bot
  * active study rooms - for rooms with cam only
  * activity notifier - lets users get notified when there are more than a certain number of users on vc, or when their friend joins vc
  * help command - adds the help command that sends a description about all commands that specific user can use
  * 
  
## The Main File 
  The main function is the actual python file we run on our machine.
  On our main function, we will create our generic bot instance, 
  and add into it all the features that we'd like to load, 
  by using the **'add_features'** method for a **few** features or the **'add_feature'** method for a **single** feature, 
  and sending the feature's class instance as a parameter.
  
  After that, we will use the **'activate'** method of the GenericBot to start the bot.
  
  There are 2 ways to create a main file.
  
  ### First way
  #### (more simple)
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

  ### Second way 
  #### (more flexible)
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

## Generic UI components
  during the making of the bot, we've created an easy to use classes for the discord UI, with the following elements:
  * Buttons
  * Select lists
  * Modals (forms)
  
  ### Generic View
  A class that inherits from the "view" object, that is added to messsages in order to attach a button or a select list.
  You may simply create a GenericView object, with its constructor - 
  
    my_view = Generic_View()
      
  then, when sending a message, and the 'view' parameter, like this:
  
    channel.send(<your message>, view = my_view)
  
  ### Generic Button
  In order to add a button to your view, you need to use the "add_generic_button" method of the Generic_View class.
  #### Parameters:
  
  * label (str)
  * style (discord.ButtonStyle)
  * emoji (str)
  * callback (function)
  * value (any)
 
  #### Code Example:
    my_view = Generic_View()
    gen_view.add_generic_button(label = '<your label>',
                                    style = ui_tools.string_to_color('<color>'),
                                    callback = <your func>,
                                    emoji= '<your emoji>'
                                    )
    channel.send('<your message>', view = my_view)
  ### ON OFF button
  a button that has its own functionality for turning green and red depends on a recieved callback.
  #### Parameters:
  
  * Any parameter from discord.ui.Button.
  * value (bool) - on/off.
  * callback : function - a function that returns the new value based on the click interaction and the current value.
  #### Code Example:
    my_view = Generic_View()
    def update_callback(interaction, prev):
        new_val = not prev
        update_db(interaction.user.id, new_val) // or whatever you wanna do based on the click
        return new_val
    gen_view.add_on_off_button(label = '<your label>',
                                    callback = update_callback, // your callback function
                                    emoji= '<your emoji>'
                                    )
    channel.send('<your message>', view = my_view)
  ### Generic Select
  A UI element that lets the user choose multiple choices from a list.
  The Select can be created with the "add_generic_select" method of the "Generic_View" class.
  
  #### Parameters:
  
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
    
  #### Code Example:
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
  * note you can only add up to 25 options, if you want to add a user select list, look for "User Selector" below
  
  #### Getting selected options
  
  You can find the values selected on the "interaction.data['values']", which contains a list of all values selected by the user.
  
  note that you can only extract the "value" parameter of the option!
  
  if you've inserted None to the value key of the option, itll insert the label as the value variable instead.
  
  ### User Selector
  
  #### Code Example:
  
    gen_view.add_user_selector(placeholder='👋 Add Users', callback=<your func>)
    
  ### Generic Modal
  
  Callback arguments - (self, interaction)
  
  **(To Be Continued)**
  
  ## UI tools module
  
  The ui tools module contains a few function that can assist you when working with discord's ui component.
  So far the module contains these functions:
  * string_to_color(color : str) - returns the "discord.ButtonStyle" equivalent of the color, so you can use simple color names when programming.
  * color_to_string(color : discord.ButtonStyle) - does the opposite of "string_to_color"
   
    supported colors are: 
    
    red, green, blue, yellow, white, black
    
  * get_modal_value(interaction : discord.Interaction, index : int) - assuming the interaction contains data from filled modal (form), 
  returns the value inserted in the "index" number of TextInput box
  
  ## View Components
  
  ### Embed Pages
  
  A class that inherits the discord view component, for presenting lists, search results or just sending a group of embeds.
  
  #### Usage:
    view = embed_pages(embeds, ...)
    view.send(interaction, ...)
  #### Parameters:
  ##### constructor
  * embeds : list - list object with all embeds that you'd like to present.
  * timeout : int (optional) - timeout of view.
  * embed_title : discord.Embed (optional) - an embed to always present at the top of the presented list.
  * title : str (optional) - the content of the message sent.
  * items_per_page : int (optional) - how many embeds to show in each page. if embed_title is given max is 9 otherwise max is 10.
  * add_numbering : bool (optional) - whether to add item number in the footer to every embed.
  ##### embed_pages.send()
  * interaction : discord.Interaction - the interaction to respond to.
  * ephemeral : bool (optional) - whether to reply privately
  * followup : bool (optional) - whether to reply as followup
  * views : list (optional) - list of view to attach to message
  #### Code example:
    embeds = []
    for x in range(1,9)
        this_embed = discord.Embed(title=str(x), description=f'this is embed number {x}')
        embeds.append(this_embed)
    title_embed = discord.Embed(title='this is a very cool title!')
    pages = embed_pages(embeds=embeds, embed_title=title_embed, items_per_page=3, add_numbering=True)
    pages.send(interaction, ephemeral=True)
  Creating a list of embeds, and sending them back privately, with an embed title
  
  ### Minesweeper
  
  An example of a view that contains functionallity inside. 
  In this case - contains functionallity for the game Minesweeper.
  just attach an instance as a view to any message, and youll be presented with an interactinve game board, that lets you play the game!
  
  ## DB instances
  the db_instances is a module that contains different classes for using the DB in an easy way.
  
  Few of the items inside it are:
  * General_DB_Names : Enum - contains a few commonly used names for collections, that features could share.
  * DB_Methods : Enum - Contains the DB interfaces options, currently supports:
    * Json
    * MongoDB
    * DynamicDB
  * DB_instance : class - an abstract class for db instances
  * collection_instance : class - an abstract class for collection instances
  * item_instance : class - represents an item inside a collection.
  * MongoDB_instance : class (inherits DB_instance) - used to connect to a MongoDB Database, parameters are:
    * db_name : str 
    * connection_string=None : str
  * JsonDB_instance : class (inherits DB_instance) - used to maintain a Json database, parameters are:
    * db_name : str
    * location=None : str
  * DynamicDB : class (inherits DB_instance) - used to maintain a variables based Databse, parameters are:
    * db_name : str 
  * DB_factory : function - for getting a DB_instance based on parameters, which are:
    * db_name : str
    * DB_Method : DB_Methods
    * uri : str - either connection string for MongoDB or location for Json
  * transfer_DB : function - for transfering all data between two DBs, parameters:
    * from_db : DB_instance
    * to_db : DB_instance
    * overwrite : bool (optional)
    * delete_from_db : bool (optional)


# Useful Links
* discord api documentation about discord modules:
  https://discordpy.readthedocs.io/en/stable/api.html
* discord api documentation about commands:
  https://discordpy.readthedocs.io/en/stable/ext/commands
* discord api documentation about interactions:
  https://discordpy.readthedocs.io/en/stable/interactions/api.html
* Article about discord Embeds structure:
  https://plainenglish.io/blog/send-an-embed-with-a-discord-bot-in-python

