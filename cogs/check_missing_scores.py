import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker
import asyncio


class CheckMissingScores(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def checkmissingscores(self, ctx):
        beatmaps = await self.database.get_all_beatmaps()
        scores = await self.database.get_scores()
        snipes = await self.database.get_all_snipes()
        beatmaps = await self.database.get_all_beatmaps()
        main_user = await self.database.get_main_from_discord(ctx.channel.id)
        main_user = main_user[0]
        main_user_scores_only_zero = await self.database.get_user_scores_only_zeros(main_user)
        main_user_scores_no_zero = await self.database.get_all_scores(main_user)
        friends = await self.database.get_user_friends(ctx.channel.id)
        all_friends = await self.database.get_all_friends()
        print("checking scores")
        
        user_beatmaps = []
        for score in main_user_scores_no_zero:
            if score[1] not in user_beatmaps:
                user_beatmaps.append(score[1])

        user_zeros = []
        for score in main_user_scores_only_zero:
            if score[1] not in user_zeros:
                user_zeros.append(score[1])

        all_beatmaps = []
        for beatmap in beatmaps:
            if beatmap not in all_beatmaps:
                if beatmap[0] not in user_zeros:
                    all_beatmaps.append(beatmap[0])

        await ctx.send(f"Estimated time to check scores is around: {round((((len(all_beatmaps)-len(user_beatmaps))*0.2*len(all_friends))/(60*60)), 2)} hours but ngl who knows")

        for beatmap in all_beatmaps:
            print(f"Checking {beatmap}")
            if beatmap not in user_beatmaps:
                user_play = await self.osu.get_score_data(beatmap, main_user)
                if user_play:
                    print(f"adding main score for {user_play['score']['user']['username']}")
                    await self.database.add_score(main_user, score[1], user_play['score']['score'], 0)
                    await snipe_bot_tracker.add_snipes(user_play['score'], "checkscore")
                else:
                    print(f"adding empty score for main user")
                    await self.database.add_score(main_user, score[1], 0, 0)
        await ctx.send("Score list has been updated successfully")

    @checkmissingscores.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-checkscores`') 

def setup(client):
    client.add_cog(CheckMissingScores(client))