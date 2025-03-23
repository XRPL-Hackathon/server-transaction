from pymongo import MongoClient
from src.main.config.mongodb import get_mongo_client
from bson import ObjectId

class PaymentsRepository:
    def __init__(self):
        client: MongoClient = get_mongo_client()
        self.db = client["xrpedia-data"]
        self.wallets_collection = self.db["wallets"]
        self.document_collection = self.db["document_collection"]
        self.files_collection = self.db["files"]
        self.transactions_collection = self.db["transactions"]

    # MongoDB에서 user_id 기반으로 XRPL 지갑 정보 조회
    def get_user_wallet(self, user_id: str):
        return self.wallets_collection.find_one({"user_id": user_id}, {"_id": 0, "address": 1, "seed": 1})
    
    # MongoDB에서 파일 정보 전체 조회 (price + owner_id 포함)
    def get_file_info(self, file_id: str):
        try:
            file_object_id = ObjectId(file_id)
        except Exception as e:
            print(f"[ERROR] file_id를 ObjectId로 변환할 수 없음: {e}")
            return None
        
        file = self.files_collection.find_one(
            {"_id": file_object_id}, 
            {"_id": 0, "owner_id": 1}
        )

        if not file:
            print("[WARN] files_collection에서 파일 정보 못 찾음")
            return None
        
        doc = self.document_collection.find_one(
            {"file_id": file_id}, 
            {"_id": 0, "price": 1}
        )

        if not doc:
            print("[WARN] document_collection에서 파일 정보 못 찾음")
            return None
        
        return {**doc, **file}

    def get_file_price(self, file_id: str):
        file_info = self.document_collection.find_one(
            {"file_id": file_id},
            {"_id": 0, "price": 1}
        )
        return file_info["price"] if file_info else None
    
    def get_user_profile(self, user_id: str):
        return self.wallets_collection.find_one(
            {"user_id": user_id},
            {"_id": 0, "profile": 1}
        )
    
    def update_user_rlusd(self, user_id: str, new_rlusd: int):
        self.wallets_collection.update_one(
            {"user_id": user_id},
            {"$set": {"rlusd": new_rlusd}}
        )
    
    def is_transaction_exist(self, user_id: str, file_id: str):
        print(f"Checking if transaction exists for user_id: {user_id}, file_id: {file_id}")
        transaction = self.transactions_collection.find_one(
            {"user_id": user_id, "file_id": file_id}
        )
        if transaction:
            print(f"Transaction found: {transaction}")
        else:
            print("Transaction not found")
        return transaction is not None
    
    def save_transaction(self, tx_data: dict):
        print(f"Saving transaction: {tx_data}")
        self.transactions_collection.insert_one(tx_data)