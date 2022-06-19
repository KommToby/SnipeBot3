import discord
from discord.ext import commands
from database.init_db import Database
from snipebot import DATABASE, AUTH, snipe_bot_tracker
from embed import create_embeds
import random


class Recommend(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command(aliases=['r'])
    async def recommend(self, ctx, user_id : str, *args):
        if not args:
            args = [""]
        if args[0] != "-min" and args[0] != "-max" and args != [""]:
            await ctx.send('Usage: `-recommend "username" ("-min/max" "stars")`')
        else:
            if args == [""]:
                args = []
            main_user = await self.database.get_main_from_discord(ctx.channel.id)
            main_user = main_user[0]
            user_data = await self.osu.get_user_data(user_id)
            beatmaps = []
            links = []
            if user_data:
                user = user_data['id']
                if main_user:
                    main_scores = await self.database.get_all_scores(main_user)
                    user_scores = await self.database.get_all_scores(user)
                    for score in main_scores:
                        add = True
                        for user_score in user_scores:
                            if str(score[2]) != "0":
                                if str(score[1]) != str(user_score[1]) and add is not False:
                                    add = True
                                else:
                                    add = False
                            else:
                                add = False
                        if add is True:
                            beatmap = await self.database.get_beatmap_data(score[1])
                            if beatmap[4] not in links:
                                beatmaps.append(beatmap)
                                links.append(beatmap[4])
                    if args == [""]:
                        pass
                    else:
                        links = []
                        for i, arg in enumerate(args):
                            if arg.lower() == "-min":
                                if self.is_float(args[i+1]):
                                    beatmaps, links = self.sort_min(beatmaps, args[i+1], links)
                                else:
                                    await ctx.send('Usage: `-recommend "username" ("-min/max" "stars")`')
                            if arg.lower() == "-max":
                                if self.is_float(args[i+1]):
                                    beatmaps, links = self.sort_max(beatmaps, args[i+1], links)
                                else:
                                    await ctx.send('Usage: `-recommend "username" ("-min/max" "stars")`')
                    new_beatmaps = []
                    new_links = []
                    for beatmap in beatmaps:
                        if beatmap[4] not in new_links:
                                new_beatmaps.append(f"{beatmap[1]} - {beatmap[2]} [{beatmap[3]}]")
                                new_links.append(beatmap[4])
                    beatmaps = new_beatmaps
                    links = new_links
                    if len(beatmaps) > 0:
                        embed = await create_embeds.create_recommendation_embed2(beatmaps, user_data, links)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("No recommendations at this time. Play some more maps and try again later.")

    def is_float(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    def sort_max(self, beatmaps, max, links):
        sorted_beatmaps = []
        sorted_links = []
        for i, beatmap in enumerate(beatmaps):
            if beatmap[5] > float(max):
                pass
            else:
                sorted_beatmaps.append(beatmap)
                sorted_links.append(beatmap[4])
        return sorted_beatmaps, sorted_links

    def sort_min(self, beatmaps, min, links):
        sorted_beatmaps = []
        sorted_links = []
        for i, beatmap in enumerate(beatmaps):
            if beatmap[5] < float(min):
                pass
            else:
                sorted_beatmaps.append(beatmap)
                sorted_links.append(beatmap[4])
        return sorted_beatmaps, sorted_links

    @recommend.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-recommend "username"`') 

def setup(client):
    client.add_cog(Recommend(client))