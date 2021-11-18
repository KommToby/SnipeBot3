import discord
from discord.ext import commands
from embed.create_embeds import create_snipes_embed
from snipebot import DATABASE, AUTH
import random
from embed import create_embeds

class Snipelist(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command()
    async def snipelist(self, ctx, username: str):
        main_user = self.database.get_main_from_discord(ctx.channel.id)
        main_user = main_user[0]
        user_data = await self.osu.get_user_data(username)
        if user_data:
            user = user_data['id']
            if main_user:
                snipes = self.database.get_single_user_snipes(user, main_user)
                sniped = self.database.get_single_user_snipes(main_user, user)
                beatmaps = []
                links = []
                for got_sniped in sniped:
                    add = True
                    for snipe in snipes:
                        if snipe[1] != got_sniped[1] and add is not False:
                            add = True
                        else:
                            add = False
                    if add == True:
                        beatmap = self.database.get_beatmap_data(got_sniped[1])
                        if beatmap[4] not in links:
                            beatmaps.append(f"{beatmap[1]} - {beatmap[2]} [{beatmap[3]}]")
                            links.append(beatmap[4])
                embed = await create_embeds.create_snipelist_embed(beatmaps, username, links, user_data)
                await ctx.send(embed=embed)
            else:
                "error. wrong channel or bot issue - please contact admin"

    @snipelist.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-snipelist "username"`')    

def setup(client):
    client.add_cog(Snipelist(client))