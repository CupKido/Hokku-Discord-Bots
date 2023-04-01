import discord
from discord import app_commands
from discord.ext import commands, tasks
import openai
import asyncio
from Interfaces.BotFeature import BotFeature
from DB_instances.per_id_db import per_id_db
from DB_instances.generic_config_interface import server_config
from ui_components_extension.generic_ui_comps import Generic_View, Generic_Modal
import ui_components_extension.ui_tools as ui_tools
import permission_checks
import os
import json
import urllib.request
import aiohttp
import requests
import threading
import time
from dotenv import dotenv_values
config = dotenv_values('.env')

class text_moderation_api(BotFeature):
    FILTER_IS_ON = "filter_is_on"

    def __init__(self, bot):
        super().__init__(bot)
        bot.add_on_message_callback(self.filter_messages)
        @bot.tree.command(name="trigger_filter", description="Generate images with Dall-E")
        @app_commands.check(permission_checks.is_admin)
        async def trigger_filter(interaction: discord.Interaction):
            mode= self.flip_filter_mode(interaction.guild)
            await interaction.response.send_message(f"Filter is now {'on' if mode else 'off'}", ephemeral=True)

    async def filter_messages(self, message):
        if message.author == self.bot_client.user:
            return
        this_guild_config = server_config(message.guild.id)
        if this_guild_config.get_param(self.FILTER_IS_ON) is None:
            return
        if not this_guild_config.get_param(self.FILTER_IS_ON):
            return
        dalle_url = 'https://api.openai.com/v1/moderations'

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + config["OPENAI_KEY"]  # Replace with your actual API key
        }

        data = {
            "input": message.content
        }
        # making request to generate image
        async with aiohttp.ClientSession() as session:
            async with session.post(dalle_url, headers=headers, data=json.dumps(data)) as response:
                response_json = await response.json()
                if response.status == 200:
                    results = response_json['results'][0]['categories']
                else:
                    if response_json['error']['type'] == 'invalid_request_error':
                        raise Exception(str(response_json['error']['message']))
                    else:
                        raise Exception("Error while generating images")
                print(results)
                for x in results.values():
                    if x:
                        await message.delete()

    def flip_filter_mode(self, guild):
        this_guild_config = server_config(guild.id)
        if this_guild_config.get_param(self.FILTER_IS_ON) is None:
            this_guild_config.set_params(filter_is_on = True)
        else:
            this_guild_config.set_params(
                filter_is_on = not this_guild_config.get_param(self.FILTER_IS_ON)
                )
        return this_guild_config.get_param(self.FILTER_IS_ON)

