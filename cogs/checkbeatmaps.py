import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker
import asyncio


class CheckBeatmaps(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def checkbeatmaps(self, ctx):
        counter = 0
        beatmaps = self.database.get_all_beatmaps()
        for beatmap in beatmaps:
            if not(self.database.get_scores_from_beatmap(beatmap[0])):
                counter += 1
        await ctx.send(f"Removed {counter} beatmaps that were unused")

    @checkbeatmaps.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-checkdupe`') 

def setup(client):
    client.add_cog(CheckBeatmaps(client))