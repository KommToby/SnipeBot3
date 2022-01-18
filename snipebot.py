# TODO
# 1: BETTER -HELP COMMAND FORMAT
# 2: -ping COMMAND TO ENABLE PINGS FOR USERS WHEN THEY ARE SNIPED
# 3: -link COMMAND TO LINK USERS DISCORD ID TO THEIR OSU ID
# 4: MAKE IT SO WHEN CHECKING A BEATMAP, IF THE BEATMAPSET EXISTS, CHECK EVERY MAP IN BEATMAPSET (MIGHT NOT BE POSSIBLE)
# 5: Map-specific statistics
# 6: If someones recent plays returns none, you can skip checking them again for another ~3-5 minutes, since its unrealistic that they will get that many so quickly

import json
import os

from discord.ext import commands

from osuauth import osu_auth
from help import Help
from database import init_db
from database import init_db_2
from snipe_tracker import SnipeTracker


with open("config.json") as f:
    DISCORD_CONFIG_DATA = json.load(f)["discord"]
    TOKEN = DISCORD_CONFIG_DATA["token"]

GUILD = None
AUTH = osu_auth.OsuAuth()
DATABASE = init_db.Database()
DATABASE2 = init_db_2.Database2()
client = commands.Bot(command_prefix="-", help_command=Help())
snipe_bot_tracker = SnipeTracker(client, AUTH, DATABASE, DATABASE2)


# called when bot is online
@client.event
async def on_ready():
    print("Connected")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")
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
