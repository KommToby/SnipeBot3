from embed.create_embeds import create_profile_embed
from snipebot import AUTH, DATABASE
from discord.ext import commands
from embed import create_embeds
import random


class Stats(commands.Cog):  # must have commands.cog or this wont work
    def __init__(self, client):
        self.client = client
        self.osu = AUTH
        self.database = DATABASE
        self.embed = create_embeds

    @commands.command()
    async def stats(self, ctx, user: str):
        artists = []
        stars = []
        ids = []
        song_names = []
        guest_diffs = []
        user_data = await self.osu.get_user_data(user)
        user_id = str(user_data['id'])
        scores = await self.database.get_all_scores(user_id)
        beatmaps = await self.database.get_all_beatmaps()
        for i, score in enumerate(scores):
            for j, beatmap in enumerate(beatmaps):
                if score[1] == beatmap[0] and score[2] != "0":
                    if beatmap[0] not in ids:
                        if float(beatmap[5]) > 0.0:
                            stars.append(float(beatmap[5]))
                    if beatmap[1] in artists and beatmap[2] not in song_names:
                        artists.append(beatmap[1])
                        song_names.append(beatmap[2])
                        ids.append(beatmap[0])
                        guest_diff = False
                    elif beatmap[1] not in artists:
                        artists.append(beatmap[1])
                        song_names.append(beatmap[2])
                        ids.append(beatmap[0])

                    guest_diff = False
                    for stri in beatmap[3]:
                            if stri == "'":
                                guest_diff = True
                    if guest_diff == True:
                        guest_diffs.append(beatmap[3].split("'")[0])

        numarray = []
        num = "none"
        for j in range(0,10):
            counter = 0
            for i in artists:
                curr_frequency = artists.count(i)
                if(curr_frequency> counter):
                    counter = curr_frequency
                    num = i
                    if j == 0:
                        song = song_names[(artists.index(i))]
            numarray.append(num)
            
            old_artists = artists
            artists = []
            for p, i in enumerate(old_artists):
                if i == num:
                    pass
                else:
                    artists.append(i)

        counter = 0
        most_frequent = []
        for s in song_names:
            curr_frequency = song_names.count(s)
            if curr_frequency > counter:
                most_frequent = []
                counter = curr_frequency
                most_frequent.append(s)
            elif curr_frequency == counter:
                most_frequent.append(s)

        random_num = random.randint(0, len(most_frequent))
        song = most_frequent[random_num]

        counter = 0
        for gd in guest_diffs:
            curr_frequency = guest_diffs.count(gd)
            if curr_frequency > counter:
                counter = curr_frequency
                most_gd = gd

        difficulty = 0.0
        for star in stars:
            difficulty = difficulty + float(star)
        diff = difficulty / float(len(stars))

        # string = f"\n__**ok fine this is {user_data['username']}'s top 10 most played artists or whatever**__\n```\n"
        # for artist in numarray:
        #     string = string + artist +"\n"
        # string = string + f"```\n ok and your average sr of all ur stored plays is `{round(diff, 2)}` wow good job\nAND your most played song is `{song}` lol"
        # await ctx.send(string)

        embed = await self.embed.create_stats_embed(numarray, diff, song, user_data, most_gd)
        await ctx.send(embed=embed)

    @stats.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-stats "username"`')


def setup(client):
    client.add_cog(Stats(client))
