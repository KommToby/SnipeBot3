import discord
from discord.ext import commands

class Snipes(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client

def setup(client):
    client.add_cog(Snipes(client))