import discord
from discord.ext import commands
import random

async def create_friend_leaderboard(leaderboard, main_user_name, main_snipes, main_sniped):
    title_message = "Snipe Leaderboard for " + main_user_name + ": " + str(main_snipes) + " | " + str(main_sniped)
    embed = discord.Embed(
        title=title_message,
        color=discord.Colour.purple()
    )    

    friend_message = ""
    for i, friend in enumerate(leaderboard):
        if i <= 9:
            weight_difference = round(float(friend['snipe difference']), 2) - round(float(friend['local_weight']), 2)
            if weight_difference >=0:
                weight_string = "+" + str(round(weight_difference,2))
            else:
                weight_string = str(round(weight_difference,2))

            friend_message = str(i+1) + ": " + friend['username']
            friend_description = "**Snipes: " + str(friend['snipes']) + \
                " | Sniped: " + \
                str(friend['sniped']) + " | Snipe PP: " + \
                str(round(friend['snipe difference'], 2)) + "** (" + weight_string + ")"
            embed.add_field(name=friend_message,
                            value=friend_description, inline=False)
    return embed  

async def create_snipelist_embed(beatmaps, username, links, user):
    while len(beatmaps) > 10:
        index = random.randint(0, len(beatmaps)-1)
        beatmaps.pop(index)
        links.pop(index)
    send_message = "**__Scores that "+str(username)+" has not sniped back__**\n"  
    
    embed = discord.Embed(
        title=send_message,
        color=discord.Color.orange()
    )
    for i, beatmap in enumerate(beatmaps):
        embed.add_field(name=str(i+1) + ". " + str(beatmap), value="[Link to map](" + str(links[i]) + ")", inline=False)
    if user['cover_url']:
        embed.set_image(url=user["cover_url"])
    if user['avatar_url'][0] == "/":
        thumbnail = f"https://osu.ppy.sh{user['avatar_url']}"
    else:
        thumbnail = user['avatar_url']
    embed.set_author(name='Snipebot 3 by Komm', icon_url=thumbnail)
    return embed

async def create_snipeback_embed(beatmaps, username, links, user):
    while len(beatmaps) > 10:
        index = random.randint(0, len(beatmaps)-1)
        beatmaps.pop(index)
        links.pop(index)
    send_message = "**__Scores that main user needs to snipe "+str(username)+" back on__**\n"  
    
    embed = discord.Embed(
        title=send_message,
        color=discord.Color.orange()
    )
    for i, beatmap in enumerate(beatmaps):
        embed.add_field(name=str(i+1) + ". " + str(beatmap), value="[Link to map](" + str(links[i]) + ")", inline=False)
    if user['cover_url']:
        embed.set_image(url=user["cover_url"])
    if user['avatar_url'][0] == "/":
        thumbnail = f"https://osu.ppy.sh{user['avatar_url']}"
    else:
        thumbnail = user['avatar_url']
    embed.set_author(name='Snipebot 3 by Komm', icon_url=thumbnail)
    return embed

async def create_recommendation_embed2(beatmaps, user_data, links, ctx):
    index = random.randint(0, len(beatmaps)-1)
    send_message = "**__Random map recommendation for "+str(user_data['username'])+"__**\n"

    embed = discord.Embed(
        title=send_message,
        color=discord.Color.purple()
    )
    embed.add_field(name=str(beatmaps[index]), value="[Link to map]("+(str(links[index]))+")")
    return embed

async def create_recommendation_embed(friend, user_data, beatmap, link):
    if friend == "bestnum":
        send_message = "**__(up to) 9 best map recommendations for "+str(user_data['username'])+"__**\n"
        embed = discord.Embed(
            title=send_message,
            color=discord.Color.purple()
        )
        for i, beatmap_string in enumerate(beatmap):
            embed.add_field(name=str(beatmap_string), value="[Link to map]("+(str(link[i]))+")", inline=False)
        return embed
    else:
        if friend == "largestnum":
            send_message = "**__map recommendation for "+str(user_data['username'])+"__**\n"
        else:
            send_message = "**__Random map recommendation for "+str(user_data['username'])+" played by "+str(friend)+"__**\n"

        embed = discord.Embed(
            title=send_message,
            color=discord.Color.purple()
        )
        if friend == "largestnum" or friend == "bestnum":
            embed.add_field(name=str(beatmap), value="[Link to map]("+(str(link))+")")
        else:
            embed.add_field(name=str(beatmap), value="[Link to map]("+(str(link))+")")
        return embed

