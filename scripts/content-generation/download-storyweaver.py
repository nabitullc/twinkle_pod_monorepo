#!/usr/bin/env python3
"""
Download stories from StoryWeaver (Pratham Books) API
License: CC-BY 4.0
"""

import requests
import json
import os
from pathlib import Path

# StoryWeaver API
API_BASE = "https://storyweaver.org.in/api/v1"

# Target distribution
STORY_TARGETS = {
    "bedtime": 20,
    "animals": 20,
    "moral": 15,
    "fantasy": 15,
    "short": 10,
    "funny": 10,
    "adventure": 10
}

AGE_RANGES = {
    "3+": {"min": 3, "max": 5, "target": 40},
    "5+": {"min": 5, "max": 7, "target": 40},
    "7+": {"min": 7, "max": 10, "target": 20}
}

def search_stories(category, age_min, age_max, limit=50):
    """Search StoryWeaver API for stories"""
    params = {
        "category": category,
        "reading_level": f"{age_min}-{age_max}",
        "per_page": limit,
        "sort": "most_read"
    }
    
    response = requests.get(f"{API_BASE}/stories", params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

def download_story(story_id):
    """Download story details and images"""
    response = requests.get(f"{API_BASE}/stories/{story_id}")
    if response.status_code == 200:
        return response.json()
    return None

def convert_to_twinklepod_format(story_data):
    """Convert StoryWeaver format to TwinklePod format"""
    pages = []
    
    # Extract pages from StoryWeaver format
    for page in story_data.get("pages", []):
        pages.append({
            "text": page.get("content", ""),
            "image": page.get("illustration_url", "")
        })
    
    return {
        "story_id": story_data.get("id"),
        "title": story_data.get("title"),
        "pages": pages,
        "age_range": story_data.get("reading_level", "3-8"),
        "category": story_data.get("category", "general"),
        "tags": story_data.get("tags", []),
        "moral": story_data.get("synopsis", ""),
        "duration_minutes": len(pages),
        "page_count": len(pages),
        "author": story_data.get("authors", ["StoryWeaver"])[0],
        "license": "CC-BY 4.0",
        "source": "StoryWeaver",
        "source_url": story_data.get("url", ""),
        "created_at": story_data.get("published_at", "")
    }

def main():
    output_dir = Path("content/storyweaver")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔍 Searching StoryWeaver for stories...")
    
    all_stories = []
    
    for category, target_count in STORY_TARGETS.items():
        print(f"\n📚 Category: {category} (target: {target_count})")
        
        for age_range, age_config in AGE_RANGES.items():
            stories = search_stories(
                category, 
                age_config["min"], 
                age_config["max"],
                limit=target_count
            )
            
            print(f"  Age {age_range}: Found {len(stories)} stories")
            
            for story in stories[:target_count]:
                story_id = story.get("id")
                print(f"    Downloading: {story.get('title')} (ID: {story_id})")
                
                full_story = download_story(story_id)
                if full_story:
                    converted = convert_to_twinklepod_format(full_story)
                    all_stories.append(converted)
                    
                    # Save individual story
                    story_file = output_dir / f"{category}_{age_range}_{story_id}.json"
                    with open(story_file, "w") as f:
                        json.dump(converted, f, indent=2)
    
    # Save manifest
    manifest = {
        "total_stories": len(all_stories),
        "source": "StoryWeaver (Pratham Books)",
        "license": "CC-BY 4.0",
        "downloaded_at": "2025-11-28",
        "stories": all_stories
    }
    
    with open(output_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Downloaded {len(all_stories)} stories")
    print(f"📁 Saved to: {output_dir}")
    print("\n⚠️  Remember to attribute: 'Stories from StoryWeaver (Pratham Books) - CC-BY 4.0'")

if __name__ == "__main__":
    main()
