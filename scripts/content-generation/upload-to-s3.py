#!/usr/bin/env python3
"""
Upload BookDash stories to S3 and generate DynamoDB seed

What it does:
1. Adds missing DynamoDB fields (s3_key, thumbnail_url, published)
2. Uploads story JSONs to S3: stories/{story_id}.json
3. Uploads images to S3: images/{story_id}/page-N.jpg
4. Generates DynamoDB seed JSON
"""

import json
import boto3
from pathlib import Path
from botocore.exceptions import ClientError

BOOKDASH_DIR = Path(__file__).parent / "content" / "bookdash"
DYNAMODB_SEED_FILE = Path(__file__).parent / "dynamodb-seed-stories.json"

# S3 configuration
BUCKET_NAME = "twinklepod-stories-beta"
CLOUDFRONT_BASE = "https://d3lncscy0tzgzt.cloudfront.net"

def upload_to_s3(local_path, s3_key, content_type="application/json"):
    """Upload file to S3"""
    s3 = boto3.client('s3')
    try:
        s3.upload_file(
            str(local_path),
            BUCKET_NAME,
            s3_key,
            ExtraArgs={'ContentType': content_type}
        )
        return True
    except ClientError as e:
        print(f"    ❌ S3 upload failed: {e}")
        return False

def process_story(json_file, index, total):
    """Process and upload a single story"""
    with open(json_file) as f:
        story = json.load(f)
    
    story_id = story["story_id"]
    title = story["title"]
    
    print(f"[{index}/{total}] 📚 {title}")
    
    # Add DynamoDB fields
    story["s3_key"] = f"stories/{story_id}.json"
    story["thumbnail_url"] = f"{CLOUDFRONT_BASE}/images/{story_id}/page-1.jpg"
    story["published"] = True
    
    # Save updated JSON
    with open(json_file, 'w') as f:
        json.dump(story, f, indent=2)
    
    # Upload story JSON to S3
    print(f"        📄 Uploading JSON...", end="", flush=True)
    if upload_to_s3(json_file, story["s3_key"], "application/json"):
        print(" ✓")
    else:
        print(" ✗ FAILED")
        return None
    
    # Upload images to S3
    image_dir = BOOKDASH_DIR / story_id / "images"
    if image_dir.exists():
        images = sorted(image_dir.glob("*.jpg"))
        print(f"        🖼️  Uploading {len(images)} images...", end="", flush=True)
        
        uploaded_count = 0
        for img_file in images:
            s3_key = f"images/{story_id}/{img_file.name}"
            if upload_to_s3(img_file, s3_key, "image/jpeg"):
                uploaded_count += 1
            else:
                print(f" ✗ FAILED at {img_file.name}")
                return None
        
        print(f" ✓ ({uploaded_count} images)")
    else:
        print(f"        ⚠️  No images directory found")
    
    # Create DynamoDB item (without pages array)
    dynamodb_item = {
        "story_id": story["story_id"],
        "title": story["title"],
        "age_range": story["age_range"],
        "categories": story["categories"],
        "tags": story["tags"],
        "s3_key": story["s3_key"],
        "thumbnail_url": story["thumbnail_url"],
        "duration_minutes": story["duration_minutes"],
        "page_count": story["page_count"],
        "author": story["author"],
        "license": story.get("license", "CC-BY 4.0"),
        "source": story.get("source", ""),
        "published": story["published"],
        "created_at": story["created_at"]
    }
    
    return dynamodb_item

def main():
    print("🚀 Uploading stories to S3...")
    print(f"📦 Bucket: {BUCKET_NAME}\n")
    
    json_files = sorted(BOOKDASH_DIR.glob("*.json"))
    total = len(json_files)
    
    stories = []
    uploaded = 0
    failed = 0
    
    for index, json_file in enumerate(json_files, 1):
        try:
            dynamodb_item = process_story(json_file, index, total)
            if dynamodb_item:
                stories.append(dynamodb_item)
                uploaded += 1
            else:
                failed += 1
        except Exception as e:
            print(f"        ❌ Error: {e}")
            failed += 1
        print()
    
    # Save DynamoDB seed
    print(f"💾 Saving DynamoDB seed...")
    with open(DYNAMODB_SEED_FILE, 'w') as f:
        json.dump(stories, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✅ Uploaded: {uploaded}/{total} stories")
    if failed > 0:
        print(f"❌ Failed: {failed}/{total} stories")
    print(f"📄 DynamoDB seed: {DYNAMODB_SEED_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
