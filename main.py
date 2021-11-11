import random
import discord
import time
import asyncio
import sys
from database.init_db import Database

class Main():
    def __init__(self):
        self.database = Database()