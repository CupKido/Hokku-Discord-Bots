import discord

def string_to_color(color_name):
    if color_name == 'red':
        return discord.ButtonStyle.red
    elif color_name == 'green':
        return discord.ButtonStyle.green
    elif color_name == 'blue':
        return discord.ButtonStyle.blurple
    elif color_name == 'yellow':
        return discord.ButtonStyle.yellow
    elif color_name == 'white':
        return discord.ButtonStyle.grey
    elif color_name == 'black':
        return discord.ButtonStyle.black
    else:
        return None

def color_to_string(color):
    if color == discord.ButtonStyle.red:
        return 'red'
    elif color == discord.ButtonStyle.green:
        return 'green'
    elif color == discord.ButtonStyle.blurple:
        return 'blue'
    elif color == discord.ButtonStyle.yellow:
        return 'yellow'
    elif color == discord.ButtonStyle.grey:
        return 'white'
    elif color == discord.ButtonStyle.black:
        return 'black'
    else:
        return 'blue'
    
def get_modal_value(interaction, index):
    return interaction.data['components'][index]['components'][0]['value']

def get_select_values(interaction):
    return interaction.data['values']

class mode_styles:
    on = discord.ButtonStyle.green
    off = discord.ButtonStyle.red

    @classmethod
    def get_on_off(instance, mode):
        if mode:
            return instance.on
        else:
            return instance.off