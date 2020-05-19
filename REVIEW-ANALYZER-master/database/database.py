from pymongo import MongoClient

class Database:

    def __init__(self):
        client = MongoClient("mongodb://localhost:27017/")
        self.db = client.test

    def getCollection(self, col_name):
        return self.db[col_name]