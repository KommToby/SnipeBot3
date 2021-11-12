import random
import discord
import time
import asyncio
import sys
from database.init_db import Database
from osu.osu_auth import OsuAuth
from embed.score_post import ScorePost
from embed.snipe_post import SnipePost

class Main():
    def __init__(self):
        self.database = Database()
        self.osu = OsuAuth()
        self.score_embed = ScorePost()
        self.snipe_embed = SnipePost()

    async def handle_recent(play):
        if play == []:
            return 0

    async def check_friend_snipe(self, play):
        sniped = []
        friends = self.database.get_user_friends(play['user_id'])
        for _, friend in enumerate(friends):
            friend_play = await self.osu._get_api_v2("/v2/beatmaps/" + str(play['beatmap']['id']) + "/scores/users/" + str(friend[1]))
            if friend_play != {}:
                if not(self.database.get_user_beatmap_play(str(friend[1]), str(play['beatmap']['id']))):
                    self.database.add_score(str(friend[1]),str(play['beatmap']['id']),friend_play['score']['score'], 0)
                    # for above, if the play isnt already listed as a beatmap for that user on the database
                if friend_play['score']['score'] < play['score']:
                    sniped.append(friend_play['score']['user']['username'])
                    discord_id = self.database.get_main_discord(play['user_id'])
                    if not(self.database.get_user_snipe_on_beatmap(play['user_id'], play['beatmap']['id'], friend[1])): # can only be sniped once per map
                        self.database.add_friend_sniped(friend[1], discord_id[0])
                        self.database.add_snipe(play['user_id'], play['beatmap']['id'], friend[1])
        return sniped

    async def check_beatmap(self, play):
        if not(self.database.get_beatmap(play['beatmap']['id'])): # if beatmap isnt in the db
            self.database.add_beatmap(play['beatmap']['id'], play['beatmapset']['artist'], play['beatmapset']['title'], play['beatmap']['version'], play['beatmap']['url'])

    async def tracker(self, client):
        start_time = time.time()
        users = self.database.get_all_users()
        for _, data in enumerate(users):  # 1 is userid
            user_data = await self.osu._get_api_v2("/v2/users/" + str(data[1]))
            if user_data != {}:
                recent_plays = await self.osu._get_api_v2("/v2/users/" + str(user_data['id']) + "/scores/recent")
                for _, play in enumerate(recent_plays):
                    post = 1
                    user_play = self.database.get_user_beatmap_play(str(user_data['id']), str(play['beatmap']['id']))
                    if user_play != None:
                        # this means the play DOES exist for this user in the database
                        # if its an improvement, replace it
                        if play['score'] > int(user_play[2]):
                            await self.database.replace_user_play(user_play[0], user_play[1], play['score'])
                        else:
                            post = 0 # Do not post because its not a new best
                    else:
                        # if its a new play, add it directly to the database
                        self.database.add_score(str(user_data['id']), str(
                            play['beatmap']['id']), str(play['score']), 0)
                    await self.check_beatmap(play) # check if map is stored in the database
                    if post == 1:
                        sniped_friends = await self.check_friend_snipe(play) # get friends sniped
                        discord_channel = self.database.get_main_discord(play['user']['id'])
                        await self.score_embed.scorepost(play, sniped_friends, client, discord_channel)

        friends = self.database.get_all_friends()
        for _, friend in enumerate(friends): # now we do the same but for friends
            friend_data = await self.osu._get_api_v2("/v2/users/" + str(friend[1]))
            if friend_data != {}:
                main_user = self.database.get_main_from_friend(friend_data['id'])
                recent_plays = await self.osu._get_api_v2("/v2/users/" + str(friend_data['id']) + "/scores/recent")
                for _, play in enumerate(recent_plays):
                    main_user_play = await self.osu._get_api_v2("/v2/beatmaps/" + str(play['beatmap']['id']) + "/scores/users/" + str(main_user[0]))
                    friend_play = self.database.get_user_beatmap_play(str(friend_data['id']), str(play['beatmap']['id']))
                    if friend_play != None:
                        if play['score'] > int(friend_play[2]):
                            await self.database.replace_user_play(friend_play[0], friend_play[1], play['score'])
                    else:
                        self.database.add_score(str(friend_data['id']), str(play['beatmap']['id']), str(play['score']), 0)
                    
                    if main_user_play != {}:
                        await self.check_beatmap(play)
                        if int(play['score']) > int(main_user_play['score']['score']):
                            if not(self.database.get_user_snipe_on_beatmap(play['user']['id'], play['beatmap']['id'], main_user[0])):
                                main_user_username = main_user_play['score']['user']['username']
                                self.database.add_snipe(play['user_id'], play['beatmap']['id'], main_user[0])
                                discord_channel = self.database.get_main_discord(main_user[0])
                                await self.snipe_embed.snipepost(play, client, discord_channel, main_user_username)
        print("Time to cycle all users and friends: " + str(round(time.time()-start_time,2)) + " seconds")