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
        leaderboard = []
        main_user_id = await self.database.get_main_from_discord(ctx.channel.id)
        main_user_id = main_user_id[0]
        friends = await self.database.get_user_friends(main_user_id) # specifically get the list of friends for that user
        for _, friend in enumerate(friends):
            friend_leaderboard = await self.database.get_stored_leaderboard(main_user_id, friend[1])
            friend_leaderboard = friend_leaderboard[0]
            friend_data = await self.database.get_friend_username(friend[1], main_user_id)
            snipes = await self.database.get_single_user_snipes(friend[1], main_user_id)
            sniped = await self.database.get_single_user_snipes(main_user_id, friend[1])
            not_sniped_back = [] # Maps that the main user has not sniped back
            for snipe in snipes:
                add = True
                for sniped_play in sniped:
                    if snipe[1] == sniped_play[1]:
                        add = False
                if add is True:
                    not_sniped_back.append(snipe)

            not_sniped_main = [] # Maps that the friend has not sniped back off the main user
            for sniped_play in sniped:
                add = True
                for snipe in snipes:
                    if snipe[1] == sniped_play[1]:
                        add = False
                if add is True:
                    not_sniped_main.append(sniped_play)
            snipes = len(snipes)
            sniped = len(sniped)
            not_sniped_back = len(not_sniped_back)        
            not_sniped_main = len(not_sniped_main)
            snipe_weight = ((snipes + 2*not_sniped_back)/(not_sniped_main+sniped)*1000)
            await self.database.update_local_leaderboard(main_user_id, friend[1], snipe_weight)
            leaderboard.append({'username': friend_data[0], 'snipes': snipes, 'sniped': sniped, 'snipe difference': snipe_weight, 'local_weight': friend_leaderboard})
        self.sort_friend_snipes(leaderboard)
        main_snipes = await self.database.get_main_snipes(main_user_id)
        main_sniped = await self.database.get_main_sniped(main_user_id)
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