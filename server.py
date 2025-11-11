from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import time
from emergentintegrations.emergent import (
    create_text_embedding
)
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Emergent LLM Key
EMERGENT_KEY = os.environ.get('EMERGENT_LLM_KEY', 'sk-emergent-a45B89aAc9459F1977')

# Create the main app
app = FastAPI(title="Vibe Matcher - Fashion Recommendation System")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    vibe_tags: List[str]
    category: str
    image_url: Optional[str] = None
    embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductCreate(BaseModel):
    name: str
    description: str
    vibe_tags: List[str]
    category: str
    image_url: Optional[str] = None

class VibeQuery(BaseModel):
    vibe: str
    limit: int = Field(default=3, ge=1, le=10)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class SimilarityResult(BaseModel):
    id: str
    name: str
    description: str
    vibe_tags: List[str]
    category: str
    image_url: Optional[str]
    similarity_score: float

class QueryMetrics(BaseModel):
    query: str
    results_count: int
    latency_ms: float
    top_score: Optional[float]
    timestamp: datetime

def generate_embedding(text: str) -> List[float]:
    """Generate embedding using Emergent LLM Key"""
    try:
        embedding = create_text_embedding(
            text=text,
            model="text-embedding-3-small",
            api_key=EMERGENT_KEY
        )
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

