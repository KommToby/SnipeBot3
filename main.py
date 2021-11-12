import random
import discord
import time
import asyncio
import sys
from database.init_db import Database
from osu.osu_auth import OsuAuth


class Main():
    def __init__(self):
        self.database = Database()
        self.osu = OsuAuth()

    async def handle_recent(play):
        if play == []:
            return 0

    async def tracker(self):
        start_time = time.time()
        users = self.database.get_all_users()
        for index, data in enumerate(users):  # 1 is userid
            user_data = await self.osu._get_api_v2("/v2/users/" + str(data[1]))
            if user_data != {}:
                recent_plays = await self.osu._get_api_v2("/v2/users/" + str(user_data['id']) + "/scores/recent")
                for num, play in enumerate(recent_plays):
                    ## check if the user has played the map before (stored in db)
                    ## if they havent, add it to database
                    ## if they have, add it to database if new score
                    ## if its not a new score, compare their old score to all of their
                    ## friends scores, and give the friend a snipe point if they beat
                    ## the main users score after they set the play.
