from enum import Enum
from typing import Optional
from bson import ObjectId
from fastapi import FastAPI, Query
from pydantic import BaseModel
from datetime import datetime
import pymongo

app = FastAPI()

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

# connect to atlas mongodb
# client = pymongo.MongoClient("mongodb+srv://yandiriswandi:rinamuyandiku@tutorialcrud.ebjbgab.mongodb.net/?retryWrites=true&w=majority&appName=tutorialCrud")
# db = client.get_database("fastapi-tutorial")
# transaction = db.get_collection("transaction")

# connect to local database
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["fastapi_database"]
transaction = db["transactions"]

#add transaction
@app.post("/transaction")
def insert_transaction(input_transaction: InputTransaction):
    transaction_data = input_transaction.model_dump()
    transaction_data['createTime'] = datetime.utcnow()
    result = transaction.insert_one(transaction_data)
    return {"message": "Transaction inserted successfully", "transaction_id": str(result.inserted_id)}

#get transaction
@app.get("/transaction")
def get_transaction(tipe: Tipe = None,name: str = None, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    query = {}
    if tipe:
        query['tipe'] = tipe
    if name:
        query['name'] = {"$regex": name, "$options": "i"} 
        
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

#update transaction
@app.put("/transaction/{id}")
def insert_transaction(id:str,input_transaction: InputTransaction):

    transaction.update_one({"_id":ObjectId(id)},{"$set":input_transaction.model_dump()})
    return {"message": "Transaction update successfully"}

#delete transaction
@app.delete("/transaction/{id}")
def insert_transaction(id:str):

    transaction.delete_one({"_id":ObjectId(id)})
    return {"message": "Transaction delete successfully"}
