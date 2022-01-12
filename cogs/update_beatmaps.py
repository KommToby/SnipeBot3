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
        self.snipebot = snipe_bot_tracker

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update(self, ctx):
        await ctx.send("ok fine")
        beatmaps = open("beatmaps.txt", "r")
        all_beatmaps = await self.database.get_all_beatmaps()
        # for line in beatmaps:
        #     stripped_line = line.strip()
        #     stripped_line = stripped_line.replace("/n", "")
        #     in_beatmaps = False
        #     for beatmap in all_beatmaps:
        #         if str(stripped_line) ==  beatmap[0]:
        #             in_beatmaps = True
        #     if in_beatmaps == False:
        #         await self.snipebot.check_specific_beatmap(stripped_line)
        #     else:
        #         print(f"Skipping {stripped_line} as its already stored")
        for beatmap in all_beatmaps:
            bm = None
            if beatmap[8] is None:
                bm = await self.osu.get_beatmap(beatmap[0])
                await self.database.update_mapper(bm['id'], bm['beatmapset']['creator'])
            if beatmap[9] is None:
                if bm is None:
                    bm = await self.osu.get_beatmap(beatmap[0])
                await self.database.update_beatmapset_id(bm['id'], bm['beatmapset']['id'])

        await ctx.send("beatmaps updated, phew")


def setup(client):
    client.add_cog(Update(client))