import datetime
import os
import discord
from discord.ext import commands
from cleantext import clean
from DB_instances.generic_config_interface import server_config
from discord_modification_tools import channel_modifier
from Interfaces.IGenericBot import IGenericBot
from Interfaces.ILogger import ILogger
class logger(ILogger):
    LOG_CHANNEL = 'log_channel'
    def __init__(self, bot_client : IGenericBot):
        bot_client.set_logger(self)
        self.bot_client = bot_client
        self.log("==================================================\n\
                logger initialized\
                \n==================================================")

        #@self.bot_client.tree.command(name = 'set_logs_cahnnel', description='sets the channel where the logs will be sent')
        #@commands.has_permissions(administrator=True)
        async def set_logs_cahnnel(interaction, channel : discord.TextChannel):
            this_server_config = server_config(interaction.guild.id)
            last_log_channel = this_server_config.get_param(logger.LOG_CHANNEL)
            if last_log_channel:
                last_log_channel = self.bot_client.get_channel(int(last_log_channel))
                if last_log_channel:
                    await last_log_channel.send('log channel changed')
                    await channel_modifier.remove_readonly(last_log_channel)
            this_server_config.set_params(log_channel = channel.id)
            self.log_guild(f'log channel set to {channel.name}', interaction.guild.id)
            await channel_modifier.set_readonly(channel)
            await interaction.response.send_message(f'log channel set to {channel.name}', ephemeral=True)
        
        #@self.bot_client.tree.command(name = 'remove_logs_cahnnel', description='changes the log channel to nothing')
        #@commands.has_permissions(administrator=True)
        async def set_logs_cahnnel(interaction):
            this_server_config = server_config(interaction.guild.id)
            last_log_channel = this_server_config.get_param(logger.LOG_CHANNEL)
            if last_log_channel:
                last_log_channel = self.bot_client.get_channel(int(last_log_channel))
                if last_log_channel:
                    await last_log_channel.send('log channel cleared')
                    await channel_modifier.remove_readonly(last_log_channel)
            this_server_config.set_params(log_channel = None)
            

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

    async def log_guild_instance(self, msg, guild_id, instance):
        msg = self.remove_emojis(msg)
        todays_file = f'logfile_{str(guild_id)}_' + str(datetime.datetime.now().date()) + '.txt'

        # create directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')

        instance_name = str(type(instance).__name__)
        message = str(msg) + '\t(' +str(datetime.datetime.now())
        # create file if not exists
        with open(f'./logs/{todays_file}', 'a+') as f:
            # write msg and time
            f.write(instance_name + ': ' + str(msg) + '\t(' +str(datetime.datetime.now()) + ')\n')
        
        # send to log channel
        this_server_config = server_config(guild_id)
        log_channel_id = this_server_config.get_param(logger.LOG_CHANNEL)
        if log_channel_id:
            # create embed
            embed = discord.Embed(title=f'{instance_name} log', description=message, color=0x00ff00)
            log_channel = self.bot_client.get_channel(int(log_channel_id))
            await log_channel.send(embed=embed)

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
                      fix_unicode=True, to_ascii=False, no_punct=False)
        
        if str(text)[0] == '\t':
            return '\t' + clean_text
        return clean_text
        # Remove all emojis from the string
        