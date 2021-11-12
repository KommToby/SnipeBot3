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
    async def friend(self, ctx, param : str, user_id : str):
        if param == "add":
            channels = self.database.get_all_discord()
            channel = 0
            for _, channel in enumerate(channels):
                if channel == str(ctx.channel.id):
                    channel = 1
                    user_data = await self.osu._get_api_v2("/v2/users/" + str(user_id))
                    userid = user_data['id']
                    if not(self.database.get_friend(userid, ctx.channel.id)):
                        self.database.add_friend(ctx.channel.id, userid)
                        await ctx.send(str(user_id) + " has been added as a friend!")
                    else:
                        await ctx.send("User is already added as a friend.")
            if channel == 0:
                await ctx.send("There is no main user being tracked in this channel")

def setup(client):
    client.add_cog(Friend(client))