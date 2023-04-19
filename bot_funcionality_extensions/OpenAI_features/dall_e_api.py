import discord
from discord import app_commands
from discord.ext import commands, tasks
import openai
import asyncio
from Interfaces.BotFeature import BotFeature
from DB_instances.per_id_db import per_id_db
from DB_instances.generic_config_interface import server_config
from ui_components_extension.generic_ui_comps import Generic_View, Generic_Modal
from ui_components_extension.views.embed_pages import embed_pages
import ui_components_extension.ui_tools as ui_tools
import permission_checks
import os
import json
import urllib.request
import aiohttp
import requests
import threading
import time
import datetime
from dotenv import dotenv_values
config = dotenv_values('.env')

class dall_e_api(BotFeature):
    max_pics_per_request = 3
    wait_per_image = 5
    new_wait_time_factor = 1.3
    default_images_amount = 1

    reset_every_hours = 0.5
    images_for_user_per_reset = 8

    unlimited_users = []
    sizes = {"small" : {"str" : "256x256", "price" : 0.016, 'resolusion' : 256}, 
             "medium" : {"str" : "512x512", "price" : 0.018, 'resolusion' : 512}, 
             "large" : {"str" : "1024x1024", "price" : 0.020, 'resolusion' : 1024}}
    defalt_size = "medium"


    USER_MID_REQUEST = "user_mid_request"
    LAST_AMOUNT_RESET = "last_amount_reset"
    REMAINING_IMAGES = "remaining_images"
    IMAGES_OVER_DATE = "images_over_date"
    MONEY_SPENT = "money_spent"

    def __init__(self, bot):
        super().__init__(bot)
        self.last_amount_reset = datetime.datetime.now()
        bot.add_on_message_callback(self.on_message)
        bot.add_on_ready_callback(self.start_tasks)
        @bot.tree.command(name="dall_e_menu", description="Generate images with Dall-E")
        async def dallE_menu(interaction : discord.Interaction):
            await self.show_dallE_menu(interaction)
    
    async def start_tasks(self):
        self.reset_amounts.start()

    @tasks.loop(hours=reset_every_hours)
    async def reset_amounts(self):
        self.last_amount_reset = datetime.datetime.now()
        # for guild in self.bot.guilds:
            # guild_db = server_config(guild.id)
            # now = datetime.datetime.now()
            # now_dictionary = {"year": now.year, "month": now.month, "day": now.day, "hour": now.hour, "minute": now.minute, "second": now.second}
            # guild_db.set_params(last_amount_reset=now_dictionary)


    async def show_dallE_menu(self, interaction):
        view = Generic_View()
        view.add_generic_button(label="Generate Image", style=discord.ButtonStyle.primary, callback=self.generate_image_button_click)
        view.add_generic_button(label="DallE website", style=discord.ButtonStyle.primary, url="https://labs.openai.com/")

        menu_embed = discord.Embed(title="Dall-E Menu", description="Generate images with Dall-E", color=discord.Color.blurple())

        await interaction.response.send_message(embed=menu_embed, view=view, ephemeral=True)
    
    async def generate_image_button_click(self, interaction, button, view):
        member_db = per_id_db(interaction.user.id)
        mid_request = member_db.get_param(self.USER_MID_REQUEST)
        if mid_request:
            await interaction.response.send_message("You are already generating images, please wait for the current request to finish", ephemeral=True)
            return
        
        remaining_images = member_db.get_param(self.REMAINING_IMAGES)
        if remaining_images is None:
            remaining_images = self.images_for_user_per_reset
        if remaining_images <= 0:
            # calculate time to reset
            images_over_date_dict = member_db.get_param(self.IMAGES_OVER_DATE)
            if images_over_date_dict is None:
                images_over_date_dict = {"year": 0, "month": 0, "day": 0, "hour": 0, "minute": 0, "second": 0}
            images_over_date = datetime.datetime(images_over_date_dict["year"], images_over_date_dict["month"], images_over_date_dict["day"], images_over_date_dict["hour"], images_over_date_dict["minute"], images_over_date_dict["second"])
            last_reset = self.last_amount_reset
            # check if last reset passed
            if images_over_date < last_reset:
                remaining_images = self.images_for_user_per_reset
                member_db.set_params(remaining_images=remaining_images)
            else:
                if interaction.user.id not in self.unlimited_users:
                    next_reset_time = last_reset + datetime.timedelta(hours=self.reset_every_hours)
                    await interaction.response.send_message("You have reached the limit of images you can generate per " + str(self.reset_every_hours) + " hours, please try again at " + str(next_reset_time), ephemeral=True)
                    return
                else: 
                    remaining_images = 10000
                    member_db.set_params(remaining_images=remaining_images)
        the_modal = Generic_Modal(title="Generate Image")
        the_modal.add_input(label="Prompt", placeholder="Enter prompt here", required=True, long=True, max_length=750)
        the_modal.add_input(label="Amount ("+ str(self.max_pics_per_request)+" max)", placeholder="Enter amount here", required=False, max_length=len(str(self.max_pics_per_request)))
        the_modal.set_callback(self.generate_image_modal_callback)
        await interaction.response.send_modal(the_modal)

    async def generate_image_modal_callback(self, interaction):
        prompt = ui_tools.get_modal_value(interaction, 0)
        try:
            amount = int(ui_tools.get_modal_value(interaction, 1))
            # amount = self.default_images_amount
        except:
            amount = self.default_images_amount
        if amount > self.max_pics_per_request:
            amount = self.max_pics_per_request
        #self.requests_queue.append((interaction, prompt, amount))
        await self.get_and_respond(interaction, prompt, amount)
        
    async def get_and_respond(self, interaction, prompt, amount):
        try:
            member_db = per_id_db(interaction.user.id)
            remaining_images = member_db.get_param(self.REMAINING_IMAGES)
            if remaining_images is None:
                remaining_images = self.images_for_user_per_reset
            if amount > remaining_images or remaining_images == self.max_pics_per_request and remaining_images == amount:
                amount = remaining_images
                now = datetime.datetime.now()
                now_dict = {"year": now.year, "month": now.month, "day": now.day, "hour": now.hour, "minute": now.minute, "second": now.second}
                member_db.set_params(images_over_date=now_dict)
            next_reset_time = self.last_amount_reset + datetime.timedelta(hours=self.reset_every_hours)
            embed_description = "**prompt:**\n" + prompt + "\n\n**amount:**\n" + str(amount) + "\n\n**remaining images:**\n" + str(remaining_images - amount) + "\n\n**next reset:**\n" + str(next_reset_time)
            sending_embed = embed = discord.Embed(title="Generating images...", description=embed_description, color=discord.Color.blurple())
            await interaction.response.send_message(embed=sending_embed, ephemeral=True)
            money_spent = member_db.get_param(self.MONEY_SPENT)
            if money_spent is None:
                money_spent = 0
            if interaction.user.id not in self.unlimited_users:
                remaining_images = remaining_images - amount
            member_db.set_params(user_mid_request=True, remaining_images=remaining_images, money_spent=money_spent + amount * self.sizes[self.defalt_size]["price"])
            user_dir = "data_base/dall_e_db/" + str(interaction.user.id)
            if not os.path.exists(user_dir):
                        os.makedirs(user_dir)
            # deleting old images
            for file in os.listdir(user_dir):
                file_path = os.path.join(user_dir, file)
                os.remove(file_path)

            #preparing request
            dalle_url = 'https://api.openai.com/v1/images/generations'

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + config["OPENAI_KEY"]  # Replace with your actual API key
            }

            data = {
                "prompt": prompt,
                "n": amount,
                "size": self.sizes[self.defalt_size]["str"]
            }
            # making request to generate image
            async with aiohttp.ClientSession() as session:
                

                #print('getting image:\t' + prompt)
                async with session.post(dalle_url, headers=headers, data=json.dumps(data)) as response:
                    response_json = await response.json()
                    if response.status == 200:
                        print('got images for '+ interaction.user.display_name +'(' + str(interaction.user.id) + '):\t' + prompt)
                        image_urls = response_json['data']
                    else:
                        if response_json['error']['type'] == 'invalid_request_error':
                            raise Exception(str(response_json['error']['message']))
                        else:
                            raise Exception("Error while generating images")
                    

                    # writing images to file
                    ready_embed = discord.Embed(title="Your AI generated images are ready", 
                                                description=embed_description, 
                                                color=discord.Color.blurple())
                    embeds = [ready_embed]
                    for x in range(len(image_urls)):
                        embed = discord.Embed(title="Image " + str(x+1), color=discord.Color.blurple())
                        embed.set_image(url=image_urls[x])
                        embeds.append(embed)
                    embs = embed_pages(embeds)
                    await embs.send(interaction=interaction, followup=True)
                    return
                    files= []
                    # create thread for downloading images and start it
                    t = threading.Thread(target=self.download_images, args=(image_urls, user_dir))
                    t.start()
                    # sleep for the time it takes to download all images, in async way so the bot can still respond
                    await asyncio.sleep(len(image_urls) * self.wait_per_image)
                    # wait for all images to be downloaded, hoping that they are all downloaded already
                    t.join()


                    
                    for x in range(len(image_urls)):
                        filename = user_dir + "\\" + str(x) +".jpg"
                        files.append(discord.File(filename))
                    # sending images with embed
                    await interaction.followup.send(content=interaction.user.mention,
                                                            embed=ready_embed,
                                                            files=files)
                    
                    # updatingg member status
                    member_db.set_params(user_mid_request=False)


        except Exception as e:
            print(e)
            error_embed = discord.Embed(title=str(e), description='embed_description', color=discord.Color.blurple())
            await interaction.followup.send(content=interaction.user.mention, embed=error_embed, ephemeral=True)
            member_db.set_params(user_mid_request=False)

    def download_images(self, image_urls, user_dir):
        # save millis to know how long it took to download images
        seconds_sum = 0
        file_size_sum = 0
        for x in range(len(image_urls)):
            filename = user_dir + "\\" + str(x) +".jpg"
            start = int(round(time.time() * 1000))
            urllib.request.urlretrieve(image_urls[x]['url'], filename)
            file_size_sum += os.path.getsize(filename)
            end = int(round(time.time() * 1000))
            seconds_sum += (end - start) / 1000
        # calculate average time per image
        average_time = seconds_sum / len(image_urls)
        # calculate how long to wait for images to download
        print("average time per image: " + str(average_time))
        print("previous wait per image: " + str(self.wait_per_image))
        self.wait_per_image = average_time * self.new_wait_time_factor
        print("new wait per image: " + str(self.wait_per_image))
        # calculate average file size
        average_file_size = int(file_size_sum / (len(image_urls) * 1000))
        print("average file size: " + str(average_file_size) + "kb")

    async def on_message(self, message):
        if message.author == self.bot_client.user:
            return
        if message.content.startswith('!edit'):
            await self.edit_image(message)
    
    async def edit_image(self, message):
        member_db = per_id_db(message.author.id)
        if member_db.get_param(self.USER_MID_REQUEST):
            await message.channel.send("You are already generating images, please wait for them to finish")
            return
        if len(message.attachments) == 0:
            await message.channel.send("Please attach an image to edit")
            return
        if len(message.attachments) > 1:
            await message.channel.send("Please attach only one image to edit")
            return
        if not message.attachments[0].filename.endswith(".png"):
            await message.channel.send("Please attach a png image file")
            return
        await message.channel.send("Editing image...")
        # downloading image
        image_url = message.attachments[0].url
        image_name = message.attachments[0].filename
        image_path = "data_base/dall_e_db/" + str(message.author.id) + "/" + image_name
        with open(image_path, 'wb+') as f:
            pic_data = await message.attachments[0].read()
            f.write(pic_data)
        # editing image
        user_dir = "data_base/dall_e_db/" + str(message.author.id)
        edited_image_path = user_dir + "/edited_" + image_name
        #preparing request
        dalle_url = 'https://api.openai.com/v1/images/edits'
        prompt = message.content[6:]
        embed_description = "Prompt: " + prompt
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + config["OPENAI_KEY"]  # Replace with your actual API key
        }

        data = {
            "prompt": message.content[6:],
            "n": self.default_images_amount,
            "size": "512x512"
        }

        files = [
            ("image", open(image_path, "rb")),
            ("mask", open("data_base/dall_e_db/mask.png", "rb"))
        ]
        response_json = requests.post(dalle_url, headers=headers, data=json.dumps(data), files=files)
        if response_json.status_code == 200:
            print('got images:\t' + prompt)
            image_urls = response_json.json()['data']
        else:
            if response_json.json()['error']['type'] == 'invalid_request_error':
                raise Exception(str(response_json.json()['error']['message']))
            else:
                raise Exception("Error while generating images")
        
        # making request to generate image
        async with aiohttp.ClientSession() as session:
            
            
            #print('getting image:\t' + prompt)
            async with session.post(dalle_url, headers=headers, data=json.dumps(data), files=files) as response:
                response_json = await response.json()
                if response.status == 200:
                    print('got images:\t' + prompt)
                    image_urls = response_json['data']
                else:
                    if response_json['error']['type'] == 'invalid_request_error':
                        raise Exception(str(response_json['error']['message']))
                    else:
                        raise Exception("Error while generating images")
                

                # writing images to file
                
                files= []
                # create thread for downloading images and start it
                t = threading.Thread(target=self.download_images, args=(image_urls, user_dir))
                t.start()
                # sleep for the time it takes to download all images, in async way so the bot can still respond
                await asyncio.sleep(len(image_urls) * self.wait_per_image)
                # wait for all images to be downloaded, hoping that they are all downloaded already
                t.join()


                
                for x in range(len(image_urls)):
                    filename = user_dir + "\\" + str(x) +".jpg"
                    files.append(discord.File(filename))
                # sending images with embed
                ready_embed = discord.Embed(title="Your AI generated images are ready", 
                                            description=embed_description, 
                                            color=discord.Color.blurple())
                await message.reply(content=message.author.mention,
                                                        embed=ready_embed,
                                                        files=files)
                
                # updatingg member status
                member_db.set_params(user_mid_request=False)

    

        