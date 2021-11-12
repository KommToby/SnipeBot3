import discord
import sys


def create_osu_profile_embed(profile_info):
    embed = discord.Embed(
        title=("osu! profile of " + profile_info['username']),
        color=discord.Colour.red()
    )
    embed.description = \
f"""**Rank**: {profile_info['statistics']['global_rank']}
**Country Rank**: {profile_info['statistics']['country_rank']}
**Accuracy**: {round(profile_info['statistics']['hit_accuracy'], 2)}%
"""
    embed.set_author(name="Snipebot 3 by Komm",
                     icon_url=f"https://osu.ppy.sh/images/flags/{profile_info['country_code']}.png")
    if profile_info['avatar_url'][0] == "/":
        embed.set_thumbnail(url="https://osu.ppy.sh" +
                            str(profile_info['avatar_url']))
    else:
        embed.set_thumbnail(url=str(profile_info['avatar_url']))
    if profile_info['cover_url']:
        embed.set_image(url=str(profile_info['cover_url']))
    return embed

