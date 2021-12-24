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
        main_user_id = await self.database.get_main_id(((user_id.lower()),))
        main_user_id = main_user_id[0]
        friends = await self.database.get_user_friends(main_user_id)
        if main_user_id is not None:
            main_username = main_user_id
            friendmessage = ""
            for friend in friends:
                friend_data = await self.database.get_friend_username(friend[1], main_user_id)
                friendmessage += f"{friend_data[0]} \n"
            await ctx.send('**Friend List For ' +
                            user_id + '**:\n```\n' + friendmessage + '```')
            
    @friends.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-friends "main username"`') 

def setup(client):
    client.add_cog(Friends(client))