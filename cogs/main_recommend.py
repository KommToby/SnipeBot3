import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker
from embed import create_embeds
import random
import numpy as np
import asyncio


class MainRecommend(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    def is_float(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False

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
                    main_user = await self.database.get_main_from_discord(ctx.channel.id)
                    userid = main_user[0]
                    friends = await self.database.get_user_friends(ctx.channel.id)
                    main_user_scores = await self.database.get_all_scores(userid)

                    main_user_beatmaps = []
                    for main_user_score in main_user_scores:
                        if main_user_score[1] not in main_user_beatmaps:
                            # maps that the main user has played
                            main_user_beatmaps.append(main_user_score[1])

                    friend_beatmaps = []
                    friend_and_main_scores = []
                    friend_and_main_beatmaps = []
                    for friend in friends:
                        local_friend_scores = await self.database.get_all_scores(friend[1])
                        for local_friend_score in local_friend_scores:
                            # maps that friends have played that the main user hasnt
                            if local_friend_score[1] not in main_user_beatmaps:
                                friend_beatmaps.append(local_friend_score[1])
                            # maps that both friends and the main user have played
                            if local_friend_score[1] in main_user_beatmaps:
                                friend_and_main_scores.append(local_friend_score)
                        
                        # Only worth checking if there are more than 5 friends who have played said map (efficiency)
                    temp = []
                    maximum = max(friend_beatmaps, key = friend_beatmaps.count)
                    maximum = friend_beatmaps.count(maximum)
                    countmin = round((1/2)*float(maximum))
                    for friend_beatmap in friend_beatmaps:
                        count = friend_beatmaps.count(friend_beatmap)
                        if count > countmin and friend_beatmap not in temp:
                            temp.append(friend_beatmap)
                    friend_beatmaps = []
                    for t in temp:
                        friend_beatmaps.append(t)

                    for friend_and_main_score in friend_and_main_scores:
                        if friend_and_main_score[1] not in friend_and_main_beatmaps:
                            friend_and_main_beatmaps.append(friend_and_main_score[1])

                    # again only worth checking if there are more than 3 friends in this case
                    temp = []
                    for friend_and_main_beatmap in friend_and_main_beatmaps:
                        count = friend_and_main_beatmaps.count(friend_and_main_beatmap)
                        if count > 3 and friend_and_main_beatmap not in temp:
                            temp.append(friend_and_main_beatmap)
                    friend_and_main_beatmaps = []
                    for t in temp:
                        friend_and_main_beatmaps.append(t)

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

                            elif args[1] and args[1].lower() == "-best":

                                # for every score that is stored in the database
                                userid = str(userid)

                                # Checks scores that have the best potential SnipeBack
                                for i, score in enumerate(friend_and_main_beatmaps):
                                    if i % 50 == 0:
                                        await asyncio.sleep(0.01)
                                    beatmap = await self.database.get_beatmap_data(score)
                                    if beatmap not in beatmaps:
                                        beatmaps.append(beatmap)
                                        all_friends = await self.database.get_user_plays_from_beatmap(score)
                                        main_score = await self.database.get_user_beatmap_play_with_zeros(userid, score)
                                        localfriends = []
                                        for friend in all_friends:
                                            if main_score:
                                                if int(friend[3]) > int(main_score[3]) and main_score[3] != '0':
                                                    localfriends.append(friend)
                                                    localfriends.append(friend)
                                                    localfriends.append(friend)
                                        friendnum = len(localfriends)
                                        friends_num.append(friendnum)

                                # Checks scores that have the most potential Snipes (-most)
                                for i, score in enumerate(friend_beatmaps):
                                    if len(friend_beatmaps) > 10:
                                        if i % (round((len(friend_beatmaps))/10)):
                                            await asyncio.sleep(0.01)
                                    beatmap = await self.database.get_beatmap_data(score)
                                    if beatmap not in beatmaps:
                                        beatmaps.append(beatmap)
                                        all_friends = await self.database.get_user_plays_from_beatmap(score)
                                        localfriends = []
                                        for friend in all_friends:
                                            localfriends.append(friend)
                                            localfriends.append(friend)
                                        friendnum = len(localfriends)
                                        friends_num.append(friendnum)
                                
                                links = []
                                beatmap_strings = []
                                for i in range(0,9):
                                    if friends_num != []:
                                        maxvalue = max(friends_num)
                                        index = friends_num.index(maxvalue)
                                        beatmap = beatmaps[index]
                                        beatmap_strings.append(f"{beatmap[2]} [{beatmap[3]}]")
                                        links.append(beatmap[4])
                                        friends_num.remove(maxvalue)
                                        beatmaps.remove(beatmaps[index])
                                embed = await create_embeds.create_recommendation_embed("bestnum", user_data, beatmap_strings, links)
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

                                            links = []
                                            beatmap_strings = []
                                            if len(args) < 4:
                                                pass
                                            else:
                                                if args[3].lower() == "-min":
                                                    if len(args) < 5:
                                                        pass
                                                    else:
                                                        if self.is_float(args[4]):
                                                            beatmaps, links = self.sort_min(beatmaps, args[4], links)
                                                        else:
                                                            pass
                                                elif args[3].lower() == "-max":
                                                    if len(args) < 5:
                                                        pass
                                                    else:
                                                        if self.is_float(args[4]):
                                                            beatmaps, links = self.sort_max(beatmaps, args[4], links)
                                                        else:
                                                            pass
                                            new_links = []
                                            for i in range(0,9):
                                                if beatmaps != []:
                                                    # index = random.randint(0, len(friend_list)-1) not sure if this stuff is required for non minmax stuff so i commented it out
                                                    # beatmap = beatmaps[index]
                                                    # beatmap_strings.append(f"{beatmap[2]} [{beatmap[3]}]")
                                                    # links.append(beatmap[4])
                                                    # friend_list.remove(friend_list[index])
                                                    # beatmaps.remove(beatmaps[index])
                                                    index = random.randint(0, len(beatmaps)-1)
                                                    beatmap = beatmaps[index]
                                                    beatmap_strings.append(f"{beatmap[2]} [{beatmap[3]}]")
                                                    new_links.append(beatmap[4])
                                                    beatmaps.remove(beatmap)
                                            embed = await create_embeds.create_recommendation_embed("playernum", user_data, beatmap_strings, new_links)
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

    def sort_max(self, beatmaps, max, links):
        sorted_beatmaps = []
        sorted_links = []
        for i, beatmap in enumerate(beatmaps):
            if beatmap[5] > float(max):
                pass
            else:
                sorted_beatmaps.append(beatmap)
                sorted_links.append(beatmap[4])
        return sorted_beatmaps, sorted_links

    def sort_min(self, beatmaps, min, links):
        sorted_beatmaps = []
        sorted_links = []
        for i, beatmap in enumerate(beatmaps):
            if beatmap[5] < float(min):
                pass
            else:
                sorted_beatmaps.append(beatmap)
                sorted_links.append(beatmap[4])
        return sorted_beatmaps, sorted_links

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