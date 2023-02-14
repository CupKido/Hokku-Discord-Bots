import datetime
import os
import discord
import re
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
    
    def remove_emojis(self, data):
        emoj = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002500-\U00002BEF"  # chinese char
            u"\U00002702-\U000027B0"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642" 
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # dingbats
            u"\u3030"
                        "]+", re.UNICODE)
        return re.sub(emoj, '', data)