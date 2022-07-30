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
        lengths = []
        ids = []
        song_names = []
        guest_diffs = []
        beatmapsets = []
        mappers = []
        gd_beatmapsets = {}
        hosts = 0
        gds = 0
        user_data = await self.osu.get_user_data(user)
        user_id = str(user_data['id'])
        scores = await self.database.get_all_scores(user_id)
        beatmaps = await self.database.get_all_beatmaps()
        scoreids = []
        for score in scores:
            if score[1] not in scoreids:
                scoreids.append(score[1])
        scores = scoreids
        for j, beatmap in enumerate(beatmaps):
            if beatmap[0] in scores:
                if beatmap[0] not in ids:
                    if float(beatmap[5]) > 0.0:
                        stars.append(float(beatmap[5]))
                    if int(beatmap[6]) > 0:
                        lengths.append(int(beatmap[6]))

                if beatmap[1] in artists and beatmap[2] not in song_names:
                    beatmapsets.append(beatmap[9])
                    artists.append(beatmap[1])
                    song_names.append(beatmap[2])
                    ids.append(beatmap[0])
                    guest_diff = False
                    mappers.append(str(beatmap[8]))

                elif beatmap[9] not in beatmapsets:
                    artists.append(beatmap[1])
                    beatmapsets.append(beatmap[9])
                    song_names.append(beatmap[2])
                    ids.append(beatmap[0])
                    mappers.append(str(beatmap[8]))

                guest_diff = False
                for stri in beatmap[3]:
                        if stri == "'":
                            guest_diff = True
                guest_name = beatmap[3].split("'")[0]
                if guest_diff == True:
                    guest_diffs.append(guest_name)
                    g = True
                    for bid in gd_beatmapsets:
                        if gd_beatmapsets[bid] == guest_name and bid == beatmap:
                            g = False
                    if g is True:
                        gd_beatmapsets[beatmap[9]] = guest_name
                        mappers.append(guest_name)

        numarray = []
        artist_count = []
        num = "none"
        best_count = 0
        count = []
        check = []
        for j in range(0,10):
            counter = 0
            for i in artists:
                curr_frequency = artists.count(i)
                if(curr_frequency> counter):
                    counter = curr_frequency
                    num = i
                    if j == 0:
                        best_count = counter
                        song = song_names[(artists.index(i))]
            numarray.append(num)
            artist_count.append(counter)
            
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
                best_count = curr_frequency
            elif curr_frequency == counter:
                most_frequent.append(s)

        random_num = random.randint(0, len(most_frequent))
        if random_num == len(most_frequent):
            random_num = random_num-1
        song = most_frequent[random_num]
        counter = 0
        gd_freq = 0
        for gd in guest_diffs:
            curr_frequency = guest_diffs.count(gd)
            if curr_frequency > counter:
                counter = curr_frequency
                most_gd = gd
                gd_freq = counter

        counter = 0
        mapper_freq = 0
        for gd in mappers:
            curr_frequency = mappers.count(gd)
            if curr_frequency > counter:
                counter = curr_frequency
                most_mapper = gd
                mapper_freq = counter

        difficulty = 0.0
        for star in stars:
            difficulty = difficulty + float(star)
        diff = difficulty / float(len(stars))
        maps = len(stars)

        av_len = 0
        for length in lengths:
            av_len = av_len + length
        av_len = av_len / len(lengths)

        gds = guest_diffs.count(most_mapper)
        hosts = mapper_freq - gds

        embed = await self.embed.create_stats_embed(numarray, diff, song, user_data, most_gd, best_count, artist_count, gd_freq, maps, av_len, most_mapper, mapper_freq, gds, hosts)
        await ctx.send(embed=embed)

    @stats.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-stats "username"`')


def setup(client):
    client.add_cog(Stats(client))