def calculate_cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Calculate cosine similarity between two embeddings"""
    vec1 = np.array(embedding1).reshape(1, -1)
    vec2 = np.array(embedding2).reshape(1, -1)
    return float(cosine_similarity(vec1, vec2)[0][0])

@api_router.get("/")
async def root():
    return {"message": "Vibe Matcher API", "version": "1.0.0"}

@api_router.post("/products", response_model=Product)
async def create_product(product_input: ProductCreate):
    """Create a new product with embedding"""
    try:
        # Generate embedding for product description
        combined_text = f"{product_input.name}. {product_input.description}. Vibes: {', '.join(product_input.vibe_tags)}"
        embedding = generate_embedding(combined_text)
        
        product = Product(
            name=product_input.name,
            description=product_input.description,
            vibe_tags=product_input.vibe_tags,
            category=product_input.category,
            image_url=product_input.image_url,
            embedding=embedding
        )
        
        doc = product.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        
        await db.products.insert_one(doc)
        return product
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/products", response_model=List[Product])
async def get_all_products():
    """Get all products"""
    try:
        products = await db.products.find({}, {"_id": 0}).to_list(100)
        for product in products:
            if isinstance(product.get('created_at'), str):
                product['created_at'] = datetime.fromisoformat(product['created_at'])
        return products
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/search", response_model=dict)
async def search_by_vibe(query: VibeQuery):
    """Search products by vibe query using cosine similarity"""
    start_time = time.time()
    
    try:
        # Generate embedding for query
        query_embedding = generate_embedding(query.vibe)
        
        # Get all products with embeddings
        products = await db.products.find({}, {"_id": 0}).to_list(100)
        
        if not products:
            return {
                "results": [],
                "metrics": {
                    "query": query.vibe,
                    "results_count": 0,
                    "latency_ms": round((time.time() - start_time) * 1000, 2),
                    "top_score": None,
                    "message": "No products found. Please add products first."
                }
            }
        
        # Calculate similarities
        results = []
        for product in products:
            if product.get('embedding'):
                similarity = calculate_cosine_similarity(query_embedding, product['embedding'])
                
                if similarity >= query.threshold:
                    results.append({
                        "id": product['id'],
                        "name": product['name'],
                        "description": product['description'],
                        "vibe_tags": product['vibe_tags'],
                        "category": product['category'],
                        "image_url": product.get('image_url'),
                        "similarity_score": round(similarity, 4)
                    })
        
        # Sort by similarity and limit results
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        results = results[:query.limit]
        
        latency = round((time.time() - start_time) * 1000, 2)
        
        # Store metrics
        metrics_doc = {
            "query": query.vibe,
            "results_count": len(results),
            "latency_ms": latency,
            "top_score": results[0]['similarity_score'] if results else None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.query_metrics.insert_one(metrics_doc)
        
        return {
            "results": results,
            "metrics": {
                "query": query.vibe,
                "results_count": len(results),
                "latency_ms": latency,
                "top_score": results[0]['similarity_score'] if results else None,
                "threshold_used": query.threshold,
                "message": "Good match found!" if results and results[0]['similarity_score'] > 0.8 else 
                          "Matches found" if results else "No matches above threshold. Try different vibes!"
            }
        }
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/metrics", response_model=List[QueryMetrics])
async def get_metrics():
    """Get all query metrics"""
    try:
        metrics = await db.query_metrics.find({}, {"_id": 0}).sort("timestamp", -1).to_list(50)
        for metric in metrics:
            if isinstance(metric.get('timestamp'), str):
                metric['timestamp'] = datetime.fromisoformat(metric['timestamp'])
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/products/all")
async def delete_all_products():
    """Delete all products"""
    try:
        result = await db.products.delete_many({})
        return {"deleted_count": result.deleted_count}
    except Exception as e:
        logger.error(f"Error deleting products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/products/seed")
async def seed_products():
    """Seed database with sample fashion products"""
    sample_products = [
        {
            "name": "Boho Maxi Dress",
            "description": "Flowy, earthy-toned maxi dress with vibrant floral patterns. Perfect for festival vibes and summer adventures.",
            "vibe_tags": ["boho", "festival", "earthy", "flowy", "nature-inspired"],
            "category": "dresses",
            "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400"
        },
        {
            "name": "Cozy Knit Sweater",
            "description": "Oversized chunky knit sweater in warm cream. Soft and comfortable for lounging or casual outings.",
            "vibe_tags": ["cozy", "comfort", "casual", "warm", "relaxed"],
            "category": "tops",
            "image_url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=400"
        },
        {
            "name": "Urban Leather Jacket",
            "description": "Sleek black leather jacket with edgy details. Perfect for energetic urban chic style and night outs.",
            "vibe_tags": ["urban", "edgy", "energetic", "chic", "bold"],
            "category": "outerwear",
            "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400"
        },
        {
            "name": "Minimalist Linen Pants",
            "description": "Clean-cut linen pants in neutral beige. Breathable and elegant for a minimal aesthetic.",
            "vibe_tags": ["minimalist", "clean", "elegant", "neutral", "breathable"],
            "category": "bottoms",
            "image_url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=400"
        },
        {
            "name": "Vintage Denim Jacket",
            "description": "Distressed light-wash denim jacket with retro patches. Gives off nostalgic, carefree vibes.",
            "vibe_tags": ["vintage", "retro", "nostalgic", "casual", "carefree"],
            "category": "outerwear",
            "image_url": "https://images.unsplash.com/photo-1576871337632-b9aef4c17ab9?w=400"
        },
        {
            "name": "Athleisure Track Set",
            "description": "Matching sporty track jacket and pants in sleek black. Comfortable yet stylish for active lifestyles.",
            "vibe_tags": ["sporty", "active", "modern", "comfortable", "athleisure"],
            "category": "sets",
            "image_url": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400"
        },
        {
            "name": "Romantic Silk Blouse",
            "description": "Delicate silk blouse in soft blush pink with ruffled details. Feminine and elegant for special occasions.",
            "vibe_tags": ["romantic", "feminine", "elegant", "delicate", "dressy"],
            "category": "tops",
            "image_url": "https://images.unsplash.com/photo-1618932260643-eee4a2f652a6?w=400"
        },
        {
            "name": "Grunge Plaid Shirt",
            "description": "Oversized flannel shirt in dark red and black plaid. Edgy alternative style for rebellious spirits.",
            "vibe_tags": ["grunge", "alternative", "edgy", "rebellious", "oversized"],
            "category": "tops",
            "image_url": "https://images.unsplash.com/photo-1602293589930-45aad59ba3ab?w=400"
        },
        {
            "name": "Tropical Print Shorts",
            "description": "Bright tropical print shorts with palm leaves and exotic flowers. Fun beach and vacation vibes.",
            "vibe_tags": ["tropical", "fun", "beach", "vacation", "colorful"],
            "category": "bottoms",
            "image_url": "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=400"
        },
        {
            "name": "Sophisticated Blazer",
            "description": "Tailored navy blazer with clean lines. Professional and polished for corporate or formal settings.",
            "vibe_tags": ["sophisticated", "professional", "polished", "corporate", "tailored"],
            "category": "outerwear",
            "image_url": "https://images.unsplash.com/photo-1507680434567-5739c80be1ac?w=400"
        }
    ]
    
    try:
        created_products = []
        for product_data in sample_products:
            product_input = ProductCreate(**product_data)
            # Generate embedding
            combined_text = f"{product_input.name}. {product_input.description}. Vibes: {', '.join(product_input.vibe_tags)}"
            embedding = generate_embedding(combined_text)
            
            product = Product(
                name=product_input.name,
                description=product_input.description,
                vibe_tags=product_input.vibe_tags,
                category=product_input.category,
                image_url=product_input.image_url,
                embedding=embedding
            )
            
            doc = product.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            
            await db.products.insert_one(doc)
            created_products.append(product.name)
        
        return {
            "message": "Products seeded successfully",
            "count": len(created_products),
            "products": created_products
        }
    except Exception as e:
        logger.error(f"Error seeding products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()