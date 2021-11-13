import discord
from discord.ext import commands

from snipebot import AUTH


def create_profile_embed(user_id: str):
    user = await AUTH.get_user_data(user_id)
    embed = discord.Embed(
        title=f"osu! profile for {user['username']}",
        color=discord.Colour.red()
    )
    embed.description = \
        f"""**Rank**: {user['statistics']['global_rank']}
**Country Rank**: {user['statistics']['country_rank']}
**Accuracy**: {round(user['statistics']['hit_accuracy'], 2)}%
"""
    embed.set_author(name="Snipebot 3 by Komm",
                     icon_url=f"https://osu.ppy.sh/images/flags/{user['country_code']}.png")
    if user['avatar_url'][0] == "/":
        embed.set_thumbnail(url=f"https://osu.ppy.sh{user['avatar_url']}")
    else:
        embed.set_thumbnail(url=user['avatar_url'])
    if user['cover_url']:
        embed.set_image(url=user["cover_url"])
    return embed


def create_snipe_embed(play, main_user):
    # MOD HANDLING
    if play['mods']:
        modstr = ""
        for mod in play['mods']:
            modstr += mod
    else:
        modstr = "No Mods"

    # PP HANDLING
    if not play['pp']:
        pp = "No "
    else:
        pp = f"{play['pp']}"

    # TITLE MESSAGE HANDLING
    title_message = f"{play['user']['username']} just sniped {main_user} with {modstr}!"

    # SCORE MESSAGE HANDLING
    score_message = f"score: {play['score']} | acc: {round((float(play['accuracy']) * 100), 2)}%" + \
                    f"| combo: {play['max_combo']}x | pp: {pp}pp"

    # USER AVATAR HANDLING
    if play['user']['avatar_url'][0] == "/":
        image = "https://osu.ppy.sh" + \
                str(play['user']['avatar_url'])
    else:
        image = str(play['user']['avatar_url'])

    embed = discord.Embed(
        title=title_message,
        description=f"{play['beatmap']['artist']} - {play['beatmapset']['title']} [{play['beatmap']['version']}]" +
                    f" - {play['beatmap']['difficulty_rating']}:star:",
        colour=discord.Colour.green()
    )

    embed.set_thumbnail(url=play['beatmapset']['covers']['list@2x'])

    embed.set_author(name='Snipebot 3 by Komm', icon_url=str(image))

    embed.add_field(
        name=score_message, value="[link to map]("
                                  + str(play['beatmap']['url'])
                                  + ")", inline=False)
    return embed


def create_score_embed(play, sniped_friends):
    # MOD HANDLING
    if play['mods']:
        modstr = ""
        for mod in play['mods']:
            modstr += mod
    else:
        modstr = "No Mods"

    # PP HANDLING
    if not play['pp']:
        pp = "No "
    else:
        pp = f"{play['pp']}"

    title_message = f"{play['user']['username']} just got a new high score with {modstr}!"

    score_message = f"score: {play['score']} | acc: {round((float(play['accuracy']) * 100), 2)}%" + \
                    f"| combo: {play['max_combo']}x | pp: {pp}pp"

    # NUMBER OF FRIENDS SNIPED HANDLING
    if not sniped_friends:
        friend_message = "`nobody`"
        friend_num_message = "no friends sniped :c"
    else:
        friend_num_message = f"{len(sniped_friends)} friend(s) sniped!"
        friend_message = f"`{','.join(sniped_friends[:4])}{' and more!' if len(sniped_friends) > 4 else ''}`"

    # USER AVATAR HANDLING
    if play['user']['avatar_url'][0] == "/":
        image = "https://osu.ppy.sh" + \
                str(play['user']['avatar_url'])
    else:
        image = str(play['user']['avatar_url'])

    embed = discord.Embed(
        title=title_message,
        description=f"{play['beatmap']['artist']} - {play['beatmapset']['title']} [{play['beatmap']['version']}]" +
                    f" - {play['beatmap']['difficulty_rating']}:star:",
        colour=discord.Colour.red()
    )

    embed.set_thumbnail(url=play['beatmapset']['covers']['list@2x'])

    embed.set_author(name='Snipebot 3 by Komm', icon_url=str(image))

    if sniped_friends:
        embed.add_field(name=friend_num_message, value=friend_message, inline=False)

    embed.add_field(
        name=score_message,
        value=f"[link to map]({play['beatmap']['url']})",
        inline=False
    )

    return embed
