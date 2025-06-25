from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import uuid
import asyncio

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL')
client = MongoClient(MONGO_URL)
db = client.youtube_shorts_db

# Pydantic models
class VideoGenerationRequest(BaseModel):
    niche: str

class GeneratedVideo(BaseModel):
    id: str
    title: str
    video_url: str
    thumbnail_url: str
    duration: int
    description: str

class VideoGenerationResponse(BaseModel):
    videos: List[GeneratedVideo]
    niche: str
    generation_id: str

# Popular YouTube shorts niches
POPULAR_NICHES = [
    "Horror Stories",
    "Cartoon Animation", 
    "Gaming Highlights",
    "Food Recipes",
    "Life Hacks",
    "Funny Moments", 
    "Travel Vlogs",
    "Tech Reviews",
    "Fitness Tips",
    "DIY Crafts",
    "Pet Videos",
    "Music Covers",
    "Dance Challenges",
    "Beauty Tips",
    "Motivational Quotes"
]

@app.get("/")
async def root():
    return {"message": "YouTube Shorts Generator API"}

@app.get("/api/niches")
async def get_niches():
    """Get list of popular YouTube shorts niches"""
    return {"niches": POPULAR_NICHES}

@app.post("/api/generate-videos", response_model=VideoGenerationResponse)
async def generate_videos(request: VideoGenerationRequest):
    """Generate 5 YouTube shorts for the selected niche"""
    try:
        if request.niche not in POPULAR_NICHES:
            raise HTTPException(status_code=400, detail="Invalid niche selected")
        
        generation_id = str(uuid.uuid4())
        
        # For now, we'll create mock videos - this will be replaced with actual generation logic
        mock_videos = []
        for i in range(5):
            video = GeneratedVideo(
                id=str(uuid.uuid4()),
                title=f"{request.niche} Video {i+1}",
                video_url=f"https://example.com/video_{i+1}.mp4",
                thumbnail_url=f"https://example.com/thumb_{i+1}.jpg",
                duration=30 + (i * 5),  # 30-50 seconds
                description=f"Amazing {request.niche.lower()} content that will keep viewers engaged!"
            )
            mock_videos.append(video)
        
        # Store generation in database
        generation_data = {
            "generation_id": generation_id,
            "niche": request.niche,
            "videos": [video.dict() for video in mock_videos],
            "created_at": asyncio.get_event_loop().time()
        }
        
        db.generations.insert_one(generation_data)
        
        return VideoGenerationResponse(
            videos=mock_videos,
            niche=request.niche,
            generation_id=generation_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating videos: {str(e)}")

@app.get("/api/generation/{generation_id}")
async def get_generation(generation_id: str):
    """Get a specific generation by ID"""
    generation = db.generations.find_one({"generation_id": generation_id})
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    # Remove MongoDB's _id field
    generation.pop('_id', None)
    return generation

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)