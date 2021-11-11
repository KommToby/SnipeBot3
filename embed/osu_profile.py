from osu.osu_auth import OsuAuth
import discord
import sys
sys.path.append("..")


class Profile():
    def __init__(self):
        self.auth = OsuAuth()

    async def profile(self, ctx, userid: str):
        dict = await self.auth._get_api_v2("/v2/users/" + str(userid), ctx)
        embed = discord.Embed(
            title=("osu! profile of " + dict['username']),
            color=discord.Colour.red()
        )
        embed.description = "gonna do this after i know it actually sends an embed"
        embed.set_author(name='Snipebot 3 by Komm',
                        icon_url="https://osu.ppy.sh/images/flags/" + dict['country_code']+".png")
        if dict['avatar_url'][0] == "/":
            embed.set_thumbnail(url="https://osu.ppy.sh" +
                                str(dict['avatar_url']))
        else:
            embed.set_thumbnail(url=str(dict['avatar_url']))
        await ctx.send(embed=embed)
