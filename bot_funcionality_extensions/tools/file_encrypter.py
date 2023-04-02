import discord
from discord.ext import commands
from Interfaces.BotFeature import BotFeature
import os
import zipfile 
import hashlib
from Crypto.Cipher import AES


class file_encrypter(BotFeature):

    encrypted_extension = '.cke'
    delete_messages_amount = 5
    def __init__(self, bot):
        super().__init__(bot)
        bot.add_on_message_callback(self.handle_message)
        @bot.tree.command(name="delete_last" + str(self.delete_messages_amount) + "_messages", description="If used on DM, deletes the last messages sent by the bot")
        async def delete_last_message(interaction):
            if interaction.channel.type == discord.ChannelType.private:
                deleted_count = 0
                async for message in interaction.channel.history(limit=100):
                    if message.author == self.bot_client.user:
                        await message.delete()
                        deleted_count += 1
                    if deleted_count == self.delete_messages_amount:
                        break
                    print(deleted_count)  
                embed= discord.Embed(title='**Deleted ' + str(deleted_count) + ' messages**', color=0x00ff00)
            else:
                embed = discord.Embed(title='**This command can only be used in DMs!**', color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True) 


    async def handle_message(self, message):
        if message.author == self.bot_client.user:
            return
        files_dir = 'data_base/file_encrypter_files/' + str(message.author.id)
        if not os.path.exists(files_dir):
            os.makedirs(files_dir)
        # encrypt files
        if message.content.startswith(self.bot_client.command_prefix + ' encrypt'):
            # make sure password is provided
            message_parts = message.content.split(' ')
            prefix_message_parts = (self.bot_client.command_prefix + ' encrypt').split(' ')
            if len(message_parts) <= len(prefix_message_parts) or message_parts[len(prefix_message_parts):] == []:
                await message.reply('Please provide a password by using this syntax:\n' + self.bot_client.command_prefix + ' encrypt <password>')
                return
            # get password
            users_password = ' '.join(message_parts[len(prefix_message_parts):])
            # encrypt and send files
            for file in  message.attachments:
                file_path = os.path.join(files_dir,  file.filename)
                await self.save_file(file, file_path)
                try:
                    new_file_path = self.encrypt_file(file_path, users_password)
                    ready_embed = discord.Embed(title='**Encrypted file is ready for:** ' + file.filename, description='Your file is ready to be downloaded', color=0x00ff00)
                    await message.author.send(embed=ready_embed, file=discord.File(new_file_path))
                    os.remove(new_file_path)
                except Exception as e:
                    print(e)
                    await message.author.send(embed=discord.Embed(title='**Error encrypting file**: ' + file.filename))
                    os.remove(file_path)
                    return
        # decrypt files
        elif message.content.startswith(self.bot_client.command_prefix + ' decrypt'):
            # make sure password is provided
            message_parts = message.content.split(' ')
            prefix_message_parts = (self.bot_client.command_prefix + ' decrypt').split(' ')
            if len(message_parts) <= len(prefix_message_parts) or message_parts[len(prefix_message_parts):] == []:
                await message.reply('Please provide a password by using this syntax:\n' + self.bot_client.command_prefix + ' decrypt <password>')
                return
            # get password
            users_password = ' '.join(message_parts[len(prefix_message_parts):])
            # decrypt and send files
            for file in message.attachments:
                file_path = os.path.join(files_dir,  file.filename)
                await self.save_file(file, file_path)
                try:
                    new_file_path = self.decrypt_file(file_path, users_password)
                    ready_embed = discord.Embed(title='**Decrypted file is ready for:** ' + file.filename, description='Your file is ready to be downloaded', color=0x00ff00)
                    await message.author.send(embed=ready_embed, file=discord.File(new_file_path))
                    os.remove(new_file_path)
                except Exception as e:
                    print(e)
                    await message.author.send(embed=discord.Embed(title='**Error decrypting file**: ' + file.filename))
                    os.remove(file_path)
                    return

        
    def encrypt_file(self, file_path, password):
    # Hash password using SHA-256
        password_hash = hashlib.sha256(password.encode()).digest()

        # Generate 256-bit AES key from hashed password
        key = password_hash[:32]

        # Initialize AES cipher
        cipher = AES.new(key, AES.MODE_EAX)

        # Encrypt and decrypt file using the key
        with open(file_path, 'rb') as f:
            plaintext = f.read()

        # Encrypt plaintext
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        os.remove(file_path)
        # Save encrypted file
        parent_dir = os.path.dirname(file_path)
        # get name of zip file
        file_name = os.path.basename(file_path)


        with open(parent_dir + '/' + file_name + self.encrypted_extension, 'wb+') as f:
            [f.write(x) for x in (cipher.nonce, tag, ciphertext)]
        return parent_dir + '/' + file_name  + self.encrypted_extension
    
    def decrypt_file(self, file_path, password):
        # Hash password using SHA-256
        password_hash = hashlib.sha256(password.encode()).digest()

        # Generate 256-bit AES key from hashed password
        key = password_hash[:32]

        # Initialize AES cipher
        cipher = AES.new(key, AES.MODE_EAX)
        # Decrypt file
        with open(file_path, 'rb') as f:
            nonce, tag, ciphertext = [f.read(x) for x in (16, 16, -1)]

        # Initialize cipher using the same key and nonce
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

        # Verify tag and decrypt ciphertext
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        os.remove(file_path)
        # Save decrypted file
        parent_dir = os.path.dirname(file_path)
        # get name of encrypted file

        file_name = os.path.basename(file_path)
        if file_name.endswith(self.encrypted_extension):
            file_name = '.'.join(file_name.split('.')[:-1])
        with open(parent_dir + '/' + file_name, 'wb+') as f:
            f.write(plaintext)
        return parent_dir + '/' + file_name


    async def save_file(self, file, file_path):
        with open(file_path, 'wb+') as f:
            f.write(await file.read())