import datetime
import os
import discord
from cleantext import clean
class logger:
    def __init__(self, bot_client):
        bot_client.set_logger(self)
        self.bot_client = bot_client
        self.log("==================================================\n\
                logger initialized\
                \n==================================================")

    def log(self, msg):
        msg = self.remove_emojis(msg)
        todays_file = 'logfile_' + str(datetime.datetime.now().date()) + '.txt'
        # create directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        # create file if not exists
        with open(f'./logs/{todays_file}', 'a+') as f:
            # write time
            
            # write msg
            f.write(str(msg) + '\t(' +str(datetime.datetime.now()) + ')\n')

    def log_instance(self, msg, instance):
        msg = self.remove_emojis(msg)
        todays_file = 'logfile_' + str(datetime.datetime.now().date()) + '.txt'
        # create directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        # create file if not exists
        with open(f'./logs/{todays_file}', 'a+') as f:
            # write time
            
            # write msg
            f.write(str(type(instance).__name__) + ': ' + str(msg) + '\t(' +str(datetime.datetime.now()) + ')\n')

    def log_guild(self, msg, guild_id):
        msg = self.remove_emojis(msg)
        todays_file = f'logfile_{str(guild_id)}_' + str(datetime.datetime.now().date()) + '.txt'
        # create directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        # create file if not exists
        with open(f'./logs/{todays_file}', 'a+') as f:
            # write time
            
            # write msg
            f.write(str(msg) + '\t(' +str(datetime.datetime.now()) + ')\n')

    def log_guild_instance(self, msg, guild_id, instance):
        msg = self.remove_emojis(msg)
        todays_file = f'logfile_{str(guild_id)}_' + str(datetime.datetime.now().date()) + '.txt'

        # create directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # create file if not exists
        with open(f'./logs/{todays_file}', 'a+') as f:
            # write msg and time
            f.write(str(type(instance).__name__) + ': ' + str(msg) + '\t(' +str(datetime.datetime.now()) + ')\n')

    def get_logs(self):
        todays_file = 'logfile_' + str(datetime.datetime.now().date()) + '.txt'
        file_path = f'./logs/{todays_file}'
        if not os.path.exists(file_path):
            return False
        with open(file_path, 'r') as f:
            return f.read()
    

    def get_guild_logs(self, guild_id): 
        todays_file = f'logfile_{str(guild_id)}_' + str(datetime.datetime.now().date()) + '.txt'
        file_path = f'./logs/{todays_file}'
        if not os.path.exists(file_path):
            return False
        with open(file_path, 'r') as f: 
            return f.read()
    
    def remove_emojis(self, text):
        if len(text) == 0:
            return text
        clean_text = clean(text, no_emoji=True, no_line_breaks=False, no_urls=False,
                      fix_unicode=False, to_ascii=False, no_punct=False)
        
        if str(text)[0] == '\t':
            return '\t' + clean_text
        return clean_text
        # Remove all emojis from the string
        