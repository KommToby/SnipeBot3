from osu.osu_auth import OsuAuth
import discord
import sys


class ScorePost():
    def __init__(self):
        self.auth = OsuAuth()

    async def scorepost(self, play, sniped_friends, client, discord_channel):
        for server in client.guilds:
            for channel in server.channels:
                if str(channel.id) == discord_channel[0]:
                    # MOD HANDLING
                    if len(play['mods']) > 0:
                        modstr = ""
                        for k, _ in enumerate(play['mods']):
                            modstr += play['mods'][k]
                    else:
                        modstr = "No Mod"

                    # PP HANDLING
                    if play['pp'] is None:
                        pp = "No "
                    else:
                        pp = play['pp']

                    # TITLE MESSAGE HANDLING
                    title_message = str(
                        play['user']['username']) + "just got a new high score with " + modstr + "!"

                    # SCORE MESSAGE HANDLING
                    score_message = "score: " + str(play['score']) + " | acc: "+str(
                        round((float(play['accuracy'])*100), 2)) + "% | combo: " \
                        + str(play['max_combo']) + "x | pp: " \
                        + str(pp) + "pp"

                    # NUMBER OF FRIENDS SNIPED HANDLING
                    if len(sniped_friends) == 0:
                        friend_message = "`nobody`"
                        friend_num_message = "no friends sniped :c"
                    else:
                        friend_num_message = str(
                            len(sniped_friends)) + " friend(s) sniped!"
                        friend_message = "`"
                        for j, friend in enumerate(sniped_friends):
                            if j == len(sniped_friends)-1 and len(sniped_friends) < 4:
                                friend_message += str(friend)
                            elif j < 3:
                                friend_message += str(friend) + ","
                            elif j == 3:
                                friend_message += " and more!"
                            friend_message += "`"

                    # USER AVATAR HANDLING
                    if play['user']['avatar_url'][0] == "/":
                        image = "https://osu.ppy.sh" + \
                            str(play['user']['avatar_url'])
                    else:
                        image = str(play['user']['avatar_url'])

                    # Now post the embed
                    print("Posting new high score for " +
                        str(play['user']['username']))
                    embed = discord.Embed(
                        title=title_message,
                        description=str(play['beatmapset']['artist']+" - "+str(
                            play['beatmapset']['title'])
                            + "  ["+str(play['beatmap']['version'])+"] - "+str(play['beatmap']['difficulty_rating'])+":star:"),
                        color=discord.Colour.red()
                    )
                    embed.set_thumbnail(
                        url=play['beatmapset']['covers']['list@2x'])
                    embed.set_author(
                        name='Snipebot 3 by Komm', icon_url=str(image))

                    if len(sniped_friends) != 0:
                        embed.add_field(name=friend_num_message,
                            value=friend_message, inline=False)

                    embed.add_field(
                        name=score_message, value="[link to map]("
                        + str(play['beatmap']['url'])
                        + ")", inline=False)

                    await channel.send(embed=embed)

                    # then post the pings afterwards
