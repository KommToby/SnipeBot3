from discord.ext import commands
from snipebot import DATABASE
from osuauth.osu_auth import OsuAuth


class Track(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = OsuAuth()

    @commands.command(aliases=['t'])
    @commands.has_permissions(administrator=True)
    async def track(self, ctx, userid : str):
        if await self.database.get_channel(ctx.channel.id):
            await ctx.send(f"<@{ctx.author.id}> channel is already being tracked! (1 tracked user per channel)")
            return

        user_data = await self.osu.get_user_data(str(userid))
        await self.database.add_channel(ctx.channel.id, userid, user_data)
        await ctx.send("Started Tracking user " + str(userid))

    @track.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-track "username"`')   


def setup(client):
    client.add_cog(Track(client))