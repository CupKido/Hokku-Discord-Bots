import discord
from discord.ext import commands
from Interfaces.BotFeature import BotFeature
from ui_components_extension.generic_ui_comps import Generic_View, Generic_Modal
from ui_components_extension import ui_tools
from DB_instances.per_id_db import per_id_db
import datetime
from datetime import timedelta

class to_do_list(BotFeature):
    TASKS_LIST = 'tasks_list'
    IS_EMBED = 'is_embed'

    def __init__(self, bot):
        super().__init__(bot)

        @bot.tree.command(name='add_task', description='add task to the list')
        async def add_task(interaction):
            this_user_db = per_id_db(interaction.user.id)
            tasks_list = this_user_db.get_param(self.TASKS_LIST)
            if tasks_list is not None and len(tasks_list) == 25:
                await interaction.response.send_message('You have reached the maximum number of tasks (25)', ephemeral=True)
                return

            await self.show_add_task_modal(interaction)

        @bot.tree.command(name='show_tasks', description='show tasks list')
        async def show_tasks(interaction):
            this_user_db = per_id_db(interaction.user.id)
            tasks_list = this_user_db.get_param(self.TASKS_LIST)
            is_embed = this_user_db.get_param(self.IS_EMBED)
            if tasks_list is None:
                tasks_list = []

            tasks_menu_view = self.get_tasks_menu_view(tasks_list)

            if is_embed is None:
                is_embed = True
            if is_embed:
                embeds = self.get_tasks_embeds(tasks_list)
                await interaction.response.send_message(embeds=embeds, view=tasks_menu_view, ephemeral=True)
            else:
                message = self.get_tasks_string(tasks_list)
                await interaction.response.send_message(content=message, view=tasks_menu_view, ephemeral=True)
                
        @bot.tree.command(name='is_to_do_list_embed', description='set if to do list will be sent as embed')
        async def is_to_do_list_embed(interaction, is_embed : bool):
            this_user_db = per_id_db(interaction.user.id)
            this_user_db.set_params(is_embed=is_embed)
            await interaction.response.send_message('To Do list was set as ' + ('Embed' if is_embed else 'Not Embed'), ephemeral=True)


    def get_new_task_modal(self):
        this_modal = Generic_Modal(title='Add new task')
        this_modal.add_input(label = 'Enter task name:', placeholder='task Name', long=False, required=True)
        this_modal.add_input(label = 'Enter task description:', placeholder='task description', long=True, required=False)
        this_modal.add_input(label = 'Enter days untill task end:', placeholder='example: 3', long=False, required=False)
        this_modal.set_callback(self.add_task)
        return this_modal
    
    def get_tasks_menu_view(self, tasks_list):
        my_view = Generic_View()
        my_view.add_generic_button(label=' Add', emoji='➕', style=discord.ButtonStyle.green, callback=self.add_task_button_click)
        if len(tasks_list) > 0:
            my_view.add_generic_button(label=' Delete', emoji='➖', style=discord.ButtonStyle.red, callback=self.delete_task_button_click)
            my_view.add_generic_button(label=' Complete', emoji='✔️', style=discord.ButtonStyle.blurple, callback=self.complete_task_button_click)
            options = [{'label' : tasks_list[x]['name'], 'description': tasks_list[x]['description'], 'value' : str(x)} for x in range(len(tasks_list))]
            my_view.add_generic_select(placeholder='Select task', options=options, min_values=1, max_values=1, callback=self.select_task)
            my_view.add_generic_button(label=' To top', emoji='☝️', style=discord.ButtonStyle.blurple, callback=self.move_to_top_button_click)
            my_view.add_generic_button(label=' To bottom', emoji='👇', style=discord.ButtonStyle.blurple, callback=self.move_to_bottom_button_click)
        return my_view

    async def add_task_button_click(self, interaction, button, view):
        await self.show_add_task_modal(interaction)

    async def delete_task_button_click(self, interaction, button, view):
        if len(view.children[3].values) == 0:
            await interaction.response.send_message('Please select a task', ephemeral=True)
            return
        this_user_db = per_id_db(interaction.user.id)
        tasks_list = this_user_db.get_param(self.TASKS_LIST)
        if tasks_list is None:
            tasks_list = []
        selected_task_index = int(view.children[3].values[0])
        tasks_list.pop(selected_task_index)
        await self.update_show_tasks(interaction, tasks_list)
        this_user_db.set_params(tasks_list=tasks_list)

    async def complete_task_button_click(self, interaction, button, view):
        if len(view.children[3].values) == 0:
            await interaction.response.send_message('Please select a task', ephemeral=True)
            return
        this_user_db = per_id_db(interaction.user.id)
        tasks_list = this_user_db.get_param(self.TASKS_LIST)
        if tasks_list is None:
            tasks_list = []
        selected_task_index = int(view.children[3].values[0])
        tasks_list[selected_task_index]['is_done'] = True
        await self.update_show_tasks(interaction, tasks_list)
        this_user_db.set_params(tasks_list=tasks_list)

    async def move_to_top_button_click(self, interaction, button, view):
        if len(view.children[3].values) == 0:
            await interaction.response.send_message('Please select a task', ephemeral=True)
            return
        this_user_db = per_id_db(interaction.user.id)
        tasks_list = this_user_db.get_param(self.TASKS_LIST)
        if tasks_list is None:
            tasks_list = []
        selected_task_index = int(view.children[3].values[0])
        tasks_list.insert(0, tasks_list.pop(selected_task_index))
        await self.update_show_tasks(interaction, tasks_list)
        this_user_db.set_params(tasks_list=tasks_list)

    async def move_to_bottom_button_click(self, interaction, button, view):
        if len(view.children[3].values) == 0:
            await interaction.response.send_message('Please select a task', ephemeral=True)
            return
        this_user_db = per_id_db(interaction.user.id)
        tasks_list = this_user_db.get_param(self.TASKS_LIST)
        if tasks_list is None:
            tasks_list = []
        selected_task_index = int(view.children[3].values[0])
        tasks_list.append(tasks_list.pop(selected_task_index))
        await self.update_show_tasks(interaction, tasks_list)
        this_user_db.set_params(tasks_list=tasks_list)

    def get_tasks_string(self, tasks_list):
        res_msg = 'To Do list:\n'
        for x in range(len(tasks_list)):
            task = tasks_list[x]
            res_msg += '\n\t' + str(x+1) + '.\n\t**' + task['name'] + '**'
            if task['year'] != -1:
                res_msg += '\t|\tDue to ' + str(task['year']) + '/' + str(task['month']) + '/' + str(task['day'])
            res_msg += (('\n\t*' + task['description'] + '*') if task['description'] != '' else '')
            res_msg += '\n\tcompleted: ' + ('Yes' if task['is_done'] else 'No')
            # if date is after today, send 'late: yes'
            if task['year'] != -1:
                task_date = datetime.datetime(task['year'], task['month'], task['day'])
                if task_date < datetime.datetime.now() and not task['is_done']:
                    res_msg += '\t|\tLate: Yes'
                else:
                    res_msg += '\t|\tLate: No'
            res_msg += '\n'
        return res_msg

    def get_tasks_embeds(self, tasks_list):
        res_embeds = []
        res_embeds.append(discord.Embed(title='To Do list:', color=0x0000ff))
        for x in range(len(tasks_list)):
            task = tasks_list[x]
            res_embeds.append(self.get_embed_for_task(task, x))
        return res_embeds

    def get_embed_for_task(self, task, index):
        if task['year'] != -1:
            task_date = datetime.datetime(task['year'], task['month'], task['day'])
        # calculate color based on task status
        if task['is_done']:
            color = 0x009900
        elif task['year'] != -1:
            if task_date < datetime.datetime.now():
                # is late
                color = 0xff0000
            else:
                color = 0x80ff80
        else:
            color = 0x80ff80

        embed = discord.Embed(title=task['name'], description=task['description'], color=color)
        embed.set_author(name=str(index+1))
        if task['year'] != -1:
            embed.add_field(name='Due to', value=str(task['year']) + '/' + str(task['month']) + '/' + str(task['day']), inline=False)
        embed.add_field(name='Completed', value='Yes' if task['is_done'] else 'No', inline=False)
        if task['year'] != -1:
            embed.add_field(name='Late', value='Yes' if task_date < datetime.datetime.now() and not task['is_done'] else 'No', inline=False)
        embed.set_footer(text='________________________________________________________________')
        return embed

    async def update_show_tasks(self, interaction, tasks_list):
        this_user_db = per_id_db(interaction.user.id)
        is_embed = this_user_db.get_param(self.IS_EMBED)
        
        tasks_menu_view = self.get_tasks_menu_view(tasks_list)

        if is_embed is None:
            is_embed = True
        if is_embed:
            embeds = self.get_tasks_embeds(tasks_list)
            await interaction.response.edit_message(embeds=embeds, view=tasks_menu_view)
        else:
            message = self.get_tasks_string(tasks_list)
            await interaction.response.edit_message(content=message, view=tasks_menu_view)

    async def show_add_task_modal(self, interaction):
        this_modal = self.get_new_task_modal()
        await interaction.response.send_modal(this_modal)

    async def add_task(self, interaction):
        task_name = ui_tools.get_modal_value(interaction, 0)
        task_description = ui_tools.get_modal_value(interaction, 1)
        task_days = ui_tools.get_modal_value(interaction, 2)
        if task_days != "":
            try:
                task_days = int(task_days)
            except:
                task_days = None
        else:
            task_days = None
        this_user_db = per_id_db(interaction.user.id)
        tasks_list = this_user_db.get_param(self.TASKS_LIST)
        if tasks_list is None:
            tasks_list = []
        

        # calculate the date
        if task_days == None:
            task = {'name' : task_name, 'description' : task_description, 'year' : -1, 'month' : -1, 'day' : -1, 'is_done' : False}
        else:
            task_date = datetime.datetime.now() + timedelta(days=task_days)
            task = {'name' : task_name, 'description' : task_description, 'year' : task_date.year, 'month' : task_date.month, 'day' : task_date.day, 'is_done' : False}
        tasks_list.append(task)
        if interaction.message is not None:
            await self.update_show_tasks(interaction, tasks_list)
        else:
            await interaction.response.send_message('added task: ' + task_name, ephemeral=True)
        this_user_db.set_params(tasks_list=tasks_list)

    async def select_task(self, interaction, select, view):
        await interaction.response.defer()