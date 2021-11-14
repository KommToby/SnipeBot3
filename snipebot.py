# TODO
# 1: PASSIVE SNIPE TRACKER (FOR IDLE BEATMAP PROCESSING)
# 2: BETTER WAY OF GETTING MAIN USER ID FROM FRIEND (FOR MAIN USERS ATTACHED TO FRIEND, CHECK BOTH MAIN USERS FOR SNIPES, ETC)
#

import json
import os

from discord.ext import commands

from osu import osu_auth
from help import Help
from database import init_db
from snipe_tracker import SnipeTracker

with open("config.json") as f:
    DISCORD_CONFIG_DATA = json.load(f)["discord"]
    TOKEN = DISCORD_CONFIG_DATA["token"]

GUILD = None
AUTH = osu_auth.OsuAuth()
DATABASE = init_db.Database()
client = commands.Bot(command_prefix="-", help_command=Help())


# called when bot is online
@client.event
async def on_ready():
    print("Connected")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")
    snipe_bot_tracker = SnipeTracker(client, AUTH, DATABASE)
    snipe_bot_tracker.start_loop()


@client.command(name="load")
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded {extension}")


# Command unloader
@client.command(name="unload")
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f"Unloaded {extension}")


#  must be final line
if __name__ == '__main__':
    client.run(TOKEN)
