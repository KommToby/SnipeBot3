import time

from discord.ext import tasks

from osuauth.osu_auth import OsuAuth
from database.init_db import Database
from embed.create_embeds import *


class SnipeTracker:
    def __init__(self, bot: commands.Bot, auth: OsuAuth, database: Database):
        self.bot = bot
        self.osu = auth
        self.database = database
        self.new_user = ""

    ## Submethod that just starts the indefinite loop
    def start_loop(self):
        self.tracker_loop.start()

    ## When given a main user play, the method calculates which friends got sniped from that play, and then posts the embed.
    async def get_sniped_friends(self, play):
        sniped = []
        friends = await self.database.get_user_friends(play["user_id"])
        for friend in friends:
            friend_play = await self.osu.get_score_data(play["beatmap"]["id"], friend[1])
            user_id = f"{friend[1]}"
            beatmap_id = play['beatmap']['id']
            if friend_play:
                score = friend_play['score']['score']
                if not (await self.database.get_user_beatmap_play(user_id, beatmap_id)):
                    await self.database.add_score(user_id, beatmap_id, score, 0)
                if friend_play['score']['score'] < play['score']:
                    sniped.append(friend_play['score']['user']['username'])
                    if not(await self.database.get_user_snipe_on_beatmap(play['user_id'], beatmap_id, user_id)): # can only be sniped once per map
                        print(f"        [4] Adding active snipe for {friend_play['score']['user']['username']}")
                        await self.database.add_snipe(play['user_id'], beatmap_id, user_id)
                        main_users = await self.database.get_all_users()
                        for main_user in main_users:
                            if str(friend_play['score']['user']['id']) == str(main_user[1]):
                                await self.post_friend_snipe(friend_play['score'], play, (friend_play['score']['user']['id'],))
        return sniped

    ## Checks all friends, and all their top plays, and verifies they have all been checked in the database
    async def scan_top(self):
        friends = await self.database.get_all_friends()
        for friend in friends:
            friend_data = await self.osu.get_user_scores(friend[1])
            for score in friend_data:
                await self.check_beatmap(score, True)

    ## Checks a single user (When a new user is added as a friend) - their top plays are checked to see if the database has scanned them prior.
    async def scan_single_top(self, userid):
        friend_data = await self.osu.get_user_scores(userid)
        for score in friend_data:
            await self.check_single_beatmap(score)

    ## Checks that the play is a new snipe that has never happened before
    async def verify_user(self, play):
        if not(await self.database.get_user_snipe(play['user']['id'], play['beatmap']['id'])): # if this user doesnt have a snipe on the beatmap
            if not(await self.database.get_user_sniped(play['user']['id'], play['beatmap']['id'])): # and they have also never been sniped on the beatmap
                if not(await self.database.get_user_beatmap_play_score(play['user']['id'], play['beatmap']['id'], play['score'])):
                    await self.database.add_score(play['user_id'], play['beatmap']['id'], play['score'], 0)
                    return True
        return False

    ## When given a play, it checks if the beatmap is already in the database or not (Specific User Passive Tracking - for newly added friends -)
    async def check_beatmap(self, play, friend): # passive tracking
        if not(await self.database.get_beatmap(str(play['beatmap']['id']))): # if beatmap isnt in the db
            await self.database.add_beatmap(str(play['beatmap']['id']), play['beatmapset']['artist'], play['beatmapset']['title'], play['beatmap']['version'], play['beatmap']['url'], play['beatmap']['difficulty_rating'], play['beatmap']['total_length'],play['beatmap']['bpm'])
            await self.add_snipes(play, friend)
        else: # if the beatmap is in the database
            if await self.verify_user(play):
                await self.add_snipes(play, friend) # also do passive tracking

    ## Same as check_beatmap, but it only checks a single play, and then scans all users for that beatmap (General Passive Tracking)
    async def check_single_beatmap(self, play):
        play2 = play
        play = await self.osu.get_score_data(play['beatmap']['id'], play['user']['id'])
        if not(await self.database.get_beatmap(str(play2['beatmap']['id']))): # if beatmap isnt in the db
            await self.database.add_beatmap(str(play2['beatmap']['id']), play2['beatmapset']['artist'], play2['beatmapset']['title'], play2['beatmap']['version'], play2['beatmap']['url'],play2['beatmap']['difficulty_rating'], play2['beatmap']['total_length'],play2['beatmap']['bpm'])
            await self.add_single_snipe(play)
        else:
            if await self.verify_user(play2):
                await self.add_single_snipe(play) # also do passive tracking

    async def check_specific_beatmap(self, beatmap_id):
        print(f"Checking Beatmap {beatmap_id}")
        main_users = await self.database.get_all_users()
        beatmap_data = await self.osu.get_beatmap(beatmap_id)
        await self.database.add_beatmap(beatmap_data['id'], beatmap_data['beatmapset']['artist'], beatmap_data['beatmapset']['title'], beatmap_data['version'], beatmap_data['url'], beatmap_data['difficulty_rating'], beatmap_data['total_length'], beatmap_data['bpm'])
        for i, main_user in enumerate(main_users):
            if i == 0:
                main_user_play = await self.osu.get_score_data(beatmap_id, main_user[1])
                if main_user_play:
                    main_user_play['score']['beatmapset'] = beatmap_data['beatmapset']
                    await self.add_new_beatmap_snipes(main_user_play)
            else:
                pass

    ## When given a play, it checks ALL users for snipes on that map, without specific comparison to that user. This contains both active and passive snipes
    async def add_snipes(self, play, friendstatus):
        skip_friends = []        
        main_users = await self.database.get_all_users()
        for _, user in enumerate(main_users):
            is_friend = False # Initialise as false
            main_play = await self.osu.get_score_data(play['beatmap']['id'], user[1])
            if main_play:
                main_user_friends = await self.database.get_user_friends(user[1])
                all_friends = await self.database.get_all_friends()
                main_date = await self.convert_date(main_play['score']['created_at'])
                for main_friend in main_user_friends: # Only check friends of the main user (I think lmao)
                    friend = main_friend
                    if str(main_friend[1]) == str(play['user']['id']):
                        friend_play = await self.osu.get_score_data(play['beatmap']['id'], friend[1])
                        if friend_play: 
                            friend_date = await self.convert_date(friend_play['score']['created_at'])
                            if await self.date_more_recent_than(friend_date, main_date):
                                if friend_play['score']['score'] > main_play['score']['score']:
                                    if not(await self.database.get_user_snipes(friend[1], play['beatmap']['id'], user[1])):
                                        if str(play['user']['id']) == str(friend[1]) and str(play['score']) == str(friend_play['score']['score']) and friendstatus is False and str(self.new_user) != str(play['user']['id']):
                                            if not(await self.database.get_user_snipe_on_beatmap(friend_play['score']['user']['id'], main_play['score']['beatmap']['id'], main_play['score']['user']['id'])):
                                                await self.post_friend_snipe(main_play['score'], friend_play['score'], (user[1],))
                                        else:
                                            play_date = await self.convert_date(play['created_at'])
                                            # below if is if their snipe exists, but they have made a better snipe
                                            if await self.date_more_recent_than(play_date, friend_date) and str(play['user']['id']) == str(friend[1]) and str(self.new_user) != str(play['user_id']):
                                                if play['score'] > main_play['score']['score']:
                                                    ## Active snipe via database
                                                    await self.post_friend_snipe(main_play['score'], play, (user[1],))
                                            else:    
                                                ## Passive snipe via database
                                                print(f"        [1] Passive Snipe By {friend_play['score']['user']['username']} against {main_play['score']['user']['username']}")
                                                await self.database.add_snipe(friend[1], play['beatmap']['id'], user[1])
                                                if not(await self.database.get_user_beatmap_play_score(friend[1], play['beatmap']['id'], play['score'])):
                                                    await self.database.add_score(friend[1], play['beatmap']['id'], play['score'], 0)
                            else:
                                if main_play['score']['score'] > friend_play['score']['score']:
                                    if not(await self.database.get_user_snipes(user[1], play['beatmap']['id'], friend[1])):    
                                        if main_play['score']['score'] > play['score']:
                                            ## Passive snipe via global plays
                                            print(f"        [2] Passive Snipe By {main_play['score']['user']['username']} against {friend_play['score']['user']['username']}")
                                            await self.database.add_snipe(user[1], play['beatmap']['id'], friend[1])
                                            if not(await self.database.get_user_beatmap_play_score(user[1], play['beatmap']['id'], main_play['score']['score'])):
                                                await self.database.add_score(user[1], play['beatmap']['id'], main_play['score']['score'], 0)
                        else:
                            pass
                    else:
                        if not(await self.database.get_user_beatmap_play_with_zeros(friend[1], play['beatmap']['id'])):
                            print(f"        [3] Adding empty score for friend who hasnt played map")
                            await self.database.add_score(friend[1], play['beatmap']['id'], 0, 0)
                        skip_friends.append(friend[1])
        all_friends = await self.database.get_all_friends()
        for friend in all_friends: # now to check the score for all friends stored (even if theyre not the friend of the main user)
            if not(await self.database.get_user_beatmap_play_with_zeros(friend[1], play['beatmap']['id'])):
                print(f"        [4] Adding empty score for friend who hasnt played map for no main user")
                await self.database.add_score(friend[1], play['beatmap']['id'], 0, 0)
            else: # the user has got a play on the beatmap
                if friend[1] not in skip_friends:
                    friend_play = await self.osu.get_score_data(play['beatmap']['id'], friend[1])
                    if friend_play:
                        friend_score = friend_play['score']['score']
                        local_score = await self.database.get_user_beatmap_play(friend[1], play['beatmap']['id'])
                        if local_score is not None:
                            if friend_score > int(local_score[2]):
                                await self.database.replace_user_play(friend[1], play['beatmap']['id'], friend_play['score']['score'])
                                ## Non-snipe via global play
                                print(f"        [5] Updating score for user whos main user hasnt played the map")
                else:
                    ## Non-play via global play
                    print(f"        [6] Skipping user who hasnt played the map and has a 0 score stored")

    ## (for new added users) handles the passive snipes
    async def add_single_snipe(self, play):
        main_users = await self.database.get_all_users()
        for _, user in enumerate(main_users):
            main_play = await self.osu.get_score_data(play['score']['beatmap']['id'], user[1])
            if main_play:
                main_date = await self.convert_date(main_play['score']['created_at'])
                friend_play = play
                friend_date = await self.convert_date(friend_play['score']['created_at'])
                if await self.date_more_recent_than(friend_date, main_date):
                    if friend_play['score']['score'] > main_play['score']['score']:
                        if not(await self.database.get_user_snipes(play['score']['user']['id'], play['score']['beatmap']['id'], user[1])):
                            print(f"Adding passive snipe for new user against main user {play['score']['user']['username']}")
                            await self.database.add_snipe(play['score']['user']['id'], play['score']['beatmap']['id'], user[1])
                else:
                    if main_play['score']['score'] > friend_play['score']['score']:
                        if not(await self.database.get_user_snipes(user[1], play['score']['beatmap']['id'], play['score']['user']['id'])):
                            print(f"Adding passive snipe for main user against new user")
                            await self.database.add_snipe(user[1], play['score']['beatmap']['id'], play['score']['user']['id'])

    async def add_new_beatmap_snipes(self, play):
        main_users = await self.database.get_all_users()
        for _, user in enumerate(main_users):
            main_play = await self.osu.get_score_data(play['score']['beatmap']['id'], user[1])
            if main_play:
                print("Adding new main user score")
                await self.database.add_score(user[1], play['score']['beatmap']['id'], main_play['score']['score'], 0)
                main_date = await self.convert_date(main_play['score']['created_at'])
                friends = await self.database.get_user_friends(user[1])
                for friend in friends:
                    friend_play = await self.osu.get_score_data(play['score']['beatmap']['id'], friend[1])
                    if friend_play:
                        print("Adding new friend score")
                        await self.database.add_score(friend[1], play['score']['beatmap']['id'], friend_play['score']['score'], 0)
                        friend_date = await self.convert_date(friend_play['score']['created_at'])
                        if await self.date_more_recent_than(friend_date, main_date):
                            if friend_play['score']['score'] > main_play['score']['score']:
                                if not(await self.database.get_user_snipes(friend_play['score']['user']['id'], play['score']['beatmap']['id'], main_play['score']['user']['id'])):
                                    print(f"        [10] Adding passive snipe for friend against main user {play['score']['user']['username']}")
                                    await self.database.add_snipe(friend_play['score']['user']['id'], main_play['score']['beatmap']['id'], main_play['score']['user']['id'])
                        else:
                            if main_play['score']['score'] > friend_play['score']['score']:
                                if not(await self.database.get_user_snipes(play['score']['beatmap']['id'], play['score']['beatmap']['id'], friend_play['score']['user']['id'])):
                                    print(f"        [20] Adding passive snipe for main user against friend")
                                    await self.database.add_snipe(main_play['score']['user']['id'], play['score']['beatmap']['id'], friend_play['score']['user']['id'])
    

    ## gets the new users data, username, and the channel that requested them to be added, and runs all the scanning submethods
    async def add_new_user(self, user_data, ctx, username):
        beatmaps = await self.database.get_all_beatmaps()
        self.new_user = user_data
        await self.scan_single_top(user_data)
        for _, beatmap in enumerate(beatmaps):
            print("still scanning " + str(user_data))
            play = await self.osu.get_score_data(beatmap[0], user_data)
            if play:
                await self.add_single_snipe(play)
        self.new_user == ""
        await ctx.send(f"{username}'s plays have been scanned and scores are up to date.")

    ## Check beatmap submethod, but for a main user (so it passes false into add_snipes)
    async def check_main_beatmap(self, play):
        if not(await self.database.get_beatmap(play['beatmap']['id'])): # if beatmap isnt in the db
            await self.database.add_beatmap(play['beatmap']['id'], play['beatmapset']['artist'], play['beatmapset']['title'], play['beatmap']['version'], play['beatmap']['url'],play['beatmap']['difficulty_rating'], play['beatmap']['total_length'],play['beatmap']['bpm'])        
            await self.add_snipes(play, False)

    ## I think the osu api returns a weird ass version of datetime, so after the conversion this checks if one play is set more recently than another
    async def date_more_recent_than(self, date1, date2):
        if date1['year'] == date2['year']:
            if date1['month'] == date2['month']:
                if date1['day'] == date2['day']:
                    if date1['hour'] == date2['hour']:
                        if date1['minute'] == date2['minute']:
                            if date1['second'] >= date2['second']:
                                return True
                        if date1['minute'] > date2['minute']:
                            return True
                    if date1['hour'] > date2['hour']:
                        return True
                if date1['day'] > date2['day']:
                    return True
            if date1['month'] > date2['month']:
                return True
        if date1['year'] > date2['year']:
            return True
        else:
            return False

    ## converts the date from unepic osu datetime to much better dictionary :)
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

    async def check_main_play(self, play, user_id, user_data):
        await self.check_main_beatmap(play)
        user_play = await self.database.get_user_beatmap_play(user_id, f"{play['beatmap']['id']}")
        online_play = await self.osu.get_score_data(play['beatmap']['id'], user_id)
        if user_play:
            if online_play:
                if play['score'] > int(user_play[2]):
                    await self.database.replace_user_play(user_play[0], user_play[1], play['score'])
                    if play['score'] >= online_play['score']['score']:
                        sniped_friends = await self.get_sniped_friends(play)
                        discord_channel = await self.database.get_main_discord(user_id)
                        channel = self.bot.get_channel(int(discord_channel[0]))
                        print(f"Posting new best for {user_data['username']}")
                        await channel.send(embed=create_score_embed(play, sniped_friends))
                        friends = await self.database.get_all_friends()
                        main_users = await self.database.get_all_users()
                        for friend in friends:
                            if friend[1] in sniped_friends:
                                for main_user in main_users:
                                    if str(main_user[1]) == str(friend[1]):
                                        friend_play = await self.osu.get_score_data(play['beatmap']['id'], play["user_id"])
                                        await self.post_friend_snipe(play, friend_play['score'], play['user_id'])
        else:
            await self.database.add_score(str(user_data['id']), str(
                play['beatmap']['id']), str(play['score']), 0)
            if online_play:
                if play['score'] >= online_play['score']['score']:    
                    sniped_friends = await self.get_sniped_friends(play)
                    discord_channel = await self.database.get_main_discord(user_id)
                    channel = self.bot.get_channel(int(discord_channel[0]))
                    print(f"Posting new best for {user_data['username']}")
                    await channel.send(embed=create_score_embed(play, sniped_friends))

    async def check_duplicate_friends(self, friends):
        ## Check for duplicates in the friends list
        for i, friend in enumerate(friends):
            friend_counter = 0
            for _, jfriend in enumerate(friends):
                if friend[1] == jfriend[1]:
                    friend_counter += 1
            if friend_counter > 1:
                friends.pop(i)
        ## Then check if any of the friends are a main user, and prune them if they are
        main_users = await self.database.get_all_users()
        for main_user in main_users:
            for i, friend in enumerate(friends):
                if main_user[1] == friend[1]:
                    friends.pop(i)
        return friends

    @tasks.loop(seconds=30.0)
    async def tracker_loop(self):
        # await self.scan_top() # UNCOMMENT THIS WHEN RESETTING EVERYTHING AND RUN ONCE
        start_time = time.time()
        users = await self.database.get_all_users()
        for data in users:
            user_id = f"{data[1]}"
            user_data = await self.osu.get_user_data(user_id)
            if user_data:
                recent_plays = await self.osu.get_recent_plays(user_id)
                print(f"     checking main user {user_data['username']}")
                if recent_plays:
                    for play in recent_plays:
                        await self.check_main_play(play, user_id, user_data)

        friends = await self.database.get_all_friends()
        # Dupe removal for friends since we dont need to check them twice as it scans every main user below
        # It also removes any main users, since they get checked in a different section of the program
        friends = await self.check_duplicate_friends(friends)
        for friend in friends:
            user_id = f"{friend[1]}"
            friend_data = await self.osu.get_user_data(user_id)
            if friend_data:
                print(f"     checking {friend_data['username']}")
                main_users = await self.database.get_all_users()
                ## Scans all main users here, which is why we dont need to check a user twice
                for main_user in main_users:
                    main_user_friends = await self.database.get_user_friends(main_user[1])
                    go_ahead = False
                    for main_friend in main_user_friends:
                        if str(user_id) == main_friend[1]:
                            go_ahead = True # lol
                    if go_ahead is True:
                        main_user = (main_user[1],)
                        main_user_id = f"{main_user[0]}"
                        recent_plays = await self.osu.get_recent_plays(user_id)
                        if recent_plays: # friend recent plays
                            for play in recent_plays: # For friends play in friends recent plays
                                beatmap_id = f"{play['beatmap']['id']}"
                                main_user_play = await self.osu.get_score_data(beatmap_id, main_user_id)#
                                if main_user_play:
                                    await self.check_beatmap(play, False)
                                    if int(play['score']) > int(main_user_play['score']['score']):
                                        if not await self.database.get_user_beatmap_play_score(play['user']['id'], play['beatmap']['id'], play['score']):
                                            if not(await self.database.get_user_beatmap_play(play['user']['id'], play['beatmap']['id'])):
                                                await self.database.add_score(str(friend_data['id']), str(play['beatmap']['id']), str(play['score']),0)
                                                if not(await self.database.get_user_snipe_on_beatmap(play['user']['id'], main_user_play['score']['beatmap']['id'], main_user_play['score']['user']['id'])) and str(self.new_user) != str(play['user']['id']):
                                                    await self.post_friend_snipe(main_user_play['score'], play, main_user)
                                                    main_users = await self.database.get_all_users()
                                                    for main_user in main_users:
                                                        if str(main_user[1]) == str(play['user']['id']):
                                                            sniped_friends = await self.get_sniped_friends(play)
                                                            print(f"Posting new best for {play['user']['username']}")
                                                            discord_channel = await self.database.get_main_discord(main_user[1])
                                                            channel = self.bot.get_channel(int(discord_channel[0]))
                                                            await channel.send(embed=create_score_embed(play, sniped_friends))
                                        
                                            else:
                                                local_play = await self.database.get_user_beatmap_play(play['user']['id'], play['beatmap']['id'])
                                                if play['score'] > int(local_play[2]):
                                                    friend_online_play = await self.osu.get_score_data(play['beatmap']['id'],friend_data['id'])
                                                    if str(play['score']) == str(friend_online_play['score']['score']):
                                                        await self.database.replace_user_play(play['user']['id'], play['beatmap']['id'], play['score'])
                                                        if not(await self.database.get_user_snipe_on_beatmap(play['user']['id'], main_user_play['score']['beatmap']['id'], main_user_play['score']['user']['id'])) and str(self.new_user) != str(play['user']['id']):
                                                            await self.post_friend_snipe(main_user_play['score'], play, main_user)
                                    elif int(play['score']) == int(main_user_play['score']['score']):
                                        if str(play['user']['id'] == main_user_id):
                                            # play is by a main user on another server
                                            user_data = await self.osu.get_user_data(play['user']['id'])
                                            user_id = play['user']['id']
                                            await self.check_main_play(self, play, user_id, user_data)
                    if len(main_user) == 1:
                        main_user = (main_user[0], 0)
                    if main_user[1] == user_id: # if the friend is the same person as a main user
                        main_user = (main_user[1],)
                        main_user_id = f"{main_user[0]}"
                        recent_plays = await self.osu.get_recent_plays(user_id)
                        if recent_plays:
                            for play in recent_plays:
                                beatmap_id = f"{play['beatmap']['id']}"
                                main_user_play = await self.osu.get_score_data(beatmap_id, main_user_id)
                                if main_user_play:
                                    if int(play['score']) == int(main_user_play['score']['score']):
                                        if str(play['user']['id'] == main_user_id):
                                            # play is by a main user on another server
                                            user_data = await self.osu.get_user_data(play['user']['id'])
                                            user_id = play['user']['id']
                                            await self.check_main_play(play, user_id, user_data)

        print(f"Snipe loop took {round(time.time() - start_time, 2)} seconds")

    ## method that takes in the main users global play, and their local play, and from that info adds the snipes to database, and posts the embed to discord
    async def post_friend_snipe(self, main_user_play, play, main_user):
        main_user_username = main_user_play['user']['username']
        if not(await self.database.get_user_snipe_on_beatmap(play['user']['id'], play['beatmap']['id'], main_user[0])):
            await self.database.add_snipe(play['user']['id'], play['beatmap']['id'], main_user[0])
        discord_channel = await self.database.get_main_discord(main_user[0])
        channel = await self.bot.fetch_channel(discord_channel[0])
        print(f"Posting snipe by {play['user']['username']} against {main_user_username}")
        beatmap_data = await self.osu.get_beatmap(main_user_play['beatmap']['id'])
        await channel.send(embed=create_snipe_embed(play, main_user_username, beatmap_data))


    @tracker_loop.before_loop
    async def before_tracker(self):
        await self.bot.wait_until_ready()
