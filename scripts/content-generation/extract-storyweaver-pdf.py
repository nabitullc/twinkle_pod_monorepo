#!/usr/bin/env python3
"""
Extract stories from downloaded StoryWeaver PDF/ZIP files
"""

import json
import zipfile
import os
from pathlib import Path
import uuid
from datetime import datetime

def extract_zip(zip_path, output_dir):
    """Extract ZIP file"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print(f"✅ Extracted: {zip_path}")

def process_storyweaver_folder(folder_path):
    """Process extracted StoryWeaver folder"""
    folder = Path(folder_path)
    
    # Find images
    images = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.png"))
    
    # Story ID from folder name
    story_id = str(uuid.uuid4())
    title = folder.name.replace("-", " ").title()
    
    # Create pages from images
    pages = []
    for i, img_path in enumerate(images):
        pages.append({
            "text": f"Page {i+1}",  # Placeholder - manually add text later
            "image": f"https://cdn.twinklepod.com/images/{story_id}/page-{i+1}.jpg"
        })
    
    story = {
        "story_id": story_id,
        "title": title,
        "pages": pages,
        "age_range": "3-8",  # Update manually
        "category": "general",  # Update manually
        "tags": [],
        "moral": "",
        "duration_minutes": len(pages),
        "page_count": len(pages),
        "author": "StoryWeaver",
        "license": "CC-BY 4.0",
        "source": "StoryWeaver (Pratham Books)",
        "source_url": "",  # Add manually
        "created_at": datetime.utcnow().isoformat()
    }
    
    return story, images

def main():
    downloads_dir = Path.home() / "Downloads"
    output_dir = Path("content/storyweaver-extracted")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔍 Looking for StoryWeaver ZIPs in Downloads folder...\n")
    
    # Find all ZIP files
    zip_files = list(downloads_dir.glob("*-*.zip"))
    
    if not zip_files:
        print("❌ No StoryWeaver ZIP files found in Downloads")
        print("   Download stories from: https://storyweaver.org.in")
        return
    
    stories = []
    
    for zip_file in zip_files:
        print(f"📦 Processing: {zip_file.name}")
        
        # Extract ZIP
        extract_dir = output_dir / zip_file.stem
        extract_zip(zip_file, extract_dir)
        
        # Process extracted folder
        story, images = process_storyweaver_folder(extract_dir)
        stories.append(story)
        
        # Save story JSON
        story_file = output_dir / f"{story['story_id']}.json"
        with open(story_file, "w") as f:
            json.dump(story, f, indent=2)
        
        print(f"  ✅ Created: {story['title']}")
        print(f"  📄 Story JSON: {story_file}")
        print(f"  🖼️  Images: {len(images)} files")
        print(f"  ⚠️  TODO: Add text to pages manually\n")
    
    # Save manifest
    manifest = {
        "total_stories": len(stories),
        "source": "StoryWeaver (Pratham Books)",
        "license": "CC-BY 4.0",
        "note": "Text needs to be added manually to each page",
        "stories": stories
    }
    
    with open(output_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Processed {len(stories)} stories")
    print(f"📁 Output: {output_dir}")
    print("\n📝 Next steps:")
    print("   1. Open each story JSON file")
    print("   2. Add text to each page (from PDF)")
    print("   3. Update category, age_range, tags")
    print("   4. Run upload-to-s3.py to upload")

if __name__ == "__main__":
    main()
