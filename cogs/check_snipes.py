import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker
import asyncio

# USE THIS WHEN NEW USERS ARE ADDED
class CheckSnipes(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def checksnipes(self, ctx):
        beatmaps = await self.database.get_all_beatmaps()
        scores = await self.database.get_scores()
        snipes = await self.database.get_all_snipes()
        main_user = await self.database.get_main_from_discord(ctx.channel.id)
        main_user = main_user[0]
        friends = await self.database.get_user_friends(ctx.channel.id)
        await ctx.send(f"Estimated time to check scores: {round(((((len(beatmaps) * (len(friends) + 1)) * 0.09) / 60)/60), 2)} hours")
        print("checking scores")
        for i, friend in enumerate(friends):
            print("checking next friend...")
            friend_scores = await self.database.get_user_scores_with_zeros(friend[1])
            for j, beatmap in enumerate(beatmaps):
                if j % 100 == 0:
                    print(f"[{i}]   still alive")
                check = True
                for k, score in enumerate(friend_scores):
                    if str(score[1]) == str(beatmap[0]):
                        check = False
                if check == True:# If friend does not have a score saved on the beatmap, get their score and store it
                    friend_score = await self.osu.get_score_data(beatmap[0], friend[1])
                    if friend_score:
                        print(f"adding friend score for {friend_score['score']['user']['username']}")
                        await self.database.add_score(friend[1], beatmap[0], friend_score['score']['score'], 0)
                        await snipe_bot_tracker.add_snipes(friend_score['score'], "checkscore")
                    else:
                        if not(await self.database.get_user_beatmap_play_score(friend[1], beatmap[0], "0")):
                            print(f"adding empty score for friend")
                            await self.database.add_score(friend[1], beatmap[0], 0, 0)

                    # now check the same for the main user
                    if not(await self.database.get_user_beatmap_play_with_zeros(main_user, beatmap[0])):
                        main_user_play = await self.osu.get_score_data(beatmap[0], main_user)
                        if main_user_play:
                            print(f"adding main score for {main_user_play['score']['user']['username']}")
                            await self.database.add_score(main_user, beatmap[0], main_user_play['score']['score'], 0)
                        else:
                            if not(await self.database.get_user_beatmap_play_score(main_user, beatmap[0], "0")):
                            # this will speed it up in the future
                                print(f"adding empty score for main user")
                                await self.database.add_score(main_user, beatmap[0], 0, 0)
        await ctx.send("Score list has been updated successfully")

    @checksnipes.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-checksnipes`') 

def setup(client):
    client.add_cog(CheckSnipes(client))