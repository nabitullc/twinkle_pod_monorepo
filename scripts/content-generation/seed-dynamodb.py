#!/usr/bin/env python3
"""
Seed DynamoDB stories table with metadata
"""

import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('twinklepod-stories-beta')

def seed_story(story_metadata):
    """Add story metadata to DynamoDB"""
    item = {
        'story_id': story_metadata['story_id'],
        'title': story_metadata['title'],
        's3_key': story_metadata['s3_key'],
        'category': story_metadata['category'],
        'age_range': story_metadata['age_range'],
        'published': True,
        'created_at': datetime.utcnow().isoformat()
    }
    
    table.put_item(Item=item)
    print(f"✅ Seeded: {story_metadata['title']}")

def main():
    with open('content/upload-manifest.json') as f:
        manifest = json.load(f)
    
    print(f"🌱 Seeding {len(manifest['stories'])} stories to DynamoDB\n")
    
    for story in manifest['stories']:
        try:
            seed_story(story)
        except Exception as e:
            print(f"❌ Error seeding {story['title']}: {e}")
    
    print(f"\n✅ Seeded {len(manifest['stories'])} stories")

if __name__ == "__main__":
    main()
