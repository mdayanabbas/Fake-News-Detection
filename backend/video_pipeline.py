"""
Complete video generation pipeline
Orchestrates content generation, TTS, image sourcing, and video creation
"""
import asyncio
import os
import uuid
from typing import Dict, List, Optional
from datetime import datetime

from content_generators import ContentGenerator
from tts_service import TTSService
from image_service import ImageService
from video_service import VideoService

class VideoPipeline:
    def __init__(self):
        self.content_generator = ContentGenerator()
        self.tts_service = TTSService()
        self.image_service = ImageService()
        self.video_service = VideoService()
        
        # Pipeline tracking
        self.active_jobs = {}

    async def generate_youtube_shorts(self, niche: str, count: int = 5, 
                                    voice_type: str = "female_calm") -> Dict:
        """
        Complete pipeline to generate YouTube shorts
        
        Args:
            niche: Content niche (e.g., "cartoon comedy videos")
            count: Number of videos to generate
            voice_type: TTS voice type
            
        Returns:
            Dictionary with generation results
        """
        job_id = str(uuid.uuid4())
        
        try:
            print(f"🚀 Starting video generation job {job_id}")
            print(f"📝 Niche: {niche}")
            print(f"🎬 Count: {count}")
            
            # Track job start
            self.active_jobs[job_id] = {
                "status": "started",
                "niche": niche,
                "count": count,
                "started_at": datetime.now(),
                "current_step": "content_generation"
            }
            
            # Step 1: Generate content for each video
            print("📚 Step 1: Generating content...")
            content_list = self.content_generator.generate_content(niche, count)
            
            if not content_list:
                return {
                    "job_id": job_id,
                    "status": "failed",
                    "error": "Failed to generate content"
                }
            
            print(f"✅ Generated {len(content_list)} content pieces")
            
            # Update job status
            self.active_jobs[job_id]["current_step"] = "audio_generation"
            
            # Step 2: Generate audio for all content
            print("🎤 Step 2: Generating audio...")
            audio_files = await self.tts_service.generate_batch_speech(
                content_list, voice_type
            )
            
            if not audio_files:
                return {
                    "job_id": job_id,
                    "status": "failed", 
                    "error": "Failed to generate audio"
                }
            
            print(f"✅ Generated {len(audio_files)} audio files")
            
            # Update job status
            self.active_jobs[job_id]["current_step"] = "image_sourcing"
            
            # Step 3: Source images for each content piece
            print("🖼️ Step 3: Sourcing images...")
            image_batches = {}
            
            for content in content_list:
                content_id = content["id"]
                
                # Search for images based on content keywords
                images = await self.image_service.search_images(
                    content["keywords"], count=3
                )
                
                if images:
                    # Download images
                    downloaded_images = await self.image_service.download_images(
                        images, f"/tmp/images_{content_id}"
                    )
                    image_batches[content_id] = list(downloaded_images.values())
                
                # Small delay between requests
                await asyncio.sleep(0.5)
            
            print(f"✅ Sourced images for {len(image_batches)} videos")
            
            # Update job status
            self.active_jobs[job_id]["current_step"] = "video_creation"
            
            # Step 4: Create videos
            print("🎬 Step 4: Creating videos...")
            video_results = await self.video_service.create_batch_videos(
                content_list, audio_files, image_batches
            )
            
            # Count successful videos
            successful_videos = [v for v in video_results if v["status"] == "success"]
            
            print(f"✅ Created {len(successful_videos)} videos successfully")
            
            # Final result
            result = {
                "job_id": job_id,
                "status": "completed",
                "niche": niche,
                "total_requested": count,
                "successful_videos": len(successful_videos),
                "videos": video_results,
                "generated_at": datetime.now().isoformat()
            }
            
            # Update job status
            self.active_jobs[job_id].update({
                "status": "completed",
                "current_step": "finished",
                "result": result
            })
            
            return result
            
        except Exception as e:
            error_result = {
                "job_id": job_id,
                "status": "failed",
                "error": str(e),
                "niche": niche
            }
            
            # Update job status
            if job_id in self.active_jobs:
                self.active_jobs[job_id].update({
                    "status": "failed",
                    "error": str(e)
                })
            
            print(f"❌ Pipeline failed: {e}")
            return error_result

    async def generate_single_video_fast(self, niche: str, 
                                       voice_type: str = "female_calm") -> Dict:
        """
        Quick generation of a single video for testing
        """
        try:
            print(f"🚀 Quick single video generation for: {niche}")
            
            # Generate one piece of content
            content_list = self.content_generator.generate_content(niche, 1)
            if not content_list:
                return {"status": "failed", "error": "Content generation failed"}
            
            content = content_list[0]
            
            # Generate audio
            audio_path = await self.tts_service.generate_speech(
                content["script"], voice_type
            )
            if not audio_path:
                return {"status": "failed", "error": "Audio generation failed"}
            
            # Get images
            images = await self.image_service.search_images(content["keywords"], 3)
            if not images:
                return {"status": "failed", "error": "Image sourcing failed"}
            
            # Download images
            downloaded_images = await self.image_service.download_images(images)
            image_paths = list(downloaded_images.values())
            
            # Create video
            video_path = await self.video_service.create_video(
                content, audio_path, image_paths
            )
            
            if video_path:
                return {
                    "status": "success",
                    "video_id": content["id"],
                    "title": content["title"],
                    "video_path": video_path,
                    "niche": niche
                }
            else:
                return {"status": "failed", "error": "Video creation failed"}
                
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def get_job_status(self, job_id: str) -> Dict:
        """Get status of a generation job"""
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        else:
            return {"error": "Job not found"}

    def get_available_niches(self) -> List[str]:
        """Get list of available content niches"""
        return self.content_generator.get_available_niches()

    def get_available_voices(self) -> Dict:
        """Get list of available TTS voices"""
        return self.tts_service.get_available_voices()

# Test the complete pipeline
async def test_pipeline():
    """Test the complete video generation pipeline"""
    pipeline = VideoPipeline()
    
    print("🧪 Testing complete video generation pipeline...")
    
    # Test quick single video generation
    result = await pipeline.generate_single_video_fast("Cartoon Comedy Videos")
    
    if result["status"] == "success":
        print(f"✅ Pipeline test successful!")
        print(f"📺 Video: {result['title']}")
        print(f"📁 Path: {result['video_path']}")
        return True
    else:
        print(f"❌ Pipeline test failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_pipeline())