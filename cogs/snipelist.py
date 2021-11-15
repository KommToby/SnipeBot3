import discord
from discord.ext import commands
from embed.create_embeds import create_snipes_embed
from snipebot import DATABASE, AUTH
import random

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
        user = user_data['id']
        if main_user:
            snipes = self.database.get_single_user_snipes(user, main_user)
            sniped = self.database.get_single_user_snipes(main_user, user)
            beatmaps = []
            links = []
            for got_sniped in sniped:
                for snipe in snipes:
                    if snipe[1] != got_sniped[1]:
                        beatmap = self.database.get_beatmap_data(got_sniped[1])
                        if beatmap[4] not in links:
                            beatmaps.append(f"{beatmap[1]} - {beatmap[2]} [{beatmap[3]}]")
                            links.append(beatmap[4])
            while len(beatmaps) > 10:
                index = random.randint(0, len(beatmaps)-1)
                beatmaps.pop(index)
                links.pop(index)
            send_message = "**__Scores that "+str(username)+" has not sniped back__**\n"
            for i, beatmap in enumerate(beatmaps):
                send_message += str(i+1) + ". `" + str(beatmap) + "`\n<" + str(links[i]) + ">\n"
            await ctx.send(send_message)
        else:
            "error. wrong channel or bot issue - please contact admin"

    @snipelist.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-snipelist "username"`')    

def setup(client):
    client.add_cog(Snipelist(client))