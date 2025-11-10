import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_URI = os.getenv("DB_URI", "mongodb://localhost:27017/university")


# Create a new client and connect to the server
client = MongoClient(DB_URI)
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)