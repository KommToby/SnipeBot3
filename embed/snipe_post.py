from osu.osu_auth import OsuAuth
import discord


class SnipePost():
    def __init__(self):
        self.auth = OsuAuth()

    async def snipepost(self, play, client, discord_channel, main_user):
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
                        pp = str(play['pp'])

                    # TITLE MESSAGE HANDLING
                    title_message = str(
                        play['user']['username']) + " just sniped " + main_user + " with " + modstr + "!"

                    # SCORE MESSAGE HANDLING
                    score_message = "score: " + str(play['score']) + " | acc: "+str(
                        round((float(play['accuracy'])*100), 2)) + "% | combo: " \
                        + str(play['max_combo']) + "x | pp: " \
                        + str(pp) + "pp"

                    # USER AVATAR HANDLING
                    if play['user']['avatar_url'][0] == "/":
                        image = "https://osu.ppy.sh" + \
                            str(play['user']['avatar_url'])
                    else:
                        image = str(play['user']['avatar_url'])

                    # Now post the embed
                    print("Posting " + str(play['user']['username']) + "'s snipe against " + main_user)
                    embed = discord.Embed(
                        title=title_message,
                        description=str(play['beatmapset']['artist']+" - "+str(
                            play['beatmapset']['title'])
                            + "  ["+str(play['beatmap']['version'])+"] - "+str(play['beatmap']['difficulty_rating'])+":star:"),
                        color=discord.Colour.green()
                    )
                    embed.set_thumbnail(
                        url=play['beatmapset']['covers']['list@2x'])
                    embed.set_author(
                        name='Snipebot 3 by Komm', icon_url=str(image))

                    embed.add_field(
                        name=score_message, value="[link to map]("
                        + str(play['beatmap']['url'])
                        + ")", inline=False)

                    await channel.send(embed=embed)

                    # then post the pings afterwards
