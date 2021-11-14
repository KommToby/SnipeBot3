import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH


class Friends(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command()
    async def friends(self, ctx, user_id : str):
        await ctx.send("Loading friends list, please wait..")
        main_user = await self.osu.get_user_data(user_id)
        main_user_id = main_user['id']
        friends = self.database.get_user_friends(main_user_id)
        if main_user_id is not None:
            main_username = main_user['username']
            friendmessage = ""
            friend_array = []
            for friend in friends:
                friend_data = await self.osu.get_user_data(friend[1])
                friendmessage += f"{friend_data['username']} \n"
            await ctx.send('**Friend List For ' +
                            main_username + '**:\n```\n' + friendmessage + '```')
            
    @friends.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-friends "main username"`') 

def setup(client):
    client.add_cog(Friends(client))