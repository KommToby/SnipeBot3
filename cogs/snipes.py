import discord
from discord.ext import commands
from embed.create_embeds import create_snipes_embed
from snipebot import DATABASE, AUTH
import random

class Snipes(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command(aliases=['s'])
    async def snipes(self, ctx, user: str):
        main_user_id = self.database.get_main_from_discord(ctx.channel.id)
        main_user_id = main_user_id[0]
        user_data = await self.osu.get_user_data(user)
        snipes = self.database.get_user_snipes(str(user_data['id']), main_user_id)
        sniped = self.database.get_user_snipes(main_user_id, str(user_data['id']))
        total_snipes = self.database.get_total_snipes(main_user_id)
        user_snipes = self.database.get_user_snipes(user_data['id'], main_user_id)
        random_play_index = random.randint(0, len(user_snipes)-1)
        random_play = user_snipes[random_play_index]
        random_play_data = await self.osu.get_score_data(random_play[1], random_play[0])
        embed = await create_snipes_embed(user_data, snipes, sniped, total_snipes, random_play_data)
        await ctx.send(embed=embed)

    @snipes.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-snipes "username"`')    

def setup(client):
    client.add_cog(Snipes(client))