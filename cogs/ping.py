import discord
from discord.ext import commands

class Ping(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener() # event within the cog
    async def on_ready(self):
        print('Bot is online.')

    @commands.command(aliases=['latency']) # command within the cog
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms')

def setup(client):
    client.add_cog(Ping(client))