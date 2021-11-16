import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker
import random


class Recommend(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command(aliases=['r'])
    @commands.has_permissions(administrator=True)
    async def recommend(self, ctx, user_id : str):
        main_user = self.database.get_main_from_discord(ctx.channel.id)
        main_user = main_user[0]
        user_data = await self.osu.get_user_data(user_id)
        beatmaps = []
        links = []
        if user_data:
            user = user_data['id']
            if main_user:
                main_scores = self.database.get_all_scores(main_user)
                user_scores = self.database.get_all_scores(user)
                for score in main_scores:
                    add = True
                    for user_score in user_scores:
                        if score[1] != user_score[1] and add is not False:
                            add = True
                        else:
                            add = False
                    if add is True:
                        beatmap = self.database.get_beatmap_data(score[1])
                        if beatmap[4] not in links:
                            beatmaps.append(f"{beatmap[1]} - {beatmap[2]} [{beatmap[3]}]")
                            links.append(beatmap[4])
                index = random.randint(0, len(beatmaps)-1)
                send_message = "**__Random map recommendation for "+str(user_data['username'])+"__**\n"
                send_message += "`" + str(beatmaps[index]) + "`\n<" + str(links[index]) + ">\n"
                await ctx.send(send_message)



    @recommend.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-recommend "username`') 

def setup(client):
    client.add_cog(Recommend(client))