async def create_snipes_embed(user, snipes, sniped, total, play, sniped_play, position, score, not_sniped, not_sniped_main):
    snipes = len(snipes)
    sniped = len(sniped)
    total = len(total)
    snipe_difference = snipes - sniped
    snipe_percentage = round(((snipes/total)*100), 2)

    # AVATAR HANDLING
    if user['avatar_url'][0] == "/":
        image = "https://osu.ppy.sh" + \
                str(user['avatar_url'])
    else:
        image = str(user['avatar_url'])    

    # FLAG HANDLING
    flag = "https://osu.ppy.sh/images/flags/" + \
    user['country_code']+".png"

    titlemessage = f"Snipe Stats For {user['username']} (#{position+1})"
    if sniped == 0:
        sniped = ('0')
    description = "**● Number of Snipes: **" + \
        str(snipes) + "\n" + "**○ Times Sniped: **" + str(sniped) + \
        "\n▻ **Snipe Difference: **" + \
        str(snipe_difference) + \
        "\n► **Snipe PP: **" + \
        str(score) + \
        "\n⯀ **Held Snipes: **" + \
        str(not_sniped) + \
        "\n☐ **To-Snipe: **" + \
        str(not_sniped_main) + \
        "\nContributed **" + str(snipe_percentage) + "%**" + " of snipes!"

    embed = discord.Embed(
        title=titlemessage,
        color=discord.Color.gold()
    )
    embed.description = description
    embed.set_author(name='Snipebot 3 by Komm', icon_url=flag)
    embed.set_thumbnail(url=str(image))
    if play != False:
        embed.add_field(name="Generated random map you sniped on below",
            value="[Link to map]("+str(play['score']['beatmap']['url'])+")", inline=False)
    if sniped_play != False:
                embed.add_field(name="Generated random you map were sniped on below",
            value="[Link to map]("+str(sniped_play['score']['beatmap']['url'])+")", inline=False)
    return embed

async def create_stats_embed(artists, diff, song, user_data, gd, best_count, artist_count, gd_freq, maps, av_len, most_mapper, mapper_freq, gds, hosts):
    string = f"\n__**{user_data['username']}'s top 10 most popular Artists:**__\n```\n"
    embed = discord.Embed(
        title=f"osu! stats for {user_data['username']}",
        color=discord.Colour.gold()
    )
    embed.set_author(name="Snipebot 3 by Komm",
                    icon_url=f"https://osu.ppy.sh/images/flags/{user_data['country_code']}.png")
    if user_data['avatar_url'][0] == "/":
        embed.set_thumbnail(url=f"https://osu.ppy.sh{user_data['avatar_url']}")
    else:
        embed.set_thumbnail(url=user_data['avatar_url'])
    
    for p, artist in enumerate(artists):
        string = string + f"{artist} ({artist_count[p]})\n"
    string = string + "```"

    embed.description = string
    if av_len < 60:
        av_len = f"{str(av_len)} seconds"
    else:
        mod = av_len%60
        mod = round(mod)
        if round(mod) < 10:
            mod = f"0{str(mod)}"
        else:
            mod = str(mod)
        av_len = f"{str(round(av_len/60))}:{mod}"
    embed.add_field(name=f"Average SR of all your stored plays: `{round(diff, 2)}` ({maps} stored plays!)\nAverage length of your stored plays: `{av_len}`",
                    value=f"**One of your most played songs: `{song}` ({best_count} instances)**\n**Your favourite Guest Difficulty Mapper: `{gd}` ({gd_freq} instances)**\n**Your favourite mapper: `{most_mapper}` ({hosts} Host | {gds} Guest instances)**")
    embed.set_footer(text="Fact of the day: Did you know that Shii is the mapper of Lagtrain?", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Blue_question_mark_icon.svg/1200px-Blue_question_mark_icon.svg.png")
    return embed

async def create_profile_embed(user):
    embed = discord.Embed(
        title=f"osu! profile for {user['username']}",
        color=discord.Colour.red()
    )
    embed.description = \
        f"""**Rank**: #{user['statistics']['global_rank']:,} **Weighted pp**: {round(user['statistics']['pp']):,}
**Country Rank**: #{user['statistics']['country_rank']:,}
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


def create_snipe_embed(play, main_user, beatmap_data):
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
        description=f"{beatmap_data['beatmapset']['artist']} - {beatmap_data['beatmapset']['title']} [{play['beatmap']['version']}]" +
                    f" - {play['beatmap']['difficulty_rating']}:star:",
        colour=discord.Colour.green()
    )

    embed.set_thumbnail(url=beatmap_data['beatmapset']['covers']['list@2x'])

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
        friend_message = f"`{', '.join(sniped_friends[:4])}{' and more!' if len(sniped_friends) > 4 else ''}`"

    # USER AVATAR HANDLING
    if play['user']['avatar_url'][0] == "/":
        image = "https://osu.ppy.sh" + \
                str(play['user']['avatar_url'])
    else:
        image = str(play['user']['avatar_url'])

    embed = discord.Embed(
        title=title_message,
        description=f"{play['beatmapset']['artist']} - {play['beatmapset']['title']} [{play['beatmap']['version']}]" +
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
