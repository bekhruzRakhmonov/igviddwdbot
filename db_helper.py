import sqlite3 as sqlt

conn = sqlt.connect('db.db',check_same_thread=False)
cursor = conn.cursor()

class DBHelper:
	def __init__(self,user):
		self.user = user
	def create_db(self):
		return cursor.execute("CREATE TABLE IF NOT EXISTS users (id integer PRIMARY KEY,user_id text NOT NULL);")

	def check_user(self):
		return cursor.execute("SELECT * FROM users WHERE user_id='{}'".format(self.user)).fetchone()

	def add_user(self):
		return cursor.execute("INSERT INTO users(user_id) VALUES ({})".format(self.user))
	def get_users_count(self):
		return cursor.execute("SELECT id FROM users")
	def commit(self):
		return conn.commit()