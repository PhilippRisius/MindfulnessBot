from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MindfulMongo:
    def __init__(self, host, port, db_name):
        self.connect_to_database(host, port)
        self.database = self.client[db_name]
        self.database.users.create_index("discord_id", unique = True)

    def connect_to_database(self, host, port):
        try:
            self.client = MongoClient(host, port)
        except ConnectionFailure as e:
            print("Could not connect to MongoDB: %s" % str(e))

    def save_user(self, user_data):
        result = self.__users().update_one(
            {"discord_id": user_data["discord_id"]},
            { '$set': user_data },
            upsert = True
        )

        return result.raw_result['updatedExisting']

    def retrieve_user(self, discord_id):
        user = self.__users().find_one({
            "discord_id": discord_id
        })

        return user

    def __users(self):
        return self.database['users']
