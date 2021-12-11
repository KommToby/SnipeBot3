import discord
from discord.ext import commands
from embed.create_embeds import create_snipes_embed
from snipebot import DATABASE, AUTH
import random

class Snipes(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command(aliases=['s'])
    async def snipes(self, ctx, user: str):
        main_user_id = await self.database.get_main_from_discord(ctx.channel.id)
        main_user_id = main_user_id[0]
        user_data = await self.osu.get_user_data(user)
        snipes = await self.database.get_single_user_snipes(str(user_data['id']), main_user_id)
        sniped = await self.database.get_single_user_snipes(main_user_id, str(user_data['id']))
        total_snipes = await self.database.get_total_snipes(main_user_id)
        user_snipes = await self.database.get_single_user_snipes(user_data['id'], main_user_id)
        user_sniped = await self.database.get_single_user_snipes(main_user_id, user_data['id'])
        if user_snipes != []:
            random_play_index = random.randint(0, len(user_snipes)-1)
            random_play = user_snipes[random_play_index]
            random_play_data = await self.osu.get_score_data(random_play[1], random_play[0])
        else:
            random_play_data = False
        if user_sniped != []:
            random_play_index = random.randint(0, len(user_sniped)-1)
            random_play = user_sniped[random_play_index]
            random_sniped_data = await self.osu.get_score_data(random_play[1], random_play[0])
        else:
            random_sniped_data = False
        position = await self.handle_leaderboard(main_user_id, user_data['id'])
        embed = await create_snipes_embed(user_data, snipes, sniped, total_snipes, random_play_data, random_sniped_data, position)
        await ctx.send(embed=embed)

    async def handle_leaderboard(self, main_user_id, friend_id):
        leaderboard = []
        friends = await self.database.get_user_friends(main_user_id)
        for _, friend in enumerate(friends):
            snipes = await self.database.get_single_user_snipes(friend[1], main_user_id)
            sniped = await self.database.get_single_user_snipes(main_user_id, friend[1])
            snipes = len(snipes)
            sniped = len(sniped)
            snipe_difference = (2*snipes)/(sniped+10)
            if str(friend_id) == friend[1]:
                friend_data = await self.osu.get_user_data(friend[1])
                friend_dict = {'username': friend_data['username'], 'snipes': snipes, 'sniped': sniped, 'snipe difference': snipe_difference}
                leaderboard.append(friend_dict)
            else:
                leaderboard.append({'username': "N/A", 'snipes': snipes, 'sniped': sniped, 'snipe difference': snipe_difference})
            
        leaderboard.sort(
            reverse=True, key=lambda friends_data: friends_data['snipe difference']
        )
        return leaderboard.index(friend_dict)

    @snipes.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-snipes "username"`')    

def setup(client):
    client.add_cog(Snipes(client))