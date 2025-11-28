#!/usr/bin/env python3
"""
Generate sample stories for MVP testing
Note: Replace with real StoryWeaver stories or custom content for production
"""

import json
import uuid
from pathlib import Path
from datetime import datetime

SAMPLE_STORIES = [
    {
        "category": "bedtime",
        "age_range": "3-5",
        "title": "The Sleepy Moon",
        "pages": [
            {"text": "Once upon a time, the moon was very sleepy.", "image_placeholder": "moon-1.jpg"},
            {"text": "All the stars sang a lullaby to help the moon sleep.", "image_placeholder": "moon-2.jpg"},
            {"text": "And the moon fell asleep with a smile.", "image_placeholder": "moon-3.jpg"}
        ],
        "tags": ["bedtime", "moon", "sleep"],
        "moral": "Everyone needs rest"
    },
    {
        "category": "animals",
        "age_range": "3-5",
        "title": "The Brave Little Rabbit",
        "pages": [
            {"text": "Ruby the rabbit loved to explore the meadow.", "image_placeholder": "rabbit-1.jpg"},
            {"text": "One day, she found a baby bird that needed help.", "image_placeholder": "rabbit-2.jpg"},
            {"text": "Ruby helped the bird back to its nest.", "image_placeholder": "rabbit-3.jpg"}
        ],
        "tags": ["animals", "courage", "kindness"],
        "moral": "Helping others makes you brave"
    }
]

def generate_story(template, story_id):
    """Generate story in TwinklePod format"""
    return {
        "story_id": story_id,
        "title": template["title"],
        "pages": [
            {
                "text": page["text"],
                "image": f"https://cdn.twinklepod.com/images/{story_id}/{page['image_placeholder']}"
            }
            for page in template["pages"]
        ],
        "age_range": template["age_range"],
        "category": template["category"],
        "tags": template["tags"],
        "moral": template.get("moral", ""),
        "duration_minutes": len(template["pages"]),
        "page_count": len(template["pages"]),
        "author": "TwinklePod",
        "license": "Sample Content",
        "created_at": datetime.utcnow().isoformat()
    }

def main():
    output_dir = Path("content/sample-stories")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("📝 Generating sample stories for testing...\n")
    
    stories = []
    for template in SAMPLE_STORIES:
        story_id = str(uuid.uuid4())
        story = generate_story(template, story_id)
        stories.append(story)
        
        # Save individual story
        filename = f"{template['category']}_{story_id}.json"
        with open(output_dir / filename, "w") as f:
            json.dump(story, f, indent=2)
        
        print(f"✅ Generated: {story['title']}")
    
    # Save manifest
    manifest = {
        "total_stories": len(stories),
        "note": "Sample stories for MVP testing. Replace with real content.",
        "stories": stories
    }
    
    with open(output_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Generated {len(stories)} sample stories")
    print(f"📁 Saved to: {output_dir}")
    print("\n⚠️  Note: These are sample stories for testing.")
    print("   For production, use StoryWeaver stories or create original content.")

if __name__ == "__main__":
    main()
