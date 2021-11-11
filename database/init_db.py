import sqlite3

class Database:
    def __init(self):
        self.db = sqlite3.connect('database.db')
        self.cursor = self.db.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores(
                user_id varchar(32) not null primary key,
                beatmap_id varchar(32),
                score varchar(32)
            )
        ''')