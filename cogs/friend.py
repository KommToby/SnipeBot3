import discord
from discord.ext import commands
from database.init_db import Database
from osu.osu_auth import OsuAuth

class Friend(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = Database()
        self.osu = OsuAuth()

    @commands.command(aliases=['f'])
    @commands.has_permissions(administrator=True)
    async def friend(self, ctx, ar : str, user_id : str):
        if ar == "add":
            user_data = await self.osu._get_api_v2("/v2/users/" + str(user_id))
            userid = user_data['id']
            self.database.add_friend(ctx.channel.id, userid)
            await ctx.send(str(user_id) + " has been added as a friend!")

def setup(client):
    client.add_cog(Friend(client))