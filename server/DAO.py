
from pymongo import MongoClient

PROJECTS = "projects"
RESULTS = "results"


class DAO:

    def __init__(self, db_url):
        client = MongoClient(db_url)
        self.db = client.waterline

    def create(self, collection, document):
        self.db[collection].insert_one(document)

    def read(self, collection, query):
        return self.db[collection].find_one(query)

    def update(self, collection, query, new_data, operator="$set"):
        self.db[collection].update_one(query, {operator: new_data})

    def delete(self, collection, query):
        self.db[collection].delete_one(query)
