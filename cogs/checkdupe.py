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
        snipes = self.database.get_all_snipes()
        def run_snipes(snipes, occurences):
            for i, snipe in enumerate(snipes):
                count = snipes.count(snipe)
                snipestatus = False
                while count > 1:
                    snipestatus = True
                    occurences += 1
                    self.database.delete_snipe(snipe[0], snipe[1], snipe[2])
                    print(f"Deleted {snipe[0]} {snipe[1]} {snipe[2]} from db as it was a dupe")
                    count = count - 1
                if snipestatus is True:
                    break
            if snipestatus is True:
                return False, occurences
            else:
                return True, occurences
        status, occurences = run_snipes(snipes, occurences)
        while status is False:
            snipes = self.database.get_all_snipes()
            status, occurences = run_snipes(snipes, occurences)

        await   ctx.send(f"check over. found {occurences} duped snipes")

    @checkdupe.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-checkdupe`') 

def setup(client):
    client.add_cog(CheckDupe(client))