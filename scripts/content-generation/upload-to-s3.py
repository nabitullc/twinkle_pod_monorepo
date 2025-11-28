#!/usr/bin/env python3
"""
Upload stories to S3 with proper folder structure
"""

import json
import boto3
import requests
from pathlib import Path
from urllib.parse import urlparse

s3 = boto3.client('s3')
BUCKET_NAME = "twinklepod-stories-beta"

def download_image(url, local_path):
    """Download image from URL"""
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            f.write(response.content)
        return True
    return False

def upload_story(story_file):
    """Upload story JSON and images to S3"""
    with open(story_file) as f:
        story = json.load(f)
    
    story_id = story["story_id"]
    category = story["category"]
    age_range = story["age_range"].split("-")[0]  # "3-8" -> "3"
    
    # S3 paths
    story_key = f"stories/{category}/age-{age_range}/{story_id}.json"
    
    print(f"📤 Uploading: {story['title']}")
    
    # Download and upload images
    image_dir = Path(f"temp/images/{story_id}")
    image_dir.mkdir(parents=True, exist_ok=True)
    
    for i, page in enumerate(story["pages"]):
        image_url = page["image"]
        if image_url:
            local_image = image_dir / f"page-{i+1}.jpg"
            
            if download_image(image_url, local_image):
                # Upload to S3
                s3_image_key = f"images/{story_id}/page-{i+1}.jpg"
                s3.upload_file(
                    str(local_image),
                    BUCKET_NAME,
                    s3_image_key,
                    ExtraArgs={'ContentType': 'image/jpeg'}
                )
                
                # Update story JSON with CloudFront URL
                page["image"] = f"https://cdn.twinklepod.com/{s3_image_key}"
    
    # Upload story JSON
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=story_key,
        Body=json.dumps(story, indent=2),
        ContentType='application/json'
    )
    
    print(f"  ✅ Uploaded to: s3://{BUCKET_NAME}/{story_key}")
    
    return {
        "story_id": story_id,
        "title": story["title"],
        "s3_key": story_key,
        "category": category,
        "age_range": story["age_range"]
    }

def main():
    content_dir = Path("content/storyweaver")
    
    if not content_dir.exists():
        print("❌ No stories found. Run download-storyweaver.py first.")
        return
    
    story_files = list(content_dir.glob("*.json"))
    story_files = [f for f in story_files if f.name != "manifest.json"]
    
    print(f"📦 Found {len(story_files)} stories to upload\n")
    
    uploaded = []
    for story_file in story_files:
        try:
            result = upload_story(story_file)
            uploaded.append(result)
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Save upload manifest
    manifest = {
        "total_uploaded": len(uploaded),
        "bucket": BUCKET_NAME,
        "stories": uploaded
    }
    
    with open("content/upload-manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Uploaded {len(uploaded)} stories to S3")
    print(f"📁 Manifest saved to: content/upload-manifest.json")

if __name__ == "__main__":
    main()
