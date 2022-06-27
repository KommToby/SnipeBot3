import discord
from discord.ext import commands
from embed.create_embeds import create_snipes_embed
from snipebot import DATABASE, AUTH
import random
import time

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
        position, score, not_sniped, not_sniped_main = await self.handle_leaderboard(main_user_id, user_data['id'])
        embed = await create_snipes_embed(user_data, snipes, sniped, total_snipes, random_play_data, random_sniped_data, position, score, not_sniped, not_sniped_main)
        await ctx.send(embed=embed)

    async def handle_leaderboard(self, main_user_id, friend_id):
        leaderboard = []
        main_discord = await self.database.get_main_discord(main_user_id)
        main_discord = main_discord[0]
        friends = await self.database.get_user_friends(main_discord)
        for _, friend in enumerate(friends):
            snipes = await self.database.get_single_user_snipes(friend[1], main_user_id)
            sniped = await self.database.get_single_user_snipes(main_user_id, friend[1])
            not_sniped_back = []
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
            # reduction multiplier
            start_time = time.time()
            multiplier = 1
            total_scores = await self.database.get_all_scores(main_user_id)
            total_scores = len(total_scores)
            if snipes < total_scores:
                multiplier = (5/100) + (0.95 * (snipes/(total_scores+1)))
            snipe_difference = round((multiplier*((3*snipes + 7*not_sniped_back)/(2*not_sniped_main+(snipes/(not_sniped_back+1))*sniped+1)*4000)), 2)
            if str(friend_id) == friend[1]:
                friend_data = await self.osu.get_user_data(friend[1])
                friend_dict = {'username': friend_data['username'], 'snipes': snipes, 'sniped': sniped, 'snipe difference': snipe_difference}
                leaderboard.append(friend_dict)
            else:
                leaderboard.append({'username': "N/A", 'snipes': snipes, 'sniped': sniped, 'snipe difference': snipe_difference})
            
        leaderboard.sort(
            reverse=True, key=lambda friends_data: friends_data['snipe difference']
        )
        snipes = await self.database.get_single_user_snipes(friend_id, main_user_id)
        sniped = await self.database.get_single_user_snipes(main_user_id, friend_id)
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
        multiplier = 1
        total_scores = await self.database.get_all_scores(main_user_id)
        total_scores = len(total_scores)
        if snipes < total_scores:
            multiplier = (5/100) + (0.95 * (snipes/total_scores))
        snipe_difference = round((multiplier*((3*snipes + 7*not_sniped_back)/(2*not_sniped_main+(snipes/not_sniped_back)*sniped+1)*4000)), 2)
        return leaderboard.index(friend_dict), snipe_difference, not_sniped_back, not_sniped_main

    @snipes.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-snipes "username"`')    

def setup(client):
    client.add_cog(Snipes(client))