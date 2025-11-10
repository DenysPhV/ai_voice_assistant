# backend/utils/db_connector.py
import os

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv


load_dotenv()

DB_URI = os.getenv("DB_URI")
DB_NAME = os.getenv("DB_NAME", "ai_assistant")

client: AsyncIOMotorClient | None = None
db = None

def connect_to_mongo():
    global client, db
    if client is None:
        client = AsyncIOMotorClient(DB_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        # можна перевірити з'єднання тут:
        # client.admin.command('ping')
    return db

def close_mongo_connection():
    global client
    if client:
        client.close()

def get_conversations_collection():
    db = connect_to_mongo()
    return db["conversations"]