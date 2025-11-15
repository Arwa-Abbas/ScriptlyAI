import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
import spacy

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def extract_features(text):
    doc = nlp(text)
    # Extract nouns/adjectives as features
    features = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "ADJ"]]
    return list(set(features))  # unique features

def update_products_features():
    for product in db.products.find():
        desc = product.get("description", "")
        features = extract_features(desc)
        db.products.update_one({"_id": product["_id"]}, {"$set": {"features": features}})

if __name__ == "__main__":
    update_products_features()
    print("Features extracted and updated in MongoDB.")
