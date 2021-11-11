import discord
from discord.ext import commands

class Help(commands.HelpCommand): # must have commands.cog or this wont work

    # def __init__(self):
    #     self.__init__()

    async def send_bot_help(self, mapping): # all cogs
        for cog in mapping:
            await self.get_destination().send(f'{cog.qualified_name}: {[command.name for command in mapping[cog]]}')
    
    async def send_cog_help(self, cog): # specific cog
        await self.get_destination().send(f'{cog.qualified_name}: {[command.name for command in cog.get_commands()]}')

    async def send_group_help(self, group): # specific group of cogs/commands
        await self.get_destination().send(f'{group.name}: {[command.name for index, command in enumerate(group.commands)]}')

    async def send_command_help(self, command): # specific command within cog
        await self.get_destination.send(command.name)

def setup(client):
    client.add_cog(Help(client))