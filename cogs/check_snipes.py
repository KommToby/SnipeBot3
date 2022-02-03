import discord
from discord.ext import commands
from snipebot import DATABASE, AUTH, snipe_bot_tracker
import asyncio
import time

# USE THIS WHEN NEW USERS ARE ADDED
class CheckSnipes(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.osu = AUTH
        self.main_database = DATABASE

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def checksnipes(self, ctx):
        if str(ctx.message.author.id) == "150313781673721856":

            all_main_scores = await self.database.get_scores()
            all_main_snipes = await self.database.get_all_snipes()
            all_scores = await self.main_database.get_scores()
            all_snipes = await self.main_database.get_all_snipes()

            #snipes first
            for main_snipe in all_main_snipes:
                if main_snipe not in all_snipes:
                    await self.main_database.add_snipe(main_snipe[0], main_snipe[1], main_snipe[2])

            #then scores
            for main_score in all_main_scores:
                if main_score not in all_scores:
                    await self.main_database.add_score(main_score[0], main_score[1], main_score[2], main_score[3])

            starttime = time.time()
            beatmaps = await self.main_database.get_all_beatmaps()
            scores = await self.main_database.get_scores()
            snipes = await self.main_database.get_all_snipes()
            main_user = await self.main_database.get_main_from_discord(ctx.channel.id)
            main_user = main_user[0]
            friends = await self.main_database.get_user_friends(ctx.channel.id)
            print("checking scores")
            for i, beatmap in enumerate(beatmaps):
                print("checking next beatmap...")
                for j, friend in enumerate(friends):
                    if j==0:
                        print(f"[{i} / {len(beatmaps)}]   still alive")
                    if i % 50 == 0 and j == 0:
                        await ctx.send(f"{(round(((i/len(beatmaps))*100), 2))}% Complete...")
                    if i >= 0:
                        friend_score = await self.osu.get_score_data(beatmap[0], friend[1])
                        if friend_score:
                            if not(await self.main_database.get_user_snipes(friend[1], beatmap[0], main_user)):
                                if not(await self.main_database.get_user_snipes(main_user, beatmap[0], friend[1])):
                                    if await self.main_database.get_user_scores_with_zeros(friend[1]):
                                        local_score = await self.main_database.get_user_beatmap_play_with_zeros(friend[1], beatmap[0])
                                        if local_score:
                                            if str(local_score[2]) != str(friend_score['score']['score']):
                                                print(f"updating friend score for {friend_score['score']['user']['username']}")
                                                await self.database.replace_user_play(friend[1], beatmap[0], friend_score['score']['score'])
                                                if not(await self.main_database.get_user_snipes(friend[1], beatmap[0], main_user)):
                                                    if not(await self.main_database.get_user_snipes(main_user, beatmap[0], friend[1])):
                                                        await self.add_single_snipe(friend_score)
                                            else:
                                                if not(await self.main_database.get_user_beatmap_play_score(friend[1], beatmap[0], "0")):
                                                    if await snipe_bot_tracker.verify_user(friend_score['score']):
                                                        print(f"adding snipes for map")
                                                        await self.add_single_snipe(friend_score)
                                        else:
                                            pass
                                    else:
                                        print(f"adding friend score for {friend_score['score']['user']['username']}")
                                        await self.database.add_score(friend[1], beatmap[0], friend_score['score']['score'], 0)
                                        if not(await self.main_database.get_user_snipes(friend[1], beatmap[0], main_user)):
                                                if not(await self.main_database.get_user_snipes(main_user, beatmap[0], friend[1])):
                                                    await self.add_single_snipe(friend_score)
                        else:
                            if not(await self.main_database.get_user_beatmap_play_score(friend[1], beatmap[0], "0")):
                                print(f"adding empty score for friend")
                                await self.database.add_score(friend[1], beatmap[0], 0, 0)

                # now check the same for the main user
                if not(await self.main_database.get_user_beatmap_play_with_zeros(main_user, beatmap[0])):
                    main_user_play = await self.osu.get_score_data(beatmap[0], main_user)
                    if main_user_play:
                        print(f"adding main score for {main_user_play['score']['user']['username']}")
                        await self.database.add_score(main_user, beatmap[0], main_user_play['score']['score'], 0)
                    else:
                        if not(await self.main_database.get_user_beatmap_play_score(main_user, beatmap[0], "0")):
                        # this will speed it up in the future
                            print(f"adding empty score for main user")
                            await self.database.add_score(main_user, beatmap[0], 0, 0)
            all_main_scores = await self.database.get_scores()
            all_main_snipes = await self.database.get_all_snipes()
            all_scores = await self.main_database.get_scores()
            all_snipes = await self.main_database.get_all_snipes()

            #snipes first
            for main_snipe in all_main_snipes:
                if main_snipe not in all_snipes:
                    await self.main_database.add_snipe(main_snipe[0], main_snipe[1], main_snipe[2])

            #then scores
            for main_score in all_main_scores:
                if main_score not in all_scores:
                    await self.main_database.add_score(main_score[0], main_score[1], main_score[2], main_score[3])

            await ctx.send("Score list has been updated successfully")
        else:
            await ctx.send(f"You do not have permissions for that command")

    @checksnipes.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-checksnipes`') 

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

def setup(client):
    client.add_cog(CheckSnipes(client))