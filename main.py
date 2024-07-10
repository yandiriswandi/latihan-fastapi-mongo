from enum import Enum
from typing import Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
from datetime import datetime
import pymongo

application = FastAPI()

class Tipe(str, Enum):
    def __str__(self):
        return str(self.value)
    INCOME="INCOME"
    PURCHASE="PURCHASE"
    INVEST="INVEST"

class Method(str, Enum):
    def __str__(self):
        return str(self.value)
    
    CASH="CASH"
    EWALLET="EWALLET"
    BANK="BANK"

class InputTransaction(BaseModel):
    tipe:Tipe
    amount:int
    notes:Optional[str]
    method:Method
    name:str

client = pymongo.MongoClient("mongodb+srv://yandiriswandi:rinamuyandiku@tutorialcrud.vjx790j.mongodb.net/?retryWrites=true&w=majority&appName=tutorialCrud")
db = client.get_database("fastapi-tutorial")
transaction = db.get_collection("transaction")

@application.post("/transaction")
def insert_transaction(input_transaction: InputTransaction):
    transaction_data = input_transaction.model_dump()
    transaction_data['createTime'] = datetime.utcnow()
    result = transaction.insert_one(transaction_data)
    return {"message": "Transaction inserted successfully", "transaction_id": str(result.inserted_id)}

@application.get("/transaction")
def get_transaction(tipe: Tipe = None,name: str = None, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    query = {}
    if tipe:
        query['tipe'] = tipe
    if name:
        query['name'] = name
        
    total_items = transaction.count_documents(query)
    result_filter = transaction.find(query).skip((page - 1) * size).limit(size)
    result_filter = list(result_filter)

    for r in result_filter:
        r["_id"] = str(r["_id"])

    return {
        "page": page,
        "size": size,
        "total_items": total_items,
        "total_pages": (total_items + size - 1) // size,  # Menghitung jumlah halaman total
        "items": result_filter
    }

