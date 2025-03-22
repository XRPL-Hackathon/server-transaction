import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

def get_mongo_client() -> MongoClient:
    return MongoClient(MONGODB_URL + "?retryWrites=true")