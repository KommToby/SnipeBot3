## TODO
## 1: Local, single database, called scores.db: USER_ID, BEATMAP_ID, USER_SCORE
## 2: Local, single database, called user.db: DISCORD_ID, USER_ID, PING_STATUS
## 3: Main loop that checks for new scores for every user
## 4: When ANYONE gets a new score, if the map hasnt been checked before, the map checks all the friends to see if they beat the main user after the main user set their play
## 5: Local, single database, called friends.db: DISCORD_ID, FRIEND_ID
## 6: 

## IMPORTS
import json # json handling
import discord # discord bot implementation
from discord.ext import commands
import os # file handling
import help # help handling
from main import Main # main loop

## LOADING CONFIG - GETTING DISCORD TOKEN
def load_config():
    with open("config.json") as f:
        data = json.load(f)['discord']
        TOKEN = data['token']
        return TOKEN

## LOADING DETAILS
token = load_config()
GUILD = ''
client = commands.Bot(command_prefix='-', help_command=help.Help())

## DISCORD BOT CONNECTION
@client.event
async def on_ready():
    return_data = ""
    print(f'{client.user} has connected to Discord!')
    main = Main()


## DISCORD BOT DISCONNECTION
@client.event
async def on_disconnect():
    print("Bot has disconnected from discord")

## Command handler
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

## Command unloader
@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

## Load all cogs before bot runs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'): # ignore non-python files
        client.load_extension(f'cogs.{filename[:-3]}') # loads extension, without the '.py'

## Must be final line
client.run(token)
