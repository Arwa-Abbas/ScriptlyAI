import pandas as pd
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def load_products():
    df = pd.read_csv("data/products.csv", encoding="latin1")  # or encoding="ISO-8859-1"
    # Convert features column from comma-separated string to list
    if "features" in df.columns:
        df["features"] = df["features"].apply(lambda x: x.split(",") if isinstance(x, str) else [])
    db.products.insert_many(df.to_dict("records"))

def load_marketing_copy():
    df = pd.read_csv("data/marketing_copy.csv")
    db.scripts.insert_many(df.to_dict("records"))

if __name__ == "__main__":
    load_products()
    load_marketing_copy()
    print("CSV data loaded into MongoDB successfully!")
