import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker
import asyncio


class CheckAllScores(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def checkallscores(self, ctx):
        beatmaps = await self.database.get_all_beatmaps()
        main_users = await self.database.get_all_users()
        beatmaps = await self.database.get_all_beatmaps()
        main_user = await self.database.get_main_from_discord(ctx.channel.id)
        main_user = main_user[0]
        friends = await self.database.get_all_friends()
        print("checking scores")

        ids = []
        for user in main_users:
            if user[1] not in ids:
                ids.append(user[1])
        for friend in friends:
            if friend[1] not in ids:
                ids.append(friend[1])

        await ctx.send(f"This will take around {round( ((len(beatmaps)*len(ids))*0.1)/(60*60), 2)} hours")
        for i, beatmap in enumerate(beatmaps):
            if i >= 16992:
                try:
                    print(f"Checking beatmap {i}/{len(beatmaps)}")
                    for user in ids:
                        play = await self.osu.get_score_data(beatmap[0], user)
                        if play:
                            await asyncio.sleep(1)
                            score = play['score']['score']
                            # if this score is not stored in the database for them
                            if not(await self.database.get_user_beatmap_play_score(user, beatmap[0], score)):
                                print(f"Adding missing score for {play['score']['user']['username']}")
                                await self.database.add_score(user, beatmap[0], score, "0")
                            # if it is already stored, do nothing
                            else:
                                pass
                        else:
                            await asyncio.sleep(0.1)
                            # If they dont have a play on the map and dont have a 0 score stored, add one
                            if not(await self.database.get_user_beatmap_play_with_zeros(user, beatmap[0])):
                                await self.database.add_score(user, beatmap[0], "0", "0")
                except:
                    print("Error. Skipping Beatmap")

        await ctx.send("Score list has been updated successfully")

    @checkallscores.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-checkscores`') 

def setup(client):
    client.add_cog(CheckAllScores(client))