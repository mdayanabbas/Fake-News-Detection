"""
Content generators for different YouTube shorts niches
"""
import random
from typing import List, Dict
import uuid

class ContentGenerator:
    def __init__(self):
        self.cartoon_comedy_templates = [
            {
                "title": "When You Try to Act Cool But Fail",
                "scenes": [
                    "Picture a cartoon character trying to impress their friends",
                    "They attempt a cool trick or move",
                    "Everything goes hilariously wrong",
                    "Their friends burst into laughter",
                    "The character realizes being yourself is better than trying to be cool"
                ],
                "keywords": ["cartoon character", "funny fail", "comedy animation", "friendship"]
            },
            {
                "title": "The Epic Food Fight Adventure",
                "scenes": [
                    "A peaceful cartoon cafeteria scene",
                    "One character accidentally drops their lunch",
                    "Chaos erupts as food starts flying everywhere",
                    "Characters slip and slide on banana peels",
                    "Everyone ends up laughing and sharing their meals"
                ],
                "keywords": ["cartoon cafeteria", "food fight", "comedy chaos", "friendship"]
            },
            {
                "title": "The Magical Pet Mix-up",
                "scenes": [
                    "A cartoon character visits a magical pet shop",
                    "They accidentally grab the wrong pet",
                    "The pet has unexpected magical powers",
                    "Hilarious situations unfold with the magic",
                    "They discover the perfect pet was with them all along"
                ],
                "keywords": ["magical pet", "cartoon magic", "funny animals", "adventure"]
            }
        ]
        
        self.cartoon_horror_templates = [
            {
                "title": "The Friendly Ghost's Dilemma",
                "scenes": [
                    "A cute cartoon ghost appears in a cozy house",
                    "They just want to make friends with the family",
                    "Every attempt to be friendly accidentally scares people",
                    "The ghost feels sad and lonely",
                    "Finally, a brave child befriends the ghost and they become best friends"
                ],
                "keywords": ["friendly ghost", "cartoon scary", "cute horror", "friendship"]
            },
            {
                "title": "The Monster Under the Bed",
                "scenes": [
                    "A child hears strange noises at night",
                    "They discover a cute monster under their bed",
                    "The monster is actually afraid of the dark",
                    "The child comforts the scared monster",
                    "They become nighttime buddies who protect each other"
                ],
                "keywords": ["monster under bed", "cute monster", "cartoon horror", "friendship"]
            },
            {
                "title": "The Haunted Library Mystery",
                "scenes": [
                    "Books start floating mysteriously in a cartoon library",
                    "A brave librarian investigates the strange events",
                    "They discover a bookworm ghost who loves reading",
                    "The ghost just wants someone to discuss stories with",
                    "They start a supernatural book club together"
                ],
                "keywords": ["haunted library", "ghost books", "cartoon mystery", "reading"]
            }
        ]
        
        self.motivational_templates = [
            {
                "title": "The Power of Small Steps",
                "scenes": [
                    "A cartoon character dreams of climbing a huge mountain",
                    "They feel overwhelmed by the enormous task",
                    "A wise mentor shows them to focus on one step at a time",
                    "Slowly but surely, they make progress each day",
                    "They reach the summit and realize every journey begins with a single step"
                ],
                "keywords": ["mountain climbing", "motivation", "small steps", "achievement"]
            },
            {
                "title": "The Seed of Persistence",
                "scenes": [
                    "A small seed is planted in difficult, rocky soil",
                    "Many other seeds give up when faced with obstacles",
                    "This little seed keeps pushing through the rocks",
                    "Day by day, it grows stronger and more determined",
                    "Finally, it becomes a beautiful tree that inspires all other plants"
                ],
                "keywords": ["growing seed", "persistence", "motivation", "growth mindset"]
            },
            {
                "title": "The Comeback Story",
                "scenes": [
                    "A cartoon athlete faces a devastating defeat",
                    "They feel like giving up on their dreams",
                    "With support from family and friends, they start training again",
                    "Through hard work and dedication, they improve daily",
                    "They make an incredible comeback and achieve their goals"
                ],
                "keywords": ["comeback story", "perseverance", "sports motivation", "never give up"]
            }
        ]

    def generate_content(self, niche: str, count: int = 5) -> List[Dict]:
        """Generate content for specified niche"""
        if niche.lower() == "cartoon comedy videos":
            templates = self.cartoon_comedy_templates
        elif niche.lower() == "cartoon horror videos":
            templates = self.cartoon_horror_templates
        elif niche.lower() == "motivational videos":
            templates = self.motivational_templates
        else:
            # Default to comedy if niche not found
            templates = self.cartoon_comedy_templates
        
        generated_content = []
        for i in range(count):
            template = random.choice(templates)
            content = {
                "id": str(uuid.uuid4()),
                "title": f"{template['title']} - Part {i+1}",
                "script": self._create_script(template["scenes"]),
                "scenes": template["scenes"],
                "keywords": template["keywords"],
                "niche": niche,
                "duration": 45 + (i * 5)  # 45-65 seconds
            }
            generated_content.append(content)
        
        return generated_content

    def _create_script(self, scenes: List[str]) -> str:
        """Convert scenes into a narration script"""
        script_parts = []
        for i, scene in enumerate(scenes):
            if i == 0:
                script_parts.append(f"Let me tell you an amazing story. {scene}")
            elif i == len(scenes) - 1:
                script_parts.append(f"And finally, {scene.lower()}")
            else:
                script_parts.append(f"Then, {scene.lower()}")
        
        return " ".join(script_parts)

    def get_available_niches(self) -> List[str]:
        """Return list of available niches"""
        return [
            "Cartoon Comedy Videos",
            "Cartoon Horror Videos", 
            "Motivational Videos"
        ]