import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker


class CheckBeatmap(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def checkbeatmap(self, ctx, id : str):
        await ctx.send("Checking Beatmap..")
        await snipe_bot_tracker.check_specific_beatmap(id)
        await ctx.send(f"Beatmap {id} checked successfully")

    @checkbeatmap.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-checkbeatmap "beatmapid"`') 

def setup(client):
    client.add_cog(CheckBeatmap(client))