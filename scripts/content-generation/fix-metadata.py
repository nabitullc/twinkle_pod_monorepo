#!/usr/bin/env python3
"""
Fix BookDash story metadata to match MVP spec

Issues to fix:
1. Duplicate CloudFront URL prefix in image paths
2. Change age_range from "3-8" to "3-6"
3. Convert category (string) to categories (array)
4. Add created_at timestamp
5. Remove "note" field
"""

import json
from pathlib import Path
from datetime import datetime

BOOKDASH_DIR = Path(__file__).parent / "content" / "bookdash"

def fix_story(json_file):
    """Fix metadata for a single story"""
    with open(json_file) as f:
        story = json.load(f)
    
    # Fix 1: Normalize image URLs
    for page in story.get("pages", []):
        if "image" in page:
            image_url = page["image"]
            
            # Remove all CloudFront prefixes first
            image_url = image_url.replace("https://cdn.twinklepod.com/", "")
            
            # Ensure it starts with "images/"
            if not image_url.startswith("images/"):
                image_url = f"images/{image_url}"
            
            # Add single CloudFront prefix
            page["image"] = f"https://cdn.twinklepod.com/{image_url}"
    
    # Fix 2: Change age_range to "3-6"
    story["age_range"] = "3-6"
    
    # Fix 3: Convert category to categories array
    if "category" in story:
        category = story.pop("category")
        if "categories" not in story:
            story["categories"] = [category] if category != "general" else []
    
    # Fix 4: Add created_at if missing
    if "created_at" not in story:
        story["created_at"] = "2025-01-01T00:00:00Z"
    
    # Fix 5: Remove note field
    story.pop("note", None)
    
    # Save fixed story
    with open(json_file, 'w') as f:
        json.dump(story, f, indent=2)
    
    return story["title"]

def main():
    print("🔧 Fixing story metadata...")
    
    fixed_count = 0
    for json_file in sorted(BOOKDASH_DIR.glob("*.json")):
        try:
            title = fix_story(json_file)
            print(f"  ✅ {title}")
            fixed_count += 1
        except Exception as e:
            print(f"  ❌ {json_file.name}: {e}")
    
    print(f"\n✅ Fixed {fixed_count} stories")

if __name__ == "__main__":
    main()
