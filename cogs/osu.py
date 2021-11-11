from embed.osu_profile import Profile
import discord
from discord.ext import commands

import sys
sys.path.append("..")


class Osu(commands.Cog):  # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.profile = Profile()

    @commands.command(aliases=['profile'])
    async def osu(self, ctx, id: str):
        await self.profile.profile(ctx, id)

    @osu.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-osu <username>`')


def setup(client):
    client.add_cog(Osu(client))
