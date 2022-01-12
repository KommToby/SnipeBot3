import discord
from discord.ext import commands
from snipebot import DATABASE, AUTH


class Count(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.Cog.listener() # event within the cog
    async def on_ready(self):
        print('Bot is online.')

    @commands.command() # command within the cog
    async def count(self, ctx, user_name, mapper_name):
        occurences = 0
        user_data = await self.osu.get_user_data(user_name)
        if user_data:
            user_id = str(user_data['id'])
            mapper = await self.database.get_mapper(mapper_name)
            if mapper:
                scores_by_user = await self.database.get_all_scores(user_id)
                beatmaps = await self.database.get_all_beatmaps()
                score_bm_ids = []
                for score in scores_by_user:
                    score_bm_ids.append(score[1])
                for beatmap in beatmaps:
                    if beatmap[0] in score_bm_ids and beatmap[8] == mapper_name:
                            occurences = occurences + 1
                await ctx.send(f"There are `{occurences}` maps hosted by `{mapper_name}` that `{user_name}` has played stored.")
                    
            else:
                await ctx.send(f"Mapper {mapper_name} not found")
        else:
            await ctx.send(f"User {user_name} not found")


def setup(client):
    client.add_cog(Count(client))