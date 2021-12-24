import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker


class CheckDupe(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def checkdupe(self, ctx):
        occurences = 0
        second_occurences = 0
        snipes = await self.database.get_all_snipes()
        scores = await self.database.get_scores()

        async def run_snipes(snipes, occurences):
            scanned_snipes = []
            for i, snipe in enumerate(snipes):
                if snipe not in scanned_snipes:
                    count = snipes.count(snipe)
                    if count>1:
                        for _ in range(0, count):
                            occurences += 1
                            await self.database.delete_snipe(snipe[0], snipe[1], snipe[2])
                            print(f"Deleted {snipe[0]} {snipe[1]} {snipe[2]} from snipes db as it was a dupe")
                        scanned_snipes.append(snipe)
                        print(f"added back")
                        await self.database.add_snipe(snipe[0], snipe[1], snipe[2])
            return occurences
        occurences = await run_snipes(snipes, occurences)

        async def run_scores(scores, occurences):
            scanned_scores = []
            for i, snipe in enumerate(scores):
                if snipe not in scanned_scores:
                    count = scores.count(snipe)
                    if count>1:
                        for _ in range(1, count):
                            occurences += 1
                            await self.database.delete_score(snipe[0], snipe[1], snipe[2])
                            print(f"Deleted {snipe[0]} {snipe[1]} {snipe[2]} from scores db as it was a dupe")
                        scanned_scores.append(snipe)
                        print(f"added back")
                        await self.database.add_score(snipe[0], snipe[1], snipe[2], snipe[3])
            return occurences
        second_occurences = await run_scores(scores, occurences)

        await ctx.send(f"check over. found:\n**{occurences}** duped snipes\n**{second_occurences}** duped scores.")

    @checkdupe.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-checkdupe`') 

def setup(client):
    client.add_cog(CheckDupe(client))