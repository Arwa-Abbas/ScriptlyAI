import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Insert a test product
test_product = {
    "name": "Test Product",
    "category": "Test Category",
    "features": ["fast", "easy to use"]
}

insert_result = db.products.insert_one(test_product)
print(f"Inserted product with _id: {insert_result.inserted_id}")

# Fetch and print all products
print("\nAll products in the database:")
for product in db.products.find():
    print(product)
