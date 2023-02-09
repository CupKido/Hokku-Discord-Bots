import datetime
import os
class logger:
    def __init__(self, bot_client):
        bot_client.set_logger(self)
        self.bot_client = bot_client
        self.log("==================================================\n\
                logger initialized\
                \n==================================================")

    def log(self, msg):
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
        todays_file = 'logfile_' + str(datetime.datetime.now().date()) + '.txt'
        # create directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        # create file if not exists
        with open(f'./logs/{todays_file}', 'a+') as f:
            # write time
            
            # write msg
            f.write(str(type(instance).__name__) + ': ' + str(msg) + '\t(' +str(datetime.datetime.now()) + ')\n')

    def get_logs(self):
        todays_file = 'logfile_' + str(datetime.datetime.now().date()) + '.txt'
        file_path = f'./logs/{todays_file}'
        if not os.path.exists(file_path):
            return False
        with open(file_path, 'r') as f:
            return f.read()