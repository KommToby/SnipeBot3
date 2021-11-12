from embed.osu_profile import create_osu_profile_embed
from osu.osu import Osu
from discord.ext import commands

import sys
sys.path.append("..")


class OsuCommands(commands.Cog):  # must have commands.cog or this wont work
    def __init__(self, client):
        self.client = client
        self.osu = Osu()

    @commands.command(aliases=['profile'])
    async def osu(self, ctx, user: str):
        user_data = await self.osu.get_user_data(user)
        embed = create_osu_profile_embed(user_data)
        await ctx.send(embed=embed)

    @osu.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-osu "username"`')


def setup(client):
    client.add_cog(OsuCommands(client))
