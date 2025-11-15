import sys
import os

# Add
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def generate_script(product):
    features_text = ", ".join(product.get("features", []))
    script = f"Introducing {product['name']}! This {product['category']} comes with {features_text}. Available for just ${product['price']}! Get yours now."
    return script

def create_all_scripts():
    for product in db.products.find():
        script = generate_script(product)
        db.products.update_one(
            {"_id": product["_id"]},
            {"$set": {"marketing_script": script}}
        )

if __name__ == "__main__":
    create_all_scripts()
    print("Marketing scripts generated and saved in MongoDB.")

