import discord
from discord.ext import commands


class Help(commands.HelpCommand): # must have commands.cog or this wont work

    # def __init__(self):
    #     self.__init__()

    async def send_bot_help(self, ctx):
        channel = self.get_destination()
        embed = discord.Embed(
            title="Snipebot 3 by Komm",
            color=discord.Colour.red()
        )
        embed.add_field(name="User Commands",
                        value="`-snipes <username>`: Displays a card with the users snipe statistics for this server\n`-stats <username>`: Displays a card with the users played map statistics\n`-snipelist <username>`: Displays a list of maps that user has been sniped on\n`-leaderboard`: Displays the snipes leaderboard for this server\n`-osu <username>`: Displays a card which shows general osu! stats for the user\n`-r <username> <-min/max 0-10>`: Recommends a map that the user has not played",
                        inline = False)
        embed.add_field(name="Main User Commands",
                        value="`-mr <username> <-best/most>`: Recommends maps snipe friends on\n`-snipeback <username>`: Displays a list of maps the user needs to snipe back on\n`-friends <username>`: lists all friends being tracked for the main user\n`-friend <add/remove> <username>`: add or remove a friend to be tracked\n`-checkbeatmap <beatmapid>`: checks all users for snipes on beatmap\n`-purge <number>`: removes a number of messages including your message",
                        inline = False)
        await channel.send(embed=embed)
    
    async def send_cog_help(self, cog): # specific cog
        await self.get_destination().send(f'{cog.qualified_name}: {[command.name for command in cog.get_commands()]}')

    async def send_group_help(self, group): # specific group of cogs/commands
        await self.get_destination().send(f'{group.name}: {[command.name for index, command in enumerate(group.commands)]}')

    async def send_command_help(self, command): # specific command within cog
        await self.get_destination().send(command.name)


def setup(client):
    client.add_cog(Help(client))
