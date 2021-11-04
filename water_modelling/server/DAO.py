
from pymongo import MongoClient
from constants import DB_URL

"""
A project document contains the following:
{
    "rows": int - the amount of rows in the model grid,
    "cols": int - the amount of columns in the model grid,
    "cell_size": float - the length of a single grid cell,
    "lat": float - the latitude the model lies at,
    "long": float - the longitude the model lies at,
    "start_date": string - the start date of the simulation, YYYY-mm-dd
    "end_date": string - the end date of the simulation, YYYY-mm-dd,
    "modflow_model": string - the name of the folder containing the modflow model,
    "hydrus_models": List<String> - a list of names of folders containing the hydrus models
}
"""


PROJECTS = "projects"
RESULTS = "results"


class DAO:
    """
    A simple data access class to make getting stuff from mongo prettier and less chaotic.

    The class contains declarations of collection names, please import and use these instead
    of re-declaring them elsewhere, mongo is stupid and if someone makes a typo it WILL create
    new collections and put stuff in them.
    """

    def __init__(self, db_url):
        client = MongoClient(db_url)
        self.db = client.waterline

    def create(self, collection: str, document: dict):
        """
        A simple insertion method. Puts the data you give it into the specified collection. If the
        collection doesn't exist it will be created.

        :param collection: a string, the name of the collection we want to insert into
        :param document: a string-keyed dict, the document we want to insert
        :return: None
        """
        self.db[collection].insert_one(document)

    def read(self, collection: str, query: dict):
        """
        Searches the specified collection for a document whose field values match those entered in the query.
        E.g. a document of {"name": "Bob", "age": 18, "size": "large"} will match a query of {"name": "Bob"},
        but also {"age": 18, "size": "large"} etc.

        :param collection: a string, the collection we want to read from
        :param query: a string-keyed dict, the key-value pairs we want to filter by
        :return: the first document found matching the query, or None if not found
        """
        return self.db[collection].find_one(query)

    def read_all(self, collection: str):
        """
        Returns all the documents from a specified collection.

        :param collection: as string, the collection whose contents we want to get
        :return: a list of documents from that collection
        """
        return [x for x in self.db[collection].find()]

    def update(self, collection: str, query: dict, new_data: dict, operator="$set"):
        """
        Searches the specified collection for a document matching the query (see the read() method),
        then updates that document's key-value pairs with those specified in new_data. The operator
        defines how the update is performed, by default it is $set, which means pair with only be created
        or updated, never deleted.

        For a list of operators go here: https://docs.mongodb.com/upcoming/reference/operator/update/.

        :param collection: a string, the collection we want to update
        :param query: a string-keyed dict, the key-value pairs identifying the update target
        :param new_data: a string-keyed dict, the stuff we want to update in the target
        :param operator: defines the update method; we probably won't use this, but it's here in case someone needs it
        :return: None
        """
        self.db[collection].update_one(query, {operator: new_data})

    def delete(self, collection: str, query: dict):
        """
        Deletes a document matching the query (see the read() method) from the specified collection.

        :param collection: a string, the collection we want to delete from
        :param query: a string-keyed dict, the key-value pairs identifying the target
        :return: None
        """
        self.db[collection].delete_one(query)
