from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import uuid
import asyncio
from datetime import datetime

# Import our video generation services
from video_pipeline import VideoPipeline
from content_generators import ContentGenerator

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

# Initialize video generation pipeline
video_pipeline = VideoPipeline()

# Pydantic models
class VideoGenerationRequest(BaseModel):
    niche: str
    count: int = 5
    voice_type: str = "female_calm"

class QuickVideoRequest(BaseModel):
    niche: str
    voice_type: str = "female_calm"

class GeneratedVideo(BaseModel):
    id: str
    title: str
    video_path: str
    thumbnail_url: str = ""
    duration: int
    description: str
    status: str

class VideoGenerationResponse(BaseModel):
    job_id: str
    status: str
    niche: str
    total_requested: int
    successful_videos: int
    videos: List[dict]
    message: str = ""

@app.get("/")
async def root():
    return {"message": "YouTube Shorts Generator API - Now with REAL video generation! 🎬"}

@app.get("/api/niches")
async def get_niches():
    """Get list of supported YouTube shorts niches"""
    niches = video_pipeline.get_available_niches()
    return {"niches": niches}

@app.get("/api/voices")
async def get_voices():
    """Get list of available TTS voices"""
    voices = video_pipeline.get_available_voices()
    return {"voices": voices}

@app.post("/api/generate-videos", response_model=VideoGenerationResponse)
async def generate_videos(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Generate multiple YouTube shorts for the selected niche"""
    try:
        # Validate niche
        available_niches = video_pipeline.get_available_niches()
        if request.niche not in available_niches:
            raise HTTPException(status_code=400, detail=f"Invalid niche. Available: {available_niches}")
        
        # Validate count
        if request.count < 1 or request.count > 10:
            raise HTTPException(status_code=400, detail="Count must be between 1 and 10")
        
        # Start video generation in background
        job_id = str(uuid.uuid4())
        
        # Store initial job in database
        job_data = {
            "job_id": job_id,
            "niche": request.niche,
            "count": request.count,
            "voice_type": request.voice_type,
            "status": "started",
            "created_at": datetime.now(),
            "videos": []
        }
        db.generation_jobs.insert_one(job_data)
        
        # Start background task
        background_tasks.add_task(
            run_video_generation_pipeline, 
            job_id, request.niche, request.count, request.voice_type
        )
        
        return VideoGenerationResponse(
            job_id=job_id,
            status="processing",
            niche=request.niche,
            total_requested=request.count,
            successful_videos=0,
            videos=[],
            message=f"Video generation started! Job ID: {job_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting video generation: {str(e)}")

@app.post("/api/quick-generate")
async def quick_generate_video(request: QuickVideoRequest):
    """Generate a single video quickly for testing"""
    try:
        available_niches = video_pipeline.get_available_niches()
        if request.niche not in available_niches:
            raise HTTPException(status_code=400, detail=f"Invalid niche. Available: {available_niches}")
        
        print(f"🚀 Starting quick video generation for: {request.niche}")
        
        # Generate single video
        result = await video_pipeline.generate_single_video_fast(
            request.niche, request.voice_type
        )
        
        if result["status"] == "success":
            # Store in database
            video_data = {
                "video_id": result["video_id"],
                "title": result["title"],
                "video_path": result["video_path"],
                "niche": result["niche"],
                "voice_type": request.voice_type,
                "created_at": datetime.now(),
                "type": "quick_generation"
            }
            db.videos.insert_one(video_data)
            
            return {
                "status": "success",
                "video": {
                    "id": result["video_id"],
                    "title": result["title"],
                    "video_path": result["video_path"],
                    "niche": result["niche"]
                },
                "message": "Video generated successfully!"
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Video generation failed"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in quick generation: {str(e)}")

@app.get("/api/job-status/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a video generation job"""
    try:
        # Check pipeline status
        pipeline_status = video_pipeline.get_job_status(job_id)
        
        # Also check database
        db_job = db.generation_jobs.find_one({"job_id": job_id})
        
        if db_job:
            db_job.pop('_id', None)  # Remove MongoDB _id
            return db_job
        elif pipeline_status.get("error") != "Job not found":
            return pipeline_status
        else:
            raise HTTPException(status_code=404, detail="Job not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting job status: {str(e)}")

@app.get("/api/download-video/{video_id}")
async def download_video(video_id: str):
    """Download a generated video"""
    try:
        # Find video in database
        video = db.videos.find_one({"video_id": video_id})
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        video_path = video["video_path"]
        
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=f"{video['title']}.mp4"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")

@app.get("/api/list-videos")
async def list_videos(limit: int = 20):
    """List recently generated videos"""
    try:
        videos = list(db.videos.find().sort("created_at", -1).limit(limit))
        
        # Clean up MongoDB _id fields
        for video in videos:
            video.pop('_id', None)
        
        return {"videos": videos}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing videos: {str(e)}")

@app.get("/api/test-pipeline")
async def test_pipeline():
    """Test the video generation pipeline"""
    try:
        print("🧪 Testing video generation pipeline...")
        
        # Test TTS
        from tts_service import test_tts
        tts_result = await test_tts()
        
        # Test Image Service
        from image_service import test_image_service
        image_result = await test_image_service()
        
        # Test Content Generator
        content_gen = ContentGenerator()
        content = content_gen.generate_content("Cartoon Comedy Videos", 1)
        content_result = len(content) > 0
        
        return {
            "tts_service": "✅ Working" if tts_result else "❌ Failed",
            "image_service": "✅ Working" if image_result else "❌ Failed", 
            "content_generator": "✅ Working" if content_result else "❌ Failed",
            "pipeline_status": "✅ Ready for video generation" if all([tts_result, image_result, content_result]) else "❌ Some components failed"
        }
        
    except Exception as e:
        return {"error": str(e)}

# Background task function
async def run_video_generation_pipeline(job_id: str, niche: str, count: int, voice_type: str):
    """Background task to run the complete video generation pipeline"""
    try:
        print(f"🎬 Background task started for job {job_id}")
        
        # Update job status
        db.generation_jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": "processing", "current_step": "starting_pipeline"}}
        )
        
        # Run the complete pipeline
        result = await video_pipeline.generate_youtube_shorts(niche, count, voice_type)
        
        # Update database with results
        update_data = {
            "status": result["status"],
            "completed_at": datetime.now(),
            "total_requested": result.get("total_requested", count),
            "successful_videos": result.get("successful_videos", 0),
            "videos": result.get("videos", [])
        }
        
        if result["status"] == "failed":
            update_data["error"] = result.get("error", "Unknown error")
        
        db.generation_jobs.update_one(
            {"job_id": job_id},
            {"$set": update_data}
        )
        
        # Store individual videos in videos collection
        if result.get("videos"):
            for video in result["videos"]:
                if video["status"] == "success":
                    video_data = {
                        "video_id": video["id"],
                        "title": video["title"],
                        "video_path": video.get("video_path", ""),
                        "duration": video.get("duration", 0),
                        "niche": niche,
                        "voice_type": voice_type,
                        "job_id": job_id,
                        "created_at": datetime.now()
                    }
                    db.videos.insert_one(video_data)
        
        print(f"✅ Background task completed for job {job_id}")
        
    except Exception as e:
        print(f"❌ Background task failed for job {job_id}: {e}")
        
        # Update job with error
        db.generation_jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now()
            }}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)