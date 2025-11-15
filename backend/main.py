from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from pymongo import MongoClient
from bson import ObjectId
import uvicorn
import logging

from config import Config
from src.recommender import MarketingScriptRecommender

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Marketing Script Assistant API",
    description="AI-powered marketing script generation",
    version="1.0.0"
)

# ENHANCED CORS CONFIGURATION
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"🌐 {request.method} {request.url}")
    logger.info(f"   Origin: {request.headers.get('origin', 'No origin')}")
    response = await call_next(request)
    logger.info(f"   Response: {response.status_code}")
    return response

# MongoDB connection
try:
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.DB_NAME]
    # Test connection
    client.server_info()
    logger.info(f"✅ Connected to MongoDB: {Config.DB_NAME}")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {str(e)}")
    db = None

# Pydantic Models
class ProductRequest(BaseModel):
    name: str
    category: Optional[str] = ""
    description: str
    price: Optional[str] = ""

class SimilarProduct(BaseModel):
    name: str
    category: str
    price: Optional[float]  # ✅ Changed from str to float
    similarity: float

class MarketingContent(BaseModel):
    video_script: str
    social_media_posts: str

class ScriptResponse(BaseModel):
    success: bool
    input_product: dict
    similar_products: List[SimilarProduct]
    marketing_content: MarketingContent

class HealthResponse(BaseModel):
    status: str
    database: str
    error: Optional[str] = None

# Helper function to serialize MongoDB documents
def serialize_doc(doc):
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    elif isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc

# Helper function to safely convert price to float
def safe_float_convert(price):
    if price is None:
        return None
    try:
        return float(price)
    except (ValueError, TypeError):
        return None

# Routes
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Marketing Script Assistant API", 
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    try:
        if db is None:
            return {"status": "unhealthy", "database": "disconnected", "error": "Database not initialized"}
        
        db.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.get("/api/products", tags=["Products"])
async def get_products(limit: int = 50, skip: int = 0):
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        products = list(db.products.find().skip(skip).limit(limit))
        serialized_products = serialize_doc(products)
        
        total_products = db.products.count_documents({})
        
        return {
            "success": True, 
            "products": serialized_products,
            "pagination": {
                "limit": limit,
                "skip": skip,
                "total": total_products,
                "has_more": (skip + limit) < total_products
            }
        }
    except Exception as e:
        logger.error(f"Get products error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/generate-script", response_model=ScriptResponse, tags=["Script Generation"])
async def generate_script(product: ProductRequest):
    try:
        logger.info(f"🔍 Received request for product: {product.name}")
        
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        input_product = {
            'name': product.name,
            'category': product.category,
            'description': product.description,
            'price': product.price
        }
        
        # Initialize recommender
        try:
            recommender = MarketingScriptRecommender()
        except Exception as e:
            logger.error(f"Failed to initialize recommender: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Recommender initialization failed: {str(e)}")
        
        # Find similar products
        try:
            similar_products = recommender.find_similar_products(input_product, top_n=3)
            logger.info(f"📊 Found {len(similar_products)} similar products")
        except Exception as e:
            logger.error(f"Failed to find similar products: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Similar product search failed: {str(e)}")
        
        if not similar_products:
            raise HTTPException(
                status_code=404, 
                detail="No similar products found to generate marketing script"
            )
        
        # Generate marketing content
        try:
            video_script = recommender.generate_marketing_script(input_product, similar_products)
            social_posts = recommender.generate_social_media_post(input_product)
        except Exception as e:
            logger.error(f"Failed to generate content: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")
        
        # Prepare response - FIXED: Convert price to float safely
        similar_products_response = []
        for sp in similar_products:
            # Safely convert price to float
            raw_price = sp['product'].get('price')
            converted_price = safe_float_convert(raw_price)
            
            similar_products_response.append({
                "name": sp['product'].get('name', 'Unknown'),
                "category": sp['product'].get('category', 'Uncategorized'),
                "price": converted_price,  # ✅ Now properly converted to float
                "similarity": round(sp['similarity'], 3)
            })
        
        response_data = {
            "success": True,
            "input_product": input_product,
            "similar_products": similar_products_response,
            "marketing_content": {
                "video_script": video_script,
                "social_media_posts": social_posts
            }
        }
        
        logger.info("✅ Successfully generated marketing script")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in generate_script: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Script generation failed: {str(e)}")

@app.get("/api/products/count", tags=["Products"])
async def get_products_count():
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        count = db.products.count_documents({})
        collections = db.list_collection_names()
        return {
            "success": True,
            "total_products": count,
            "collections": collections
        }
    except Exception as e:
        logger.error(f"Get products count error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Run the application
if __name__ == "__main__":
    logger.info(f"🚀 Starting server on port {Config.PORT}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=Config.PORT,
        reload=True,
        log_level="info"
    )