from osu.osu_auth import OsuAuth
import discord
import sys


class Profile():
    def __init__(self):
        self.auth = OsuAuth()

    async def profile(self, ctx, userid: str):
        dict = await self.auth._get_api_v2("/v2/users/" + str(userid))
        embed = discord.Embed(
            title=("osu! profile of " + dict['username']),
            color=discord.Colour.red()
        )
        embed.description = "**Rank**: " + f"{(dict['statistics']['global_rank']):,}" + "\n" + \
                            "**Country Rank**: " + f"{(dict['statistics']['country_rank']):,}" + "\n" + \
                            "**Accuracy**: " + \
                            str(round(dict['statistics']['hit_accuracy'], 2)) + "%"
        embed.set_author(name='Snipebot 3 by Komm',
                        icon_url="https://osu.ppy.sh/images/flags/" + dict['country_code']+".png")
        if dict['avatar_url'][0] == "/":
            embed.set_thumbnail(url="https://osu.ppy.sh" +
                                str(dict['avatar_url']))
        else:
            embed.set_thumbnail(url=str(dict['avatar_url']))
        if dict['cover_url']:
            embed.set_image(url=str(dict['cover_url']))
        await ctx.send(embed=embed)
