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
        if user_id == "Komm2":
            user_data = await self.osu.get_user_data(user_id[:-1])
        else:
            user_data = await self.osu.get_user_data(user_id)
        if user_data:
            userid = user_data['id']
            beatmaps = []
            links = []
            friends = []
            friends_num = []
            if user_data:
                all_scores = self.database.get_scores()
                main_scores = self.database.get_all_scores(userid)
                for score in all_scores:
                    add = True
                    for main_score in main_scores:
                        if main_score[1] != score[1] and add is not False:
                            add = True
                        else:
                            if str(main_score[2]) != "0":
                                add = False
                            else:
                                add = True
                    if add is True:
                        if not(self.database.get_user_beatmap_play(userid, score[1])):
                            beatmap = self.database.get_beatmap_data(score[1])
                            if beatmap[4] not in links:
                                beatmaps.append(f"{beatmap[1]} - {beatmap[2]} [{beatmap[3]}]")
                                links.append(beatmap[4])
                                friends.append(score[0])
                                all_friends = self.database.get_user_plays_from_beatmap(score[1])
                                localfriends = []
                                for friend in all_friends:
                                    localfriends.append(friend[0])
                                friendnum = len(localfriends)
                                friends_num.append(friendnum)
                        else:
                            post2 = True
                            if self.database.get_user_beatmap_play_score(userid, score[1], '0'):
                                plays = self.database.get_user_beatmap_plays(userid, score[1])
                                for play in plays:
                                    if play[2] != "0":
                                        post2 = False
                                if post2 is True:
                                    beatmap = self.database.get_beatmap_data(score[1])
                                    if beatmap[4] not in links:
                                        beatmaps.append(f"{beatmap[1]} - {beatmap[2]} [{beatmap[3]}]")
                                        links.append(beatmap[4])
                                        friends.append(score[0])
                                        all_friends = self.database.get_user_plays_from_beatmap(score[1])
                                        localfriends = []
                                        for friend in all_friends:
                                            localfriends.append(friend[0])
                                        friendnum = len(localfriends)
                                        friends_num.append(friendnum)

                if len(beatmaps) > 0:
                    if user_id == "Komm2":
                        maxvalue = max(friends_num)
                        index = friends_num.index(maxvalue)
                        embed = await create_embeds.create_recommendation_embed(beatmaps[index], user_data, links, ctx, "largestnum", index)
                        await ctx.send(embed=embed)
                    else:
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