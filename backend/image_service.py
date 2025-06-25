"""
Image service for sourcing cartoon-style images
Uses free APIs and fallback methods
"""
import requests
import os
import uuid
import asyncio
import aiohttp
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import random

class ImageService:
    def __init__(self):
        # Free image APIs (no keys required for basic access)
        self.pixabay_url = "https://pixabay.com/api/"
        self.unsplash_url = "https://api.unsplash.com/photos/random"
        
        # Fallback: Generate simple cartoon-style images locally
        self.colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
            "#DDA0DD", "#98D8C8", "#FFCCCB", "#FFE4B5", "#E6E6FA"
        ]

    async def search_images(self, keywords: List[str], count: int = 5) -> List[Dict]:
        """
        Search for images using multiple sources
        
        Args:
            keywords: List of search keywords
            count: Number of images to find
            
        Returns:
            List of image dictionaries with URLs and metadata
        """
        all_images = []
        
        # Try different search strategies
        for keyword in keywords[:2]:  # Limit to first 2 keywords to avoid too many requests
            try:
                # Search Pixabay (free, no API key needed for basic access)
                pixabay_images = await self._search_pixabay(keyword, count // 2)
                all_images.extend(pixabay_images)
                
                # Add small delay to be respectful
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error searching images for {keyword}: {e}")
        
        # If we don't have enough images, generate some locally
        while len(all_images) < count:
            generated_image = self._generate_cartoon_image(keywords[0] if keywords else "cartoon")
            all_images.append(generated_image)
        
        return all_images[:count]

    async def _search_pixabay(self, query: str, per_page: int = 3) -> List[Dict]:
        """Search Pixabay for images (free tier)"""
        try:
            # Pixabay allows basic access without API key (limited)
            params = {
                "q": f"{query} cartoon illustration",
                "image_type": "illustration",
                "category": "backgrounds",
                "safesearch": "true",
                "per_page": per_page
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.pixabay_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        images = []
                        
                        for hit in data.get("hits", [])[:per_page]:
                            images.append({
                                "id": str(uuid.uuid4()),
                                "url": hit.get("webformatURL", ""),
                                "source": "pixabay",
                                "keywords": [query],
                                "width": hit.get("webformatWidth", 640),
                                "height": hit.get("webformatHeight", 480)
                            })
                        
                        return images
                    
        except Exception as e:
            print(f"Pixabay search error: {e}")
            
        return []

    def _generate_cartoon_image(self, theme: str) -> Dict:
        """
        Generate a simple cartoon-style image locally as fallback
        """
        try:
            # Create a 640x480 image
            width, height = 640, 480
            img = Image.new('RGB', (width, height), random.choice(self.colors))
            draw = ImageDraw.Draw(img)
            
            # Add some simple shapes to make it look cartoon-like
            self._add_cartoon_elements(draw, width, height, theme)
            
            # Save the image
            image_id = str(uuid.uuid4())
            output_dir = "/tmp/generated_images"
            os.makedirs(output_dir, exist_ok=True)
            
            image_path = os.path.join(output_dir, f"{image_id}.png")
            img.save(image_path)
            
            return {
                "id": image_id,
                "url": image_path,
                "source": "generated",
                "keywords": [theme],
                "width": width,
                "height": height
            }
            
        except Exception as e:
            print(f"Error generating cartoon image: {e}")
            return None

    def _add_cartoon_elements(self, draw, width, height, theme):
        """Add simple cartoon elements to the image"""
        try:
            # Define theme-based elements
            if "comedy" in theme.lower():
                # Add smiley faces and fun shapes
                self._draw_smiley(draw, width//4, height//4, 50)
                self._draw_star(draw, 3*width//4, height//4, 40)
                
            elif "horror" in theme.lower():
                # Add spooky but cute elements
                self._draw_moon(draw, width//2, height//4, 60)
                self._draw_cute_ghost(draw, width//4, 3*height//4, 80)
                
            elif "motivational" in theme.lower():
                # Add uplifting elements
                self._draw_sun(draw, width//2, height//4, 70)
                self._draw_mountain(draw, width//2, 3*height//4, 100)
                
            else:
                # Default elements
                self._draw_heart(draw, width//2, height//2, 60)
                
        except Exception as e:
            print(f"Error adding cartoon elements: {e}")

    def _draw_smiley(self, draw, x, y, size):
        """Draw a simple smiley face"""
        # Face
        draw.ellipse([x-size, y-size, x+size, y+size], fill="yellow", outline="black", width=3)
        # Eyes
        draw.ellipse([x-size//2, y-size//3, x-size//4, y-size//6], fill="black")
        draw.ellipse([x+size//4, y-size//3, x+size//2, y-size//6], fill="black")
        # Smile
        draw.arc([x-size//2, y, x+size//2, y+size//2], 0, 180, fill="black", width=3)

    def _draw_star(self, draw, x, y, size):
        """Draw a simple star"""
        points = []
        for i in range(10):
            angle = i * 36 * 3.14159 / 180
            if i % 2 == 0:
                radius = size
            else:
                radius = size // 2
            px = x + radius * (angle)**0.5 * 0.8
            py = y + radius * (angle)**0.5 * 0.6
            points.append((px, py))
        
        draw.polygon(points, fill="gold", outline="orange", width=2)

    def _draw_heart(self, draw, x, y, size):
        """Draw a simple heart"""
        draw.ellipse([x-size, y-size//2, x, y+size//2], fill="red")
        draw.ellipse([x, y-size//2, x+size, y+size//2], fill="red")
        draw.polygon([(x-size, y), (x, y+size), (x+size, y)], fill="red")

    def _draw_moon(self, draw, x, y, size):
        """Draw a crescent moon"""
        draw.ellipse([x-size, y-size, x+size, y+size], fill="lightyellow", outline="gold", width=3)
        draw.ellipse([x-size//2, y-size, x+size//2, y+size], fill="lightblue")

    def _draw_cute_ghost(self, draw, x, y, size):
        """Draw a cute ghost"""
        # Body
        draw.ellipse([x-size, y-size, x+size, y], fill="white", outline="lightgray", width=2)
        draw.rectangle([x-size, y-size//2, x+size, y+size//4], fill="white")
        # Eyes
        draw.ellipse([x-size//2, y-size//2, x-size//4, y-size//4], fill="black")
        draw.ellipse([x+size//4, y-size//2, x+size//2, y-size//4], fill="black")

    def _draw_sun(self, draw, x, y, size):
        """Draw a cheerful sun"""
        # Sun body
        draw.ellipse([x-size, y-size, x+size, y+size], fill="yellow", outline="orange", width=4)
        # Rays
        for i in range(8):
            angle = i * 45 * 3.14159 / 180
            x1 = x + size * 1.2 * (angle)**0.5 * 0.7
            y1 = y + size * 1.2 * (angle)**0.5 * 0.7
            x2 = x + size * 1.5 * (angle)**0.5 * 0.7
            y2 = y + size * 1.5 * (angle)**0.5 * 0.7
            draw.line([x1, y1, x2, y2], fill="orange", width=4)

    def _draw_mountain(self, draw, x, y, size):
        """Draw simple mountains"""
        # Mountain peaks
        points = [
            (x-size, y+size//2),
            (x-size//2, y-size//2),
            (x, y),
            (x+size//2, y-size//2),
            (x+size, y+size//2)
        ]
        draw.polygon(points, fill="green", outline="darkgreen", width=3)

    async def download_images(self, image_list: List[Dict], output_dir: str = "/tmp/downloads") -> Dict[str, str]:
        """
        Download images from URLs
        
        Args:
            image_list: List of image dictionaries
            output_dir: Directory to save images
            
        Returns:
            Dictionary mapping image IDs to local file paths
        """
        os.makedirs(output_dir, exist_ok=True)
        downloaded_files = {}
        
        async with aiohttp.ClientSession() as session:
            for image_data in image_list:
                try:
                    image_id = image_data["id"]
                    
                    # If it's already a local file, just copy the path
                    if image_data["source"] == "generated":
                        downloaded_files[image_id] = image_data["url"]
                        continue
                    
                    # Download remote image
                    async with session.get(image_data["url"]) as response:
                        if response.status == 200:
                            # Determine file extension
                            content_type = response.headers.get('content-type', '')
                            if 'jpeg' in content_type or 'jpg' in content_type:
                                ext = '.jpg'
                            elif 'png' in content_type:
                                ext = '.png'
                            else:
                                ext = '.jpg'
                            
                            # Save file
                            filename = f"{image_id}{ext}"
                            filepath = os.path.join(output_dir, filename)
                            
                            with open(filepath, 'wb') as f:
                                async for chunk in response.content.iter_chunked(8192):
                                    f.write(chunk)
                            
                            downloaded_files[image_id] = filepath
                            print(f"Downloaded image: {filename}")
                            
                        await asyncio.sleep(0.1)  # Be respectful with requests
                        
                except Exception as e:
                    print(f"Error downloading image {image_data['id']}: {e}")
        
        return downloaded_files

# Test function
async def test_image_service():
    """Test the image service"""
    service = ImageService()
    
    print("Testing image search...")
    keywords = ["cartoon", "funny", "character"]
    images = await service.search_images(keywords, 3)
    
    print(f"Found {len(images)} images")
    for img in images:
        print(f"- {img['source']}: {img['id']}")
    
    return len(images) > 0

if __name__ == "__main__":
    asyncio.run(test_image_service())