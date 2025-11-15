import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME", "marketing_assistant")
    PORT = int(os.getenv("PORT", 8000))  # Changed default to 8000

# For backward compatibility
MONGO_URI = Config.MONGO_URI
DB_NAME = Config.DB_NAME
PORT = Config.PORT