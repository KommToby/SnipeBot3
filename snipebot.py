# TODO
# 1: Local, single database, called scores.db: USER_ID, BEATMAP_ID, USER_SCORE
# 2: Local, single database, called user.db: DISCORD_ID, USER_ID, PING_STATUS
# 3: Main loop that checks for new scores for every user
# 4: When ANYONE gets a new score, if the map hasn't been checked before, the map checks all the friends to see if they beat the main user after the main user set their play
# 5: Local, single database, called friends.db: DISCORD_ID, FRIEND_ID
# 6: Store all plays in a database table USER_ID, BEATMAP_ID, SCORE

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
client.run(TOKEN)
