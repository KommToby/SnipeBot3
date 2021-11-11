import discord
from discord.ext import commands


class Purge(commands.Cog):  # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['clear'])
    @commands.has_permissions(manage_messages=True)  # permission check
    async def purge(self, ctx, amount: int):  # clears
        await ctx.channel.purge(limit=amount)

    @purge.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-clear <number of messages>`')


def setup(client):
    client.add_cog(Purge(client))
