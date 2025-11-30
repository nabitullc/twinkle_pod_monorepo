#!/usr/bin/env python3
"""
Generate DynamoDB seed with denormalized records for efficient querying

Creates multiple records per story:
1. Main record: PK = story_id
2. Category records: PK = "CATEGORY#{category}"
3. Age record: PK = "AGE#{age_range}"
4. Published record: PK = "PUBLISHED#true"
"""

import json
from pathlib import Path

BOOKDASH_DIR = Path(__file__).parent / "content" / "bookdash"
OUTPUT_FILE = Path(__file__).parent / "dynamodb-seed-stories.json"

def create_story_records(story):
    """Create denormalized records for a story"""
    records = []
    
    # Extract minimal DynamoDB fields
    base_item = {
        "story_id": story["story_id"],
        "title": story["title"],
        "age_range": story["age_range"],
        "categories": story["categories"],
        "tags": story["tags"],
        "s3_key": story["s3_key"],
        "thumbnail_url": story["thumbnail_url"],
        "duration_minutes": story["duration_minutes"],
        "published": story["published"],
        "created_at": story["created_at"]
    }
    
    # 1. Main record (PK = story_id)
    main_record = {
        "pk": story["story_id"],
        "sk": "METADATA",
        **base_item
    }
    records.append(main_record)
    
    # 2. Category records (one per category)
    for category in story["categories"]:
        category_record = {
            "pk": f"CATEGORY#{category}",
            "sk": f"{story['created_at']}#{story['story_id']}",
            **base_item
        }
        records.append(category_record)
    
    # 3. Age range record
    age_record = {
        "pk": f"AGE#{story['age_range']}",
        "sk": f"{story['created_at']}#{story['story_id']}",
        **base_item
    }
    records.append(age_record)
    
    # 4. Published record
    if story["published"]:
        published_record = {
            "pk": "PUBLISHED#true",
            "sk": f"{story['created_at']}#{story['story_id']}",
            **base_item
        }
        records.append(published_record)
    
    return records

def main():
    print("🔍 Generating DynamoDB seed with denormalized records...")
    
    all_records = []
    story_count = 0
    
    for json_file in sorted(BOOKDASH_DIR.glob("*.json")):
        try:
            with open(json_file) as f:
                story = json.load(f)
            
            records = create_story_records(story)
            all_records.extend(records)
            story_count += 1
            
            print(f"  ✅ {story['title']} → {len(records)} records")
            
        except Exception as e:
            print(f"  ❌ {json_file.name}: {e}")
    
    # Save seed file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_records, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ Processed {story_count} stories")
    print(f"📊 Generated {len(all_records)} DynamoDB records")
    print(f"📄 Seed file: {OUTPUT_FILE}")
    print(f"{'='*60}")
    
    # Print statistics
    category_counts = {}
    age_counts = {}
    
    for record in all_records:
        if record["pk"].startswith("CATEGORY#"):
            category = record["pk"].replace("CATEGORY#", "")
            category_counts[category] = category_counts.get(category, 0) + 1
        elif record["pk"].startswith("AGE#"):
            age = record["pk"].replace("AGE#", "")
            age_counts[age] = age_counts.get(age, 0) + 1
    
    print("\n📊 Category Distribution:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count} stories")
    
    print("\n📊 Age Range Distribution:")
    for age, count in sorted(age_counts.items()):
        print(f"   {age}: {count} stories")

if __name__ == "__main__":
    main()
