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
            for i, snipe in enumerate(snipes):
                count = snipes.count(snipe)
                snipestatus = False
                while count > 1:
                    snipestatus = True
                    occurences += 1
                    await self.database.delete_snipe(snipe[0], snipe[1], snipe[2])
                    print(f"Deleted {snipe[0]} {snipe[1]} {snipe[2]} from db as it was a dupe")
                    count = count - 1
                if snipestatus is True:
                    break
            if snipestatus is True:
                return False, occurences
            else:
                return True, occurences
        status, occurences = await run_snipes(snipes, occurences)
        while status is False:
            snipes = await self.database.get_all_snipes()
            status, occurences = await run_snipes(snipes, occurences)

        async def run_scores(scores, occurences):
            for i, snipe in enumerate(scores):
                count = scores.count(snipe)
                snipestatus = False
                while count > 1:
                    snipestatus = True
                    occurences += 1
                    await self.database.delete_score(snipe[0], snipe[1], snipe[2])
                    print(f"Deleted {snipe[0]} {snipe[1]} {snipe[2]} from db as it was a dupe")
                    count = count - 1
                if snipestatus is True:
                    await self.database.add_score(snipe[0], snipe[1], snipe[2], 0)
                    break
            if snipestatus is True:
                return False, occurences
            else:
                return True, occurences
        status, second_occurences = await run_scores(scores, occurences)
        while status is False:
            scores = await self.database.get_scores()
            status, second_occurences = await run_scores(scores, second_occurences)

        await   ctx.send(f"check over. found {occurences} duped snipes\nand {second_occurences} duped scores.")

    @checkdupe.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-checkdupe`') 

def setup(client):
    client.add_cog(CheckDupe(client))