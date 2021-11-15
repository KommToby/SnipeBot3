import discord
from discord.ext import commands
from embed.create_embeds import create_friend_leaderboard
from snipebot import DATABASE, AUTH

class Leaderboard(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    def sort_friend_snipes(self, friends_data):
        friends_data.sort(
            reverse=True, key=lambda friends_data: friends_data['snipe difference']
        )

    @commands.command(aliases=['best'])
    async def leaderboard(self, ctx):
        await ctx.send("Loading Leaderboard, please wait..")
        leaderboard = []
        main_user_id = self.database.get_main_from_discord(ctx.channel.id)
        main_user_id = main_user_id[0]
        friends = self.database.get_all_friends()
        for _, friend in enumerate(friends):
            friend_data = await self.osu.get_user_data(friend[1])
            snipes = self.database.get_single_user_snipes(friend[1], main_user_id)
            sniped = self.database.get_single_user_snipes(main_user_id, friend[1])
            snipes = len(snipes)
            sniped = len(sniped)
            snipe_difference = snipes - sniped
            leaderboard.append({'username': friend_data['username'], 'snipes': snipes, 'sniped': sniped, 'snipe difference': snipe_difference})
        self.sort_friend_snipes(leaderboard)
        main_snipes = self.database.get_main_snipes(main_user_id)
        main_sniped = self.database.get_main_sniped(main_user_id)
        main_snipes = len(main_snipes)
        main_sniped = len(main_sniped)
        main_data = await self.osu.get_user_data(main_user_id)
        embed = await create_friend_leaderboard(leaderboard, main_data['username'], main_snipes, main_sniped)
        await ctx.send(embed=embed)

    @leaderboard.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-leaderboard`')    

def setup(client):
    client.add_cog(Leaderboard(client))