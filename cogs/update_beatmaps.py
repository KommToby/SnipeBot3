import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker
from embed import create_embeds
import random


class Update(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update(self, ctx):
        await ctx.send("ok fine")
        beatmaps = await self.database.get_all_beatmaps()
        for beatmap in beatmaps:
            if beatmap[5] == None or beatmap[6] == None or beatmap[7] == None:
                beatmapdata = await self.osu.get_beatmap(beatmap[0])
                await self.database.update_beatmap_stars(beatmapdata['difficulty_rating'], beatmap[0])
                await self.database.update_beatmap_length(beatmapdata['total_length'], beatmap[0])
                await self.database.update_beatmap_bpm(beatmapdata['bpm'], beatmap[0])
        await ctx.send("beatmaps updated, phew")


def setup(client):
    client.add_cog(Update(client))