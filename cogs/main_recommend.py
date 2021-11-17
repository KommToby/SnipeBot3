import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker
import random


class MainRecommend(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command(aliases=['mr'])
    @commands.has_permissions(administrator=True)
    async def main_recommend(self, ctx, user_id : str):
        user_data = await self.osu.get_user_data(user_id)
        username = user_data['username']
        userid = user_data['id']
        friends = self.database.get_user_friends(userid)
        beatmaps = []
        links = []
        if user_data:
            if friends:
                for friend in friends:
                    main_scores = self.database.get_all_scores(userid)
                    friend_scores = self.database.get_all_scores(friend[1])
                    for score in main_scores:
                        add = True
                        for friend_score in friend_scores:
                            if score[1] != friend_score[1] and add is not False:
                                add = True
                            else:
                                add = False
                        if add is True:
                            beatmap = self.database.get_beatmap_data(score[1])
                            if beatmap[4] not in links:
                                beatmaps.append(f"{beatmap[1]} - {beatmap[2]} [{beatmap[3]}]")
                                links.append(beatmap[4])
                if len(beatmaps) > 0:
                    index = random.randint(0, len(beatmaps)-1)
                    send_message = "**__Random map recommendation for "+str(user_data['username'])+"__**\n"
                    send_message += "`" + str(beatmaps[index]) + "`\n<" + str(links[index]) + ">\n"
                    await ctx.send(send_message)
                else:
                    await ctx.send("No recommendations at this time. Play some more maps and try again later.")



    @main_recommend.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-recommend "username"`') 

def setup(client):
    client.add_cog(MainRecommend(client))