import time

from discord.ext import tasks

from osu.osu_auth import OsuAuth
from database.init_db import Database
from embed.create_embeds import *


class SnipeTracker:
    def __init__(self, bot: commands.Bot, auth: OsuAuth, database: Database):
        self.bot = bot
        self.osu = auth
        self.database = database

    def start_loop(self):
        self.tracker_loop.start()

    async def get_sniped_friends(self, play):
        sniped = []
        friends = self.database.get_user_friends(play["user_id"])
        for friend in friends:
            friend_play = await self.osu.get_score_data(play["beatmap"]["id"], friend[1])
            user_id = f"{friend[1]}"
            beatmap_id = play['beatmap']['id']
            if friend_play:
                score = friend_play['score']['score']
                if not self.database.get_user_beatmap_play(user_id, beatmap_id):
                    self.database.add_score(user_id, beatmap_id, score, 0)
                if friend_play['score']['score'] < play['score']:
                    sniped.append(friend_play['score']['user']['username'])
                    discord_id = self.database.get_main_discord(play['user_id'])
                    if not(self.database.get_user_snipe_on_beatmap(play['user_id'], beatmap_id, user_id)): # can only be sniped once per map
                        self.database.add_friend_sniped(user_id, discord_id[0])
                        self.database.add_snipe(play['user_id'], beatmap_id, user_id)
        return sniped

    async def check_beatmap(self, play):
        if not(self.database.get_beatmap(play['beatmap']['id'])): # if beatmap isnt in the db
            self.database.add_beatmap(play['beatmap']['id'], play['beatmapset']['artist'], play['beatmapset']['title'], play['beatmap']['version'], play['beatmap']['url'])

    @tasks.loop(seconds=30.0)
    async def tracker_loop(self):
        start_time = time.time()
        users = self.database.get_all_users()
        for data in users:
            user_id = f"{data[1]}"
            user_data = await self.osu.get_user_data(user_id)
            if user_data:
                recent_plays = await self.osu.get_recent_plays(user_id)
                for play in recent_plays:
                    await self.check_beatmap(play)
                    user_play = self.database.get_user_beatmap_play(user_id, f"{play['beatmap']['id']}")
                    if user_play:
                        if play['score'] > int(user_play[2]):
                            await self.database.replace_user_play(user_play[0], user_play[1], play['score'])
                            sniped_friends = await self.get_sniped_friends(play)
                            discord_channel = self.database.get_main_discord(play['user']['id'])
                            channel = self.bot.get_channel(int(discord_channel[0]))
                            await channel.send(embed=create_score_embed(play, sniped_friends))
                    else:
                        self.database.add_score(str(user_data['id']), str(
                            play['beatmap']['id']), str(play['score']), 0)
                        sniped_friends = await self.get_sniped_friends(play)
                        discord_channel = self.database.get_main_discord(play['user']['id'])
                        channel = self.bot.get_channel(int(discord_channel[0]))
                        await channel.send(embed=create_score_embed(play, sniped_friends))

        friends = self.database.get_all_friends()
        for friend in friends:
            user_id = f"{friend[1]}"
            friend_data = await self.osu.get_user_data(user_id)
            if friend_data:
                main_user = self.database.get_main_from_friend(friend_data['id'])
                main_user_id = f"{main_user[0]}"
                recent_plays = await self.osu.get_recent_plays(user_id)
                for play in recent_plays:
                    beatmap_id = f"{play['beatmap']['id']}"
                    main_user_play = await self.osu.get_score_data(beatmap_id, main_user_id)
                    friend_play = self.database.get_user_beatmap_play(f"{friend_data['id']}", beatmap_id)
                    if friend_play:
                        if play['score'] > int(friend_play[2]):
                            await self.database.replace_user_play(friend_play[0], friend_play[1], play['score'])
                    else:
                        self.database.add_score(str(friend_data['id']), str(play['beatmap']['id']), str(play['score']),
                                                0)
                    if main_user_play:
                        await self.check_beatmap(play)
                        if int(play['score']) > int(main_user_play['score']['score']):
                            if not self.database.get_user_snipe_on_beatmap(play['user']['id'], play['beatmap']['id'], main_user[0]):
                                main_user_username = main_user_play['score']['user']['username']
                                self.database.add_snipe(play['user_id'], play['beatmap']['id'], main_user[0])
                                discord_channel = self.database.get_main_discord(main_user[0])
                                channel = await self.bot.get_channel(discord_channel)
                                await channel.send(embed=create_snipe_embed(play, main_user_username))

        print(f"Snipe loop took {round(time.time() - start_time, 2)} seconds")

    @tracker_loop.before_loop
    async def before_tracker(self):
        await self.bot.wait_until_ready()
