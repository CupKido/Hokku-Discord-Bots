from discord.ui import View
import discord
import random
from ui_components_extension.generic_ui_comps import Generic_Button

class minesweeper(View):
    def __init__(self, *, timeout = 600, ephemeral=False):
        super().__init__(timeout=timeout)
        self.ephemeral = ephemeral
        self.game_over = False
        self.flagging = False
        self.board = [[spot(random.randint(0, 11) in [0,1,2] and x*y != 16) for x in range(5)] for y in range(5)]
        self.board[4][4].flag_button = True
        for x in range(5):
            for y in range(5):
                if self.board[x][y].is_bomb:
                    for x2 in range(x-1, x+2):
                        for y2 in range(y-1, y+2):
                            if x2 >= 0 and x2 < 5 and y2 >= 0 and y2 < 5:
                                self.board[x2][y2].add(1)
        for x in range(5):
            for y in range(5):
                print(self.board[x][y].amount, end=' ')
                if x* y != 16:
                    new_button = Generic_Button(emoji='🟦', style=discord.ButtonStyle.grey, callback=self.button_callback, value=(x, y))
                    self.add_item(new_button)
            print()
        
        flag_button = Generic_Button(emoji='🚩', style=discord.ButtonStyle.gray, callback=self.flag_callback)
        self.add_item(flag_button)

    async def button_callback(self, interaction, button, view):
        if self.game_over or self.board[button.value[0]][button.value[1]].is_presented:
            await interaction.response.defer()
            return

        if self.flagging:
            if self.board[button.value[0]][button.value[1]].is_flagged:
                button.emoji = '🟦'
                self.board[button.value[0]][button.value[1]].is_flagged = False
            else:
                button.emoji = '🚩'
                self.board[button.value[0]][button.value[1]].is_flagged = True
        else:
            if self.board[button.value[0]][button.value[1]].is_flagged:
                pass
            elif self.board[button.value[0]][button.value[1]].is_bomb:
                button.emoji = '💣'
                self.game_over = True
            else:
                button.label = str(self.board[button.value[0]][button.value[1]].amount)
                self.board[button.value[0]][button.value[1]].is_presented = True
                button.emoji = None
                # if self.board[button.value[0]][button.value[1]].amount == 0:
                #     for x in range(button.value[0]-1, button.value[0]+2):
                #         for y in range(button.value[1]-1, button.value[1]+2):
                #             if x >= 0 and x < 5 and y >= 0 and y < 5:
                #                 if not self.board[x][y].is_presented:
                #                     await self.button_callback(interaction, view.children[x*5+y-1], view)
        try:
            if not interaction.response.is_done():
                await interaction.response.edit_message(view=view)
        except Exception as e:
            print(e)
        if self.game_over:
            await interaction.followup.send(' :bomb: **Boom** :bomb:  - Game Over!', ephemeral=self.ephemeral)

        for x in range(5):
            for y in range(5):
                if self.board[x][y].is_bomb and not self.board[x][y].is_flagged or \
                not self.board[x][y].is_bomb and self.board[x][y].is_flagged or \
                not self.board[x][y].is_flagged and \
                not self.board[x][y].is_presented and \
                not self.board[x][y].flag_button:
                    return
        self.game_over = True
        await interaction.followup.send('You Win! :partying_face: ', ephemeral=self.ephemeral)

    async def flag_callback(self, interaction, button, view):
        if self.game_over:
            await interaction.response.defer()
            return
        self.flagging = not self.flagging
        button.style = discord.ButtonStyle.green if self.flagging else discord.ButtonStyle.blurple
        await interaction.response.edit_message(view=view)



class spot:
    def __init__(self, is_bomb):
        self.is_bomb = is_bomb
        self.amount = 10 if is_bomb else 0
        self.is_flagged = False
        self.is_presented = False
        self.flag_button = False
    
    def flag(self):
        self.is_flagged = not self.is_flagged
    
    def add(self, amount):
        self.amount += amount