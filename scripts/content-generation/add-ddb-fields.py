#!/usr/bin/env python3
"""
Add missing DynamoDB fields to story JSONs
"""

import json
from pathlib import Path

BOOKDASH_DIR = Path(__file__).parent / "content" / "bookdash"
CLOUDFRONT_BASE = "https://cdn.twinklepod.com"

def add_fields(json_file):
    with open(json_file) as f:
        story = json.load(f)
    
    story_id = story["story_id"]
    
    # Add missing fields
    story["s3_key"] = f"stories/{story_id}.json"
    story["thumbnail_url"] = f"{CLOUDFRONT_BASE}/images/{story_id}/page-1.jpg"
    story["published"] = True
    
    # Save
    with open(json_file, 'w') as f:
        json.dump(story, f, indent=2)
    
    return story["title"]

def main():
    print("🔧 Adding DynamoDB fields...")
    
    count = 0
    for json_file in sorted(BOOKDASH_DIR.glob("*.json")):
        title = add_fields(json_file)
        print(f"  ✅ {title}")
        count += 1
    
    print(f"\n✅ Updated {count} stories")

if __name__ == "__main__":
    main()
