"""
Video generation service for creating YouTube shorts
Combines audio, images, and effects into 9:16 format videos
"""
import os
import asyncio
import uuid
from typing import List, Dict, Optional
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import math

class VideoService:
    def __init__(self):
        self.output_dir = "/tmp/videos"
        self.temp_dir = "/tmp/video_temp"
        
        # YouTube Shorts specifications
        self.shorts_width = 1080
        self.shorts_height = 1920  # 9:16 aspect ratio
        self.default_fps = 24
        
        # Ensure directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    async def create_video(self, content: Dict, audio_path: str, 
                          image_paths: List[str]) -> Optional[str]:
        """
        Create a complete YouTube short video
        
        Args:
            content: Content data with title, script, etc.
            audio_path: Path to generated audio file
            image_paths: List of paths to images
            
        Returns:
            Path to generated video file
        """
        try:
            video_id = str(uuid.uuid4())
            temp_video_dir = os.path.join(self.temp_dir, video_id)
            os.makedirs(temp_video_dir, exist_ok=True)
            
            print(f"Creating video for: {content['title']}")
            
            # Step 1: Prepare images for 9:16 format
            processed_images = await self._prepare_images_for_shorts(
                image_paths, temp_video_dir
            )
            
            # Step 2: Get audio duration to determine timing
            audio_clip = AudioFileClip(audio_path)
            total_duration = audio_clip.duration
            
            # Step 3: Create video clips from images
            video_clips = self._create_image_clips(
                processed_images, total_duration, content
            )
            
            # Step 4: Combine clips with transitions
            final_video = self._combine_clips_with_transitions(video_clips)
            
            # Step 5: Add audio
            final_video = final_video.set_audio(audio_clip)
            
            # Step 6: Add title overlay
            final_video = self._add_title_overlay(final_video, content["title"])
            
            # Step 7: Export the final video
            output_path = os.path.join(self.output_dir, f"{video_id}.mp4")
            
            final_video.write_videofile(
                output_path,
                fps=self.default_fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=f'{temp_video_dir}/temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Cleanup
            final_video.close()
            audio_clip.close()
            
            print(f"✅ Video created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error creating video: {e}")
            return None

    async def _prepare_images_for_shorts(self, image_paths: List[str], 
                                       output_dir: str) -> List[str]:
        """
        Convert images to 9:16 format with proper sizing
        """
        processed_paths = []
        
        for i, image_path in enumerate(image_paths):
            try:
                # Open and process image
                with Image.open(image_path) as img:
                    # Convert to RGB if necessary
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Create 9:16 canvas
                    canvas = Image.new('RGB', (self.shorts_width, self.shorts_height), 
                                     color='#2C3E50')  # Dark blue background
                    
                    # Calculate scaling to fit image nicely
                    img_ratio = img.width / img.height
                    canvas_ratio = self.shorts_width / self.shorts_height
                    
                    if img_ratio > canvas_ratio:
                        # Image is wider, fit to width
                        new_width = self.shorts_width
                        new_height = int(self.shorts_width / img_ratio)
                    else:
                        # Image is taller, fit to height with some margin
                        new_height = int(self.shorts_height * 0.7)  # Use 70% of height
                        new_width = int(new_height * img_ratio)
                    
                    # Resize image
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Center image on canvas
                    x_offset = (self.shorts_width - new_width) // 2
                    y_offset = (self.shorts_height - new_height) // 2
                    
                    canvas.paste(img_resized, (x_offset, y_offset))
                    
                    # Add decorative border
                    self._add_decorative_border(canvas)
                    
                    # Save processed image
                    processed_path = os.path.join(output_dir, f"processed_{i}.jpg")
                    canvas.save(processed_path, quality=90)
                    processed_paths.append(processed_path)
                    
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
                
        return processed_paths

    def _add_decorative_border(self, canvas):
        """Add a subtle decorative border to the image"""
        draw = ImageDraw.Draw(canvas)
        
        # Add gradient-like border effect
        border_width = 10
        colors = ['#3498DB', '#2ECC71', '#E74C3C', '#F39C12']
        
        for i in range(border_width):
            color = colors[i % len(colors)]
            # Top and bottom
            draw.rectangle([i, i, self.shorts_width-i, i+2], fill=color)
            draw.rectangle([i, self.shorts_height-i-2, self.shorts_width-i, self.shorts_height-i], fill=color)
            # Left and right
            draw.rectangle([i, i, i+2, self.shorts_height-i], fill=color)
            draw.rectangle([self.shorts_width-i-2, i, self.shorts_width-i, self.shorts_height-i], fill=color)

    def _create_image_clips(self, image_paths: List[str], total_duration: float, 
                           content: Dict) -> List[VideoClip]:
        """
        Create video clips from processed images
        """
        clips = []
        
        if not image_paths:
            return clips
            
        # Calculate duration per image
        duration_per_image = total_duration / len(image_paths)
        
        for i, image_path in enumerate(image_paths):
            try:
                # Create image clip
                clip = ImageClip(image_path, duration=duration_per_image)
                
                # Add zoom effect for dynamic feel
                if i % 2 == 0:
                    # Zoom in effect
                    clip = clip.resize(lambda t: 1 + 0.1 * t / duration_per_image)
                else:
                    # Zoom out effect  
                    clip = clip.resize(lambda t: 1.1 - 0.1 * t / duration_per_image)
                
                # Set position
                clip = clip.set_position('center')
                
                clips.append(clip)
                
            except Exception as e:
                print(f"Error creating clip from {image_path}: {e}")
        
        return clips

    def _combine_clips_with_transitions(self, clips: List[VideoClip]) -> VideoClip:
        """
        Combine clips with smooth transitions
        """
        if not clips:
            # Create a default clip if no images
            return ColorClip(size=(self.shorts_width, self.shorts_height), 
                           color=(44, 62, 80), duration=30)
        
        if len(clips) == 1:
            return clips[0]
        
        # Add crossfade transitions between clips
        transition_duration = 0.5
        final_clips = []
        
        for i, clip in enumerate(clips):
            if i == 0:
                # First clip
                final_clips.append(clip)
            else:
                # Add crossfade transition
                prev_clip = final_clips[-1]
                
                # Overlap clips for transition
                clip = clip.set_start(prev_clip.end - transition_duration)
                clip = clip.crossfadein(transition_duration)
                
                final_clips.append(clip)
        
        return CompositeVideoClip(final_clips)

    def _add_title_overlay(self, video: VideoClip, title: str) -> VideoClip:
        """
        Add animated title overlay to the video
        """
        try:
            # Create title text clip
            title_clip = TextClip(
                title,
                fontsize=70,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=3
            ).set_duration(3.0).set_position(('center', 0.1), relative=True)
            
            # Add fade in/out effects
            title_clip = title_clip.fadeout(0.5).fadein(0.5)
            
            # Composite title over video
            final_video = CompositeVideoClip([video, title_clip])
            
            return final_video
            
        except Exception as e:
            print(f"Error adding title overlay: {e}")
            return video

    async def create_batch_videos(self, content_list: List[Dict], 
                                audio_files: Dict[str, str],
                                image_batches: Dict[str, List[str]]) -> List[Dict]:
        """
        Create multiple videos in batch
        
        Args:
            content_list: List of content data
            audio_files: Dictionary mapping content IDs to audio file paths
            image_batches: Dictionary mapping content IDs to image file lists
            
        Returns:
            List of video generation results
        """
        results = []
        
        for content in content_list:
            content_id = content["id"]
            
            if content_id in audio_files and content_id in image_batches:
                try:
                    video_path = await self.create_video(
                        content=content,
                        audio_path=audio_files[content_id],
                        image_paths=image_batches[content_id]
                    )
                    
                    if video_path:
                        result = {
                            "id": content_id,
                            "title": content["title"],
                            "video_path": video_path,
                            "duration": content.get("duration", 45),
                            "status": "success"
                        }
                    else:
                        result = {
                            "id": content_id,
                            "title": content["title"],
                            "status": "failed",
                            "error": "Video generation failed"
                        }
                    
                    results.append(result)
                    
                except Exception as e:
                    results.append({
                        "id": content_id,
                        "title": content["title"],
                        "status": "failed",
                        "error": str(e)
                    })
            else:
                results.append({
                    "id": content_id,
                    "title": content["title"],
                    "status": "failed",
                    "error": "Missing audio or images"
                })
        
        return results

    def get_video_info(self, video_path: str) -> Dict:
        """
        Get information about a generated video
        """
        try:
            if os.path.exists(video_path):
                clip = VideoFileClip(video_path)
                info = {
                    "duration": clip.duration,
                    "fps": clip.fps,
                    "size": clip.size,
                    "file_size": os.path.getsize(video_path)
                }
                clip.close()
                return info
            else:
                return {"error": "Video file not found"}
                
        except Exception as e:
            return {"error": str(e)}

# Test function
async def test_video_service():
    """Test the video service"""
    print("Testing video service...")
    
    service = VideoService()
    
    # Create a test video with dummy data
    test_content = {
        "id": "test-123",
        "title": "Test Video",
        "script": "This is a test video.",
        "duration": 10
    }
    
    # This would normally come from TTS and image services
    print("Note: This test requires actual audio and image files to work properly")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_video_service())