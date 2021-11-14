import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker


class Friend(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command(aliases=['f'])
    @commands.has_permissions(administrator=True)
    async def friend(self, ctx, param : str, user_id : str):
        if param == "add":
            channels = self.database.get_all_discord()
            channel = 0
            for _, channel in enumerate(channels):
                if channel[0] == str(ctx.channel.id):
                    channel = 1
                    user_data = await self.osu.get_user_data(str(user_id))
                    if user_data:
                        userid = user_data['id']
                        if not(self.database.get_friend(userid, ctx.channel.id)):
                            self.database.add_friend(ctx.channel.id, userid)
                            await ctx.send(str(user_id) + " has been added as a friend!")
                            await snipe_bot_tracker.new_user(user_data['id'])
                        else:
                            await ctx.send("User is already added as a friend.")
            if channel == 0:
                await ctx.send("There is no main user being tracked in this channel")

    @friend.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-friend add/remove "username"`') 

def setup(client):
    client.add_cog(Friend(client))