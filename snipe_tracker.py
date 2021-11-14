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
                    if not(self.database.get_user_snipe_on_beatmap(play['user_id'], beatmap_id, user_id)): # can only be sniped once per map
                        self.database.add_snipe(play['user_id'], beatmap_id, user_id)
        return sniped

    async def scan_top(self):
        friends = self.database.get_all_friends()
        for friend in friends:
            friend_data = await self.osu.get_user_scores(friend[1])
            for score in friend_data:
                await self.check_beatmap(score)

    async def scan_single_top(self, userid):
        friend_data = await self.osu.get_user_scores(userid)
        for score in friend_data:
            await self.check_beatmap(score)

    async def check_beatmap(self, play): # passive tracking
        if not(self.database.get_beatmap(play['beatmap']['id'])): # if beatmap isnt in the db
            self.database.add_beatmap(play['beatmap']['id'], play['beatmapset']['artist'], play['beatmapset']['title'], play['beatmap']['version'], play['beatmap']['url'])
            await self.add_snipes(play)

    async def add_snipes(self, play):        
        main_users = self.database.get_all_users()
        for _, user in enumerate(main_users):
            main_play = await self.osu.get_score_data(play['beatmap']['id'], user[1])
            if main_play:
                friends = self.database.get_user_friends(user[1])
                main_date = await self.convert_date(main_play['score']['created_at'])
                for friend in friends:
                    friend_play = await self.osu.get_score_data(play['beatmap']['id'], friend[1])
                    if friend_play:
                        friend_date = await self.convert_date(friend_play['score']['created_at'])
                        if await self.date_more_recent_than(friend_date, main_date):
                            if friend_play['score']['score'] > main_play['score']['score']:
                                self.database.add_snipe(friend[1], play['beatmap']['id'], user[1])
                        else:
                            if main_play['score']['score'] > friend_play['score']['score']:
                                self.database.add_snipe(user[1], play['beatmap']['id'], friend[1])

    async def new_user(self, user_data):
        beatmaps = self.database.get_all_beatmaps()
        await self.scan_single_top(user_data)
        for _, beatmap in enumerate(beatmaps):
            play = await self.osu.get_score_data(user_data, beatmap[0])
            if play:
                self.add_snipes(play)

    async def check_main_beatmap(self, play):
        if not(self.database.get_beatmap(play['beatmap']['id'])): # if beatmap isnt in the db
            self.database.add_beatmap(play['beatmap']['id'], play['beatmapset']['artist'], play['beatmapset']['title'], play['beatmap']['version'], play['beatmap']['url'])        

    async def date_more_recent_than(self, date1, date2):
        if type(date1) is dict and type(date2) is dict:
            if date1.keys() == date2.keys():
                if date1 == date2:
                    return True
                return self._more_recent_than(list(date1.values()), list(date2.values()))


    async def _more_recent_than(self, date1, date2):
        if type(date1) is list and type(date2) is list:
            if len(date1) == len(date2):
                if (date1[0] > date2[0]):
                    return True
                elif len(date1) > 1 and len(date2) > 1:
                    return self._more_recent_than(date1[1:], date2[1:])
                else:
                    return False

    async def convert_date(self, datetime):
        date = datetime.split('-')
        year = date[0]
        month = date[1]
        date = date[2].split('T')
        day = date[0]
        date = date[1].split(':')
        hour = date[0]
        minute = date[1]
        date = date[2].split("+")
        second = date[0]
        return {'year': year, 'month': month, 'day': day, 'hour': hour, 'minute': minute, 'second': second}


    @tasks.loop(seconds=30.0)
    async def tracker_loop(self):
        # await self.scan_top() # UNCOMMENT THIS WHEN RESETTING EVERYTHING AND RUN ONCE
        start_time = time.time()
        users = self.database.get_all_users()
        for data in users:
            user_id = f"{data[1]}"
            user_data = await self.osu.get_user_data(user_id)
            if user_data:
                recent_plays = await self.osu.get_recent_plays(user_id)
                for play in recent_plays:
                    await self.check_main_beatmap(play)
                    user_play = self.database.get_user_beatmap_play(user_id, f"{play['beatmap']['id']}")
                    online_play = await self.osu.get_score_data(play['beatmap']['id'], user_id)
                    if user_play:
                        if play['score'] > int(user_play[2]):
                            await self.database.replace_user_play(user_play[0], user_play[1], play['score'])
                            if play['score'] >= online_play['score']:
                                sniped_friends = await self.get_sniped_friends(play)
                                discord_channel = self.database.get_main_discord(user_id)
                                channel = self.bot.get_channel(int(discord_channel[0]))
                                await channel.send(embed=create_score_embed(play, sniped_friends))
                    else:
                        self.database.add_score(str(user_data['id']), str(
                            play['beatmap']['id']), str(play['score']), 0)
                        if play['score'] >= online_play['score']['score']:    
                            sniped_friends = await self.get_sniped_friends(play)
                            discord_channel = self.database.get_main_discord(user_id)
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
                if recent_plays:
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
                                    channel = self.bot.get_channel(int(discord_channel[0]))
                                    await channel.send(embed=create_snipe_embed(play, main_user_username))

        print(f"Snipe loop took {round(time.time() - start_time, 2)} seconds")

    @tracker_loop.before_loop
    async def before_tracker(self):
        await self.bot.wait_until_ready()
