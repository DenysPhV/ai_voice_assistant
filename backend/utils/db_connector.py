import os

from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()

def get_db():
    mongo_uri = os.getenv("DB_URI")
    client = MongoClient(mongo_uri)
    db = client["university_ai"]
    return db