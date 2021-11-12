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
        ''')

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