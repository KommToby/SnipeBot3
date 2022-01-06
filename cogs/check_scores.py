import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker
import asyncio


class CheckScores(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def checkscores(self, ctx):
        beatmaps = await self.database.get_all_beatmaps()
        scores = await self.database.get_scores()
        snipes = await self.database.get_all_snipes()
        main_user = await self.database.get_main_from_discord(ctx.channel.id)
        main_user = main_user[0]
        friends = await self.database.get_user_friends(ctx.channel.id)
        await ctx.send(f"Estimated time to check scores: {round(((((len(beatmaps) * (len(friends) + 1)) * 0.25) / 60)/60), 2)} hours")
        print("checking scores")
        for i, friend in enumerate(friends):
            print("Checking next friend..")
            # note for toby when youre back - its probably better to loop through each map and then through each player instead of each plaeyr
            # and then every map. then you can store everything in an array
            await asyncio.sleep(0.001)
            for i, score in enumerate(scores):
                if i % 100 == 0:
                    await asyncio.sleep(0.1)
                    print(f"[{i}]   still alive")
                check = True
                for snipe in snipes:
                    if str(score[1]) != str(snipe[0]) and check != False and friend[1] != scores[0]: # if map is not in scores but is in snipes
                        check = True
                    else:
                        check = False
                if check == True:
                    if not(await self.database.get_user_beatmap_play_with_zeros(friend[1], score[1])): # if user does not have score saved for beatmap
                        friend_score = await self.osu.get_score_data(score[1], friend[1])
                        if friend_score:
                            print(f"adding friend score for {friend_score['score']['user']['username']}")
                            await self.database.add_score(friend[1], score[1], friend_score['score']['score'], 0)
                            await snipe_bot_tracker.add_snipes(friend_score['score'], "checkscore")
                        else:
                            if not(await self.database.get_user_beatmap_play_score(friend[1], score[1], "0")):
                                print(f"adding empty score for friend")
                                await self.database.add_score(friend[1], score[1], 0, 0)
                # print(f"checking map id {score[1]}")
                if not(await self.database.get_user_beatmap_play_with_zeros(main_user, score[1])):
                    await asyncio.sleep(0.001)
                    main_user_play = await self.osu.get_score_data(score[1], main_user)
                    if main_user_play:
                        print(f"adding main score for {main_user_play['score']['user']['username']}")
                        await self.database.add_score(main_user, score[1], main_user_play['score']['score'], 0)
                    else:
                        if not(await self.database.get_user_beatmap_play_score(main_user, score[1], "0")):
                        # this will speed it up in the future
                            print(f"adding empty score for main user")
                            await self.database.add_score(main_user, score[1], 0, 0)
        await ctx.send("Score list has been updated successfully")

    @checkscores.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-checkdupe`') 

def setup(client):
    client.add_cog(CheckScores(client))