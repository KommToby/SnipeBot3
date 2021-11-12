import discord
from discord.ext import commands, tasks
from database.init_db import Database
from main import Main


class Track(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = Database()

    @commands.command(aliases=['t'])
    @commands.has_permissions(administrator=True)
    async def track(self, ctx, userid : str):
        if self.database.get_channel(ctx.channel.id):
            await ctx.send(
                "<@"+str(ctx.author.id) +
                "> Channel is already being tracked!"
                    + " (1 tracked user per channel)"
            )
            return

        await self.database.add_channel(ctx.channel.id, userid)
        await ctx.send("Started Tracking user " + str(userid))

    @track.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-track "username"`')   


def setup(client):
    client.add_cog(Track(client))