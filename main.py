import random
import discord
import time
import asyncio
import sys
from database.init_db import Database
from osu.osu_auth import OsuAuth
from embed.score_post import ScorePost

class Main():
    def __init__(self):
        self.database = Database()
        self.osu = OsuAuth()
        self.score_embed = ScorePost()

    async def handle_recent(play):
        if play == []:
            return 0

    async def check_friend_snipe(self, play):
        sniped = []
        friends = self.database.get_user_friends(play['user_id'])
        for _, friend in enumerate(friends):
            friend_play = await self.osu._get_api_v2("/v2/beatmaps/" + str(play['beatmap']['id']) + "/scores/users/" + str(friend[1]))
            if friend_play != {}:
                if self.database.get_user_beatmap_play(str(friend[1]), str(play['beatmap']['id'])):
                    pass
                else:
                    self.database.add_score(str(friend[1]),str(play['beatmap']['id']),friend_play['score']['score'])
                if friend_play['score']['score'] < play['score']:
                    sniped.append(friend_play['score']['user']['username'])
        return sniped

        # FOR EACH FRIEND, CHECK IF THEY HAVE A PLAY ON THE MAP AND
        # IF THE PLAY BEATS THEM, IT COUNTS AS A SNIPE ETC
        pass

    async def tracker(self, client):
        start_time = time.time()
        users = self.database.get_all_users()
        for index, data in enumerate(users):  # 1 is userid
            user_data = await self.osu._get_api_v2("/v2/users/" + str(data[1]))
            if user_data != {}:
                recent_plays = await self.osu._get_api_v2("/v2/users/" + str(user_data['id']) + "/scores/recent")
                for num, play in enumerate(recent_plays):
                    post = 1
                    user_play = self.database.get_user_beatmap_play(str(user_data['id']), str(play['beatmap']['id']))
                    if user_play != None:
                        # this means the play DOES exist for this user in the database
                        # if its an improvement, replace it
                        if play['score'] > int(user_play[2]):
                            self.database.replace_user_play(user_play[0], user_play[1], play['score'])
                        else:
                            post = 0 # Do not post because its not a new best
                    else:
                        # if its a new play, add it directly to the database
                        self.database.add_score(str(user_data['id']), str(
                            play['beatmap']['id']), str(play['score']))
                    if post == 1:
                        sniped_friends = await self.check_friend_snipe(play)
                        discord_channel = self.database.get_main_discord(play['user']['id'])
                        await self.score_embed.scorepost(play, sniped_friends, client, discord_channel)

                        # post score in discord channel (check friends sniped first)

                    # check if the user has played the map before (stored in db)
                    # if they havent, add it to database
                    # if they have, add it to database if new score
                    # if its not a new score, compare their old score to all of their
                    # friends scores, and give the friend a snipe point if they beat
                    # the main users score after they set the play.
