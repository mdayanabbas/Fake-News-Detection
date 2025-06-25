"""
Text-to-Speech service using Edge TTS (completely free)
"""
import edge_tts
import asyncio
import os
import uuid
from typing import Optional

class TTSService:
    def __init__(self):
        # Soothing voices available in Edge TTS
        self.soothing_voices = {
            "female_calm": "en-US-AriaNeural",
            "female_gentle": "en-US-EmmaNeural", 
            "female_warm": "en-US-JennyNeural",
            "male_calm": "en-US-GuyNeural",
            "male_gentle": "en-US-BrandonNeural"
        }
        
        # Default voice for calm narration
        self.default_voice = "en-US-AriaNeural"
        
    async def generate_speech(self, text: str, voice_type: str = "female_calm", 
                            output_dir: str = "/tmp/audio") -> str:
        """
        Generate speech from text using Edge TTS
        
        Args:
            text: Text to convert to speech
            voice_type: Type of soothing voice to use
            output_dir: Directory to save audio file
            
        Returns:
            Path to generated audio file
        """
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Select voice
            voice_id = self.soothing_voices.get(voice_type, self.default_voice)
            
            # Generate unique filename
            audio_id = str(uuid.uuid4())
            output_file = os.path.join(output_dir, f"{audio_id}.mp3")
            
            # Configure TTS with calm settings
            tts = edge_tts.Communicate(
                text=text,
                voice=voice_id,
                rate="-10%",  # Slightly slower for calmness
                pitch="-5Hz"  # Slightly lower pitch for soothing effect
            )
            
            # Generate and save audio
            await tts.save(output_file)
            
            return output_file
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None
    
    async def generate_batch_speech(self, content_list: list, 
                                  voice_type: str = "female_calm") -> dict:
        """
        Generate speech for multiple content pieces
        
        Args:
            content_list: List of content dictionaries with scripts
            voice_type: Type of soothing voice to use
            
        Returns:
            Dictionary mapping content IDs to audio file paths
        """
        audio_files = {}
        
        for content in content_list:
            try:
                audio_path = await self.generate_speech(
                    text=content["script"],
                    voice_type=voice_type
                )
                
                if audio_path:
                    audio_files[content["id"]] = audio_path
                    print(f"Generated audio for: {content['title']}")
                    
            except Exception as e:
                print(f"Error generating audio for {content['id']}: {e}")
                
        return audio_files
    
    def get_available_voices(self) -> dict:
        """Return available soothing voice options"""
        return {
            "female_calm": "Aria - Calm and soothing female voice",
            "female_gentle": "Emma - Gentle and warm female voice",
            "female_warm": "Jenny - Warm and friendly female voice", 
            "male_calm": "Guy - Calm and reassuring male voice",
            "male_gentle": "Brandon - Gentle and smooth male voice"
        }

# Test function to verify TTS works
async def test_tts():
    """Test function to verify Edge TTS is working"""
    tts = TTSService()
    
    test_text = "Hello! This is a test of our soothing text-to-speech system. The voice should sound calm and peaceful."
    
    print("Testing Edge TTS...")
    audio_file = await tts.generate_speech(test_text, "female_calm")
    
    if audio_file and os.path.exists(audio_file):
        print(f"✅ TTS test successful! Audio saved to: {audio_file}")
        return True
    else:
        print("❌ TTS test failed")
        return False

if __name__ == "__main__":
    # Run test
    asyncio.run(test_tts())