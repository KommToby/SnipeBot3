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

async def a():
    friends = DATABASE.get_all_friends()
    for friend in friends:
        friend_data = await AUTH.get_user_data(friend[1])
        print("")
