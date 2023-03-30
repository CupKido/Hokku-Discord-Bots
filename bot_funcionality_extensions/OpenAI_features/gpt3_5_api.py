import discord
import openai
from discord.ext import commands
from Interfaces.BotFeature import BotFeature
from DB_instances.per_id_db import per_id_db
from ui_components_extension.generic_ui_comps import Generic_View
from dotenv import dotenv_values
config = dotenv_values('.env')

class gpt3_5_api(BotFeature):
    openai_key = config["OPENAI_KEY"]

    GPT_USER_HISTORY = 'gpt_user_history'

    def __init__(self, bot):
        super().__init__(bot)
        openai.api_key = self.openai_key
        
        @bot.tree.command(name='ask_gpt3_5', description='send GPT3.5 a question/message and receive a response') 
        async def ask_GPT3_5_command(interaction : discord.Interaction, message : str):
            if self.openai_key is None:
                await interaction.response.send_message("OpenAI key not found")
                return
            if len(message) > 3500:
                await interaction.response.send_message("message too long, max 3500 characters")
                return
            user_mention = interaction.user.mention
            await interaction.response.send_message("sending to ChatGPT, wait a few seconds for response...", ephemeral=True)
            response = await self.ask_GPT3_5(message, interaction.user.id)
            question_embed = discord.Embed(title=f"Your question:", description=message, color=0x00ff00)
            response_embed = discord.Embed(title=f"GPT3.5\'s response:", description=response, color=0x00ff00)
            embeds=[question_embed, response_embed]
            answer_view = Generic_View()
            answer_view.add_generic_button(label="Show chat history", style=discord.ButtonStyle.primary, callback=self.show_history_button_click)
            await interaction.followup.send(content=user_mention,embeds=embeds, view=answer_view, ephemeral=True)
            return

    async def ask_GPT3_5(self, message, user_id=None):
        if user_id is not None:
            member_db = per_id_db(user_id)
            user_history = member_db.get_param(self.GPT_USER_HISTORY)
            if user_history is None or type(user_history) is not list:
                user_history = []

            user_history.append({"role":"user", "content" : message})
            while(len(str(user_history)) > 3500):
                user_history = user_history[1:]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=user_history
            )
            user_history.append({"role":"assistant", "content" : response["choices"][0]["message"]["content"]})
            if len(user_history) > 10:
                user_history = user_history[1:]
            member_db.set_params(gpt_user_history=user_history)
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user", "content" : message}]
            )
        
        return response["choices"][0]["message"]["content"]
    
    async def show_history_button_click(self, interaction, button, view):
        member_db = per_id_db(interaction.user.id)
        user_history = member_db.get_param(self.GPT_USER_HISTORY)
        if user_history is None or type(user_history) is not list:
            user_history = []
        embeds = []
        i = 0
        if len(user_history) > 10:
            user_history = user_history[-10:]
        for message in user_history:
            if i == 10:
                break
            if message["role"] == "user":
                author = "You"
            else:
                author = "GPT3.5"
            embed = discord.Embed(title=f"{author} said:", description=message["content"], color=0x11ffaa)
            embed.set_footer(text='_________________________________________________________________________')
            embeds.append(embed)
            i += 1
        await interaction.response.edit_message(embeds=embeds, view=None)
        return