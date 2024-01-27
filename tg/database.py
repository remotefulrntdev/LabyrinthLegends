import sqlite3

class db:
    @staticmethod
    def connect_database():
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS players (tg_id INTEGER PRIMARY KEY, move_count INTEGER DEFAULT 0 NOT NULL,is_banned INTEGER DEFAULT 0 NOT NULL,tg_name TEXT DEFAULT 'Unknown')")
        connection.commit()
        return connection, cursor
    @staticmethod
    def create_player(tg_id, tg_name):
        connection, cursor = db.connect_database()
        cursor.execute("INSERT INTO players (tg_id, tg_name) VALUES (?,?)", (tg_id, tg_name))
        connection.commit()
        connection.close()
    @staticmethod
    def update_move_count(tg_id,c=1):
        connection, cursor = db.connect_database()
        cursor.execute("UPDATE players SET move_count = move_count + "+str(c)+ " WHERE tg_id = ?", (tg_id,))
        connection.commit()
        connection.close()
    @staticmethod
    def user_exists(tg_id):
        connection, cursor = db.connect_database()
        cursor.execute("SELECT * FROM players WHERE tg_id = ?", (tg_id,))
        result = cursor.fetchone()
        connection.close()
        if result == None:
            return False
        else:
            return True
    @staticmethod
    def get_info(tg_id):
        connection, cursor = db.connect_database()

        cursor.execute("SELECT * FROM players WHERE tg_id = ?", (tg_id,))
        result = cursor.fetchone()

        connection.close()   
        return result