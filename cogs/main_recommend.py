import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker
from embed import create_embeds
import random


class MainRecommend(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command(aliases=['mr'])
    @commands.has_permissions(administrator=True)
    async def main_recommend(self, ctx, user_id : str):
        user_data = await self.osu.get_user_data(user_id)
        userid = user_data['id']
        beatmaps = []
        links = []
        friends = []
        if user_data:
            all_scores = self.database.get_scores()
            main_scores = self.database.get_all_scores(userid)
            for score in all_scores:
                add = True
                for main_score in main_scores:
                    if main_score[1] != score[1] and add is not False:
                        add = True
                    else:
                        add = False
                if add is True:
                    if not(self.database.get_user_beatmap_play(userid, score[1])):
                        beatmap = self.database.get_beatmap_data(score[1])
                        if beatmap[4] not in links:
                            beatmaps.append(f"{beatmap[1]} - {beatmap[2]} [{beatmap[3]}]")
                            links.append(beatmap[4])
                            friends.append(score[0])
            if len(beatmaps) > 0:
                index = random.randint(0, len(beatmaps)-1)
                frienddata = await self.osu.get_user_data(friends[index])
                friend_name = frienddata['username']
                embed = await create_embeds.create_recommendation_embed(beatmaps, user_data, links, ctx, friend_name, index)
                await ctx.send(embed=embed)
            else:
                await ctx.send("No recommendations at this time. Play some more maps and try again later.")



    @main_recommend.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-recommend "username"`') 

def setup(client):
    client.add_cog(MainRecommend(client))