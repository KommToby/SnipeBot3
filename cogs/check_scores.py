import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker


class CheckScores(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def checkscores(self, ctx):
        scores = self.database.get_scores()
        snipes = self.database.get_all_snipes()
        main_user = self.database.get_main_from_discord(ctx.channel.id)
        main_user = main_user[0]
        friends = self.database.get_user_friends(main_user)
        print("checking scores")
        for i, friend in enumerate(friends):
            for score in scores:
                check = True
                for snipe in snipes:
                    if str(score[1]) != str(snipe[0]) and check != False and friend[1] != scores[0]: # if map is not in scores but is in snipes
                        check = True
                    else:
                        check = False
                if check == True and i > 21:
                    print(f"checking map id {score[1]}")
                    if not(self.database.get_user_beatmap_play(friend[1], score[1])): # if user does not have score saved for beatmap
                        friend_score = await self.osu.get_score_data(score[1], friend[1])
                        if friend_score:
                            print(f"adding friend score for {friend_score['score']['user']['username']}")
                            self.database.add_score(friend[1], score[1], friend_score['score']['score'], 0)
            if not(self.database.get_user_beatmap_play(main_user, score[1])):
                main_user_play = await self.osu.get_score_data(score[1], main_user)
                if main_user_play:
                    print(f"adding main score for {main_user_play['score']['user']['username']}")
                    self.database.add_score(main_user, score[1], main_user_play['score']['score'], 0)
        await ctx.send("Score list has been updated successfully")

    @checkscores.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-checkdupe`') 

def setup(client):
    client.add_cog(CheckScores(client))