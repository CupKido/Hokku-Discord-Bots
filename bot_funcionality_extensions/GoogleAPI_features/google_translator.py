import discord 
import googletrans
from googletrans import Translator
from Interfaces.BotFeature import BotFeature

class google_translator(BotFeature):
    def __init__(self, bot):
        super().__init__(bot)
        self.languages = self.flip_dict(googletrans.LANGUAGES)
        @bot.tree.command(name="translate", description="Translate text")
        async def translate(interaction: discord.Interaction, text: str, target_language: str = "english"):
            translator = Translator()
            result = translator.translate(text, dest=self.get_letters_from_language(target_language))
            await interaction.response.send_message(result.text, ephemeral=True)
        
    def get_letters_from_language(self, language):
        if language in self.languages.keys():
            return self.languages[language.lower()]
        for key, value in self.languages.items():
            if key.startswith(language.lower()):
                return value
    def flip_dict(self, dict):
        return {v: k for k, v in dict.items()}