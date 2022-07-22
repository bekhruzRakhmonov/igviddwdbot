import sqlite3 as sqlt
import pymongo
import os

PASSWORD = os.getenv("PASSWORD")

myclient = pymongo.MongoClient(f"mongodb+srv://bexruz:{PASSWORD}@cluster0.pedffq8.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["igviddwdbot"]
mycol = mydb["users"]

def add_user(user_id):
	mydict = {"user_id": user_id}
	mydoc = mycol.insert_one(mydict)
	return mydoc

def get_user(user_id):
	myquery = { "user_id": user_id }
	mydoc = mycol.find(myquery)
	doc = [doc for doc in mydoc]
	return doc

def get_users():
	users = [user for user in mycol.find()]
	return users
