from pymongo import MongoClient

_client = MongoClient("mongodb://%s:%s@127.0.0.1" % ("root", "root"))
database = _client["yuta"]
