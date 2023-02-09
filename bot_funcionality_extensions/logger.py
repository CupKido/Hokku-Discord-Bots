import datetime
class logger:
    def __init__(self, bot_client):
        bot_client.set_logger(self)

    def log(self, msg):
        todays_file = str(datetime.datetime.now().date()) + '_logfile.txt'
        # create file if not exists
        with open(f'./logs/{todays_file}', 'a+') as f:
            # write time
            
            # write msg
            f.write(msg + '\t(' +str(datetime.datetime.now()) + ')\n')
