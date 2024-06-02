from pymongo import MongoClient

from app.config import DATABASE_NAME, DATABASE_URL

_client = MongoClient(DATABASE_URL)
database = _client[DATABASE_NAME]
