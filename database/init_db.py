import sqlite3
from osu.osu_auth import OsuAuth

class Database:
    def __init__(self):
        self.osu = OsuAuth()
        self.db = sqlite3.connect('database.db')
        self.cursor = self.db.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores(
                user_id varchar(32) not null,
                beatmap_id varchar(32),
                score varchar(32)
            )
        ''') ## potentially add mods to this db later on

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users(
                discord_id varchar(32) not null primary key,
                user_id varchar(32),
                last_score varchar(32)
            )
        ''') # discord_id is channel id, user id is users osu name / id

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends(
                discord_channel varchar(32) not null,
                user_id varchar(32),
                last_score varchar(32),
                ping int2
            )
        ''') 

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS beatmaps(
                beatmap_id varchar(32) not null,
                song_name varchar(32),
                difficulty_name varchar(32)
            )
        ''') 
        
    def get_channel(self, discord_id):
        return self.cursor.execute(
            "SELECT * FROM users WHERE discord_id=?",
            (discord_id,)).fetchone()

    async def add_channel(self, discord_id, user_id):
        user_data = await self.osu._get_api_v2("/v2/users/" + str(user_id))
        user_id = user_data['id']
        self.cursor.execute(
            "INSERT INTO users VALUES(?,?,?)",
            (discord_id, user_id, 0)
        )
        self.db.commit()

    def get_all_users(self):
        return self.cursor.execute(
            "SELECT * FROM users"
        ).fetchall()

    def get_best_play(self, user_id):
        return self.cursor.execute(
            "SELECT * FROM users WHERE user_id=?",
            (user_id,)
        ).fetchone()

    def get_user_beatmap_play(self, user_id, beatmap_id):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND beatmap_id=?",
            (user_id,beatmap_id)
        ).fetchone()

    def add_score(self, user_id, beatmap_id, score):
        self.cursor.execute(
            "INSERT INTO scores VALUES(?,?,?)",
            (user_id,beatmap_id,score)
        )
        self.db.commit()

    def add_friend(self, discord_id, friend_id):
        self.cursor.execute(
            "INSERT INTO friends VALUES(?,?,?,?)",
            (discord_id,friend_id,0,0) # second 0 = no ping on snipe
        )
        self.db.commit()              