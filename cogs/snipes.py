import discord
from discord.ext import commands
from embed.create_embeds import create_snipes_embed
from snipebot import DATABASE, AUTH

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
        embed = await create_snipes_embed(user_data, snipes, sniped)
        await ctx.send(embed=embed)

    @snipes.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-snipes "username"`')    

def setup(client):
    client.add_cog(Snipes(client))