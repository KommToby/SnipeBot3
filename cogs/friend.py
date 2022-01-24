import discord
from discord.ext import commands
from database.init_db import Database
from database.init_db_2 import Database2
from snipebot import DATABASE, AUTH, snipe_bot_tracker
import asyncio


class Friend(commands.Cog): # must have commands.cog or this wont work

    def __init__(self, client):
        self.client = client
        self.database = DATABASE
        self.osu = AUTH

    @commands.command(aliases=['f'])
    @commands.has_permissions(administrator=True)
    async def friend(self, ctx, param : str, user_id : str):
        if param == "add":
            channels = await self.database.get_all_discord()
            channel = 0
            for _, channel in enumerate(channels):
                if channel[0] == str(ctx.channel.id):
                    channel = 1
                    user_data = await self.osu.get_user_data(str(user_id))
                    if user_data:
                        userid = user_data['id']
                        if not(await self.database.get_friend(userid, ctx.channel.id)):
                            with open('queue.txt', 'a') as file2:
                                file2.write(f'{str(userid)}\n')
                            file2.close()
                            file1 = open('done.txt', 'r')
                            lines = file1.readlines()
                            await self.database.add_friend(ctx.channel.id, userid)
                            await ctx.send(str(user_id) + " has been added as a friend!")
                            beatmaps = await self.database.get_all_beatmaps()
                            time1 = round(len(beatmaps) * 0.8, 2)
                            time2 = round(len(beatmaps) * 1.9, 2)
                            # if there isnt another instance of the program checking new friends
                            if lines[0] == '0':
                                file1 = open('done.txt', 'w')
                                file1.write('1')
                                file1.close()
                                await ctx.send(f"scanning {str(user_id)}'s plays for snipe's, this could take between {round((time1/60), 2)} and {round((time2/60), 2)} minutes to complete.")
                                checking = True
                                while checking is True:
                                    with open('queue.txt', 'r') as fin:
                                        data = fin.read().splitlines(True)
                                        first_user_id = data[0][:-1]
                                    fin.close()
                                    user_data = await self.osu.get_user_data(str(first_user_id))
                                    await snipe_bot_tracker.add_new_user(user_data['id'], ctx, user_data['username']) #user_id is their username not their id
                                    with open('queue.txt', 'r') as fin:
                                        data = fin.read().splitlines(True)
                                    fin.close()
                                    if data[1:]:
                                        with open('queue.txt', 'w') as fout:
                                            fout.writelines(data[1:])
                                        fout.close()
                                    else:
                                        fout = open('queue.txt', 'w')
                                        fout.close()
                                        checking = False
                                        file1.close()
                                        file1 = open('done.txt', 'w')
                                        file1.write('0')
                                        file1.close()
                            else:
                                file1.close()
                                lengtha = open('queue.txt', 'r')
                                count = 0
                                for line in lengtha.readlines():
                                    count = count+1

                                await ctx.send(f"Added {str(user_id)} to the friend queue, it could take between {(round((time1/60), 2))*count} and {(round((time2/60), 2))*count} minutes to complete.")

                                    

                        else:
                            await ctx.send("User is already added as a friend.")
            if channel == 0:
                await ctx.send("There is no main user being tracked in this channel")

    @friend.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: `-friend add/remove "username"`') 

def setup(client):
    client.add_cog(Friend(client))