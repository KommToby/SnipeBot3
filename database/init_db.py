import sqlite3
from osuauth.osu_auth import OsuAuth


class Database:
    def __init__(self):
        self.osu = OsuAuth()
        self.db = sqlite3.connect('database.db')
        self.cursor = self.db.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores(
                user_id varchar(32) not null,
                beatmap_id varchar(32),
                score varchar(32),
                snipe int2
            )
        ''')  # potentially add mods to this db later on - snipe is to check if theyve been awarded a snipe for this map

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users(
                discord_id varchar(32) not null primary key,
                user_id varchar(32),
                last_score varchar(32),
                snipes varchar(16),
                times_sniped varchar(16)
            )
        ''')  # discord_id is channel id, user id is users osu name / id

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends(
                discord_channel varchar(32) not null,
                user_id varchar(32),
                last_score varchar(32),
                ping int2
            )
        ''') # dont need to store snipes and sniped, since you can just count from the snipes table

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS beatmaps(
                beatmap_id varchar(32) not null,
                artist varchar(32),
                song_name varchar(32),
                difficulty_name varchar(32),
                url varchar(32)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS snipes(
                user_id varchar(32) not null,
                beatmap_id varchar(32),
                second_user_id varchar(32)
            )
        ''')  # for storing if someone has been sniped on a specific beatmap

    # GETS

    async def get_channel(self, discord_id):
        return self.cursor.execute(
            "SELECT * FROM users WHERE discord_id=?",
            (discord_id,)).fetchone()

    async def get_all_users(self):
        return self.cursor.execute(
            "SELECT * FROM users"
        ).fetchall()

    async def get_all_friends(self):
        return self.cursor.execute(
            "SELECT * FROM friends"
        ).fetchall()

    async def get_best_play(self, user_id):
        return self.cursor.execute(
            "SELECT * FROM users WHERE user_id=?",
            (user_id,)
        ).fetchone()

    async def get_user_beatmap_play(self, user_id, beatmap_id):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND beatmap_id=? AND score!=?",
            (user_id, beatmap_id, "0")
        ).fetchone()

    async def get_user_beatmap_play_with_zeros(self, user_id, beatmap_id):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND beatmap_id=?",
            (user_id, beatmap_id)
        ).fetchone()

    async def get_user_beatmap_plays(self, user_id, beatmap_id):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND beatmap_id=? AND score!=?",
            (user_id, beatmap_id, "0")
        ).fetchall()

    async def get_user_plays_from_beatmap(self, beatmap_id):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE beatmap_id=? AND score!=?",
            (beatmap_id, "0")
        ).fetchall()

    async def get_user_beatmap_play_score(self, user_id, beatmap_id, score):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND beatmap_id=? AND score=?",
            (user_id, beatmap_id, score)
        ).fetchone()

    async def get_all_scores(self, user_id):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND score!=?",
            (user_id,"0")
        ).fetchall()

    async def get_user_scores_with_zeros(self, user_id):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=?",
            (user_id,)
        ).fetchall()

    async def get_scores_from_beatmap(self, beatmap_id):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE beatmap_id=?",
            (beatmap_id,)
        ).fetchall()

    async def get_scores(self):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE score!=?",
            ("0",)
        ).fetchall()

    async def get_single_user_snipes(self, user_id, main_user_id):
        return self.cursor.execute(
            "SELECT * FROM snipes WHERE user_id=? AND second_user_id=?",
            (user_id, main_user_id)
        ).fetchall()

    async def get_user_snipe(self, user_id, beatmap_id):
        return self.cursor.execute(
            "SELECT * FROM snipes WHERE user_id=? AND beatmap_id=?",
            (user_id, beatmap_id)
        ).fetchall()

    async def get_user_sniped(self, user_id, beatmap_id):
        return self.cursor.execute(
            "SELECT * FROM snipes WHERE second_user_id=? AND beatmap_id=?",
            (user_id, beatmap_id)
        ).fetchall()

    async def get_user_snipes(self, user_id, beatmap_id, second_user):
        # if theres a bug with this, try naming the function to the one above which doesnt require second user
        return self.cursor.execute(
            "SELECT * FROM snipes WHERE user_id=? AND second_user_id=? AND beatmap_id=?",
            (user_id, second_user, beatmap_id)
        ).fetchone()

    async def get_beatmap_data(self, beatmap_id):
        return self.cursor.execute(
            "SELECT * FROM beatmaps WHERE beatmap_id=?",
            (beatmap_id,)
        ).fetchone()

    async def get_total_snipes(self, main_user_id):
        return self.cursor.execute(
            "SELECT * FROM snipes WHERE second_user_id=?",
            (main_user_id,)
        ).fetchall()

    async def get_main_snipes(self, main_user_id):
        return self.cursor.execute(
            "SELECT * FROM snipes WHERE user_id=?",
            (main_user_id,)
        ).fetchall()

    async def get_main_sniped(self, main_user_id):
        return self.cursor.execute(
            "SELECT * FROM snipes WHERE second_user_id=?",
            (main_user_id,)
        ).fetchall()

    async def get_user_friends(self, main_id):
        main_discord = await self.get_main_discord(main_id)
        return self.cursor.execute(
            "SELECT * FROM friends WHERE discord_channel=?",
            (main_discord[0],)
        ).fetchall()

    async def get_main_discord(self, main_id):
        return self.cursor.execute(
            "SELECT discord_id FROM users WHERE user_id=?",
            (main_id,)
        ).fetchone()

    async def get_all_discord(self):
        return self.cursor.execute(
            "SELECT * FROM users"
        ).fetchall()

    async def get_friend_discord(self, friend_id):
        return self.cursor.execute(
            "SELECT discord_channel FROM friends WHERE user_id=?",
            (friend_id,)
        ).fetchone()

    async def get_friend_times_sniped(self, friend_id, discord_id):
        return self.cursor.execute(
            "SELECT times_sniped FROM friends WHERE user_id=? AND discord_channel=?",
            (friend_id, discord_id)
        ).fetchone()

    async def get_beatmap(self, beatmap_id):
        return self.cursor.execute(
            "SELECT song_name FROM beatmaps WHERE beatmap_id=?",
            (beatmap_id,)
        ).fetchone()

    async def get_all_beatmaps(self):
        return self.cursor.execute(
            "SELECT * FROM beatmaps"
        ).fetchall()

    async def get_user_snipe_on_beatmap(self, user_id, beatmap_id, sniped_user_id):
        return self.cursor.execute(
            "SELECT user_id FROM snipes WHERE user_id=? AND beatmap_id=? AND second_user_id=?",
            (user_id, beatmap_id, sniped_user_id)
        ).fetchone()

    async def get_friend(self, user_id, discord_channel):
        return self.cursor.execute(
            "SELECT user_id FROM friends WHERE discord_channel=? AND user_id=?",
            (discord_channel, user_id)
        ).fetchone()

    async def get_main_from_friend(self, friend_id):
        discord_id = await self.get_friend_discord(friend_id)
        return self.cursor.execute(
            "SELECT user_id FROM users WHERE discord_id=?",
            (discord_id[0],)
        ).fetchone()

    async def get_main_from_discord(self, discord_id):
        return self.cursor.execute(
            "SELECT user_id FROM users WHERE discord_id=?",
            (discord_id,)
        ).fetchone()

    async def get_all_snipes(self):
        return self.cursor.execute(
            "SELECT * FROM snipes"
        ).fetchall()

    # ADDS

    async def add_score(self, user_id, beatmap_id, score, snipe):
        self.cursor.execute(
            "INSERT INTO scores VALUES(?,?,?,?)",
            (user_id, beatmap_id, score, snipe)  # SNIPE 0 OR 1
        )
        self.db.commit()

    async def add_friend(self, discord_id, friend_id):
        self.cursor.execute(
            "INSERT INTO friends VALUES(?,?,?,?)",
            (discord_id, friend_id, 0, 0)  # second 0 = no ping on snipe
        )
        self.db.commit()

    async def add_channel(self, discord_id, user_id):
        user_data = await self.osu.get_user_data(str(user_id))
        user_id = user_data['id']
        self.cursor.execute(
            "INSERT INTO users VALUES(?,?,?,?,?)",
            (discord_id, user_id, 0, 0, 0)
        )
        self.db.commit()

    async def add_beatmap(self, beatmap_id, artist, song_name, difficulty_name, url):
        self.cursor.execute(
            "INSERT INTO beatmaps VALUES(?,?,?,?,?)",
            (beatmap_id, artist, song_name, difficulty_name, url)
        )
        self.db.commit()

    async def add_snipe(self, user_id, beatmap_id, second_user_id):
        self.cursor.execute(
            "INSERT INTO snipes VALUES(?,?,?)",
            (user_id, beatmap_id, second_user_id)
        )
        self.db.commit()

    # UPDATES
    async def replace_user_play(self, user_id, beatmap_id, new_score):
        self.cursor.execute(
            "UPDATE scores SET score=? WHERE user_id=? AND beatmap_id=?",
            (new_score, user_id, beatmap_id)
        )
        self.db.commit()

    # DELETES
    async def delete_snipe(self, user_id, beatmap_id, second_user_id):
        self.cursor.execute(
            "DELETE FROM snipes WHERE user_id=? AND beatmap_id=? AND second_user_id=?",
            (user_id, beatmap_id, second_user_id)
        )
        self.db.commit()

    async def delete_score(self, user_id, beatmap_id, score):
        self.cursor.execute(
            "DELETE FROM scores WHERE user_id=? AND beatmap_id=? AND score=?",
            (user_id, beatmap_id, score)
        )
        self.db.commit()

    async def delete_beatmap(self, beatmap_id):
        self.cursor.execute(
            "DELETE FROM beatmaps WHERE beatmap_id=?",
            (beatmap_id,)
        )
        self.db.commit()

