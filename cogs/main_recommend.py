import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker
from embed import create_embeds
import random
import numpy as np


class MainRecommend(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command(aliases=['mr'])
    @commands.has_permissions(administrator=True)
    async def main_recommend(self, ctx, *args):
        if not args:
            await ctx.send('Usage: `main_recommend "username" -[most/player]`') 
        else:
            # Gets the main users data
            user_data = await self.osu.get_user_data(args[0])
            if user_data:
                # Initialise variables
                userid = user_data['id']
                beatmaps = []
                friends = []
                friends_num = []
                # If the user exists on osu
                if user_data:

                    # I think the previous method was just to check scores that their friends have
                    friends = await self.database.get_user_friends(userid)
                    main_user_scores = await self.database.get_all_scores(userid)

                    main_user_beatmaps = []
                    for main_user_score in main_user_scores:
                        if main_user_score[1] not in main_user_beatmaps:
                            main_user_beatmaps.append(main_user_score[1])

                    friend_beatmaps = []
                    for friend in friends:
                        local_friend_scores = await self.database.get_all_scores(friend[1])
                        for local_friend_score in local_friend_scores:
                            if local_friend_score[1] not in friend_beatmaps and local_friend_score[1] not in main_user_beatmaps:
                                friend_beatmaps.append(local_friend_score[1])

                    if len(friend_beatmaps) > 0:
                        if len(args) > 1:
                            if args[1] and args[1].lower() == "-most":

                                # for every score that is stored in the database
                                userid = str(userid)
                                for i, score in enumerate(friend_beatmaps):
                                    beatmap = await self.database.get_beatmap_data(score)
                                    if beatmap not in beatmaps:
                                        beatmaps.append(beatmap)
                                        all_friends = await self.database.get_user_plays_from_beatmap(score)
                                        localfriends = []
                                        for friend in all_friends:
                                            localfriends.append(friend)
                                        friendnum = len(localfriends)
                                        friends_num.append(friendnum)
                                maxvalue = max(friends_num)
                                index = friends_num.index(maxvalue)
                                beatmap = beatmaps[index]
                                beatmap_string = f"{beatmap[2]} [{beatmap[3]}]"
                                embed = await create_embeds.create_recommendation_embed("largestnum", user_data, beatmap_string, beatmap[4])
                                await ctx.send(embed=embed)

                            elif args[1] and args[1].lower() == "-player":
                                if not args[2]:
                                    await ctx.send('Usage: `main_recommend "username" -player "playername') 
                                else:
                                    friend_data = await self.osu.get_user_data(args[2])
                                    if friend_data:
                                        single_friend_beatmaps = []
                                        local_single_friend_scores = await self.database.get_all_scores(str(friend_data['id']))
                                        for local_single_friend_score in local_single_friend_scores:
                                            if local_single_friend_score[1] not in single_friend_beatmaps and local_single_friend_score[1] not in main_user_beatmaps:
                                                single_friend_beatmaps.append(local_single_friend_score[1])
                                        friend_list = single_friend_beatmaps

                                        if friend_list != []:
                                            beatmaps = []
                                            for _, score in enumerate(friend_list):
                                                beatmap = await self.database.get_beatmap_data(score)
                                                if beatmap not in beatmaps:
                                                    beatmaps.append(beatmap)

                                            index = random.randint(0, len(friend_list)-1)
                                            friend_name = friend_data['username']
                                            beatmap = beatmaps[index]
                                            beatmap_string = f"{beatmap[2]} [{beatmap[3]}]"
                                            embed = await create_embeds.create_recommendation_embed(friend_name, user_data, beatmap_string, beatmap[4])
                                            await ctx.send(embed=embed)
                                        else:
                                            all_friends = await self.database.get_all_friends()
                                            friendcheck = False
                                            for f in all_friends:
                                                if str(friend_data['id']) == f[1]:
                                                    friendcheck = True
                                            if friendcheck == True:
                                                await ctx.send(f'You have played all scanned beatmaps that `{args[2]}` has played.') 
                                            else:
                                                await ctx.send(f'`{args[2]}` is not a friend.') 
                                    else:
                                        await ctx.send(f'User `{args[2]}` not found.') 

                        else:
                            beatmaps = []
                            for i, score in enumerate(friend_beatmaps):
                                beatmap = await self.database.get_beatmap_data(score)
                                if beatmap not in beatmaps:
                                    beatmaps.append(beatmap)
                            index = random.randint(0, len(beatmaps)-1)
                            beatmap = beatmaps[index]
                            beatmap_string = f"{beatmap[2]} [{beatmap[3]}]"
                            embed = await create_embeds.create_recommendation_embed("a friend", user_data, beatmap_string, beatmap[4])
                            await ctx.send(embed=embed)
                    else:
                        await ctx.send("No recommendations at this time. Play some more maps and try again later.")


    @main_recommend.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-recommend "username"`') 

    @main_recommend.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('You do not have permissions for -mr (main user only)') 

def setup(client):
    client.add_cog(MainRecommend(client))