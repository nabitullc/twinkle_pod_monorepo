#!/usr/bin/env python3
"""
Seed DynamoDB stories table with denormalized records for efficient querying.
Creates multiple records per story:
- Main record: PK = story_id
- Category records: PK = CATEGORY#{category}
- Age record: PK = AGE#{age_range}
- Published record: PK = PUBLISHED#{published}
"""

import json
import boto3
import sys
from datetime import datetime

def get_table_name():
    """Get the stories table name from CloudFormation outputs"""
    cf = boto3.client('cloudformation', region_name='us-east-1')
    try:
        response = cf.describe_stacks(StackName='TwinklePod-Database-beta')
        outputs = response['Stacks'][0]['Outputs']
        for output in outputs:
            if output['OutputKey'] == 'StoriesTableName':
                return output['OutputValue']
    except Exception as e:
        print(f"❌ Error getting table name: {e}")
        print("Using fallback table name pattern...")
        return None

def create_denormalized_records(story):
    """Create all denormalized records for a story"""
    records = []
    
    # Main record: PK = story_id
    main_record = {
        'pk': story['story_id'],
        'sk': story['story_id'],
        'story_id': story['story_id'],
        'title': story['title'],
        'age_range': story['age_range'],
        'categories': story['categories'],
        'tags': story['tags'],
        's3_key': story['s3_key'],
        'thumbnail_url': story['thumbnail_url'],
        'duration_minutes': story['duration_minutes'],
        'published': story['published'],
        'created_at': story['created_at']
    }
    records.append(main_record)
    
    # Category records: PK = CATEGORY#{category}
    for category in story['categories']:
        category_record = {
            'pk': f"CATEGORY#{category}",
            'sk': f"{story['created_at']}#{story['story_id']}",
            'story_id': story['story_id'],
            'title': story['title'],
            'age_range': story['age_range'],
            'categories': story['categories'],
            'tags': story['tags'],
            's3_key': story['s3_key'],
            'thumbnail_url': story['thumbnail_url'],
            'duration_minutes': story['duration_minutes'],
            'published': story['published'],
            'created_at': story['created_at']
        }
        records.append(category_record)
    
    # Age record: PK = AGE#{age_range}
    age_record = {
        'pk': f"AGE#{story['age_range']}",
        'sk': f"{story['created_at']}#{story['story_id']}",
        'story_id': story['story_id'],
        'title': story['title'],
        'age_range': story['age_range'],
        'categories': story['categories'],
        'tags': story['tags'],
        's3_key': story['s3_key'],
        'thumbnail_url': story['thumbnail_url'],
        'duration_minutes': story['duration_minutes'],
        'published': story['published'],
        'created_at': story['created_at']
    }
    records.append(age_record)
    
    # Published record: PK = PUBLISHED#{published}
    published_record = {
        'pk': f"PUBLISHED#{str(story['published']).lower()}",
        'sk': f"{story['created_at']}#{story['story_id']}",
        'story_id': story['story_id'],
        'title': story['title'],
        'age_range': story['age_range'],
        'categories': story['categories'],
        'tags': story['tags'],
        's3_key': story['s3_key'],
        'thumbnail_url': story['thumbnail_url'],
        'duration_minutes': story['duration_minutes'],
        'published': story['published'],
        'created_at': story['created_at']
    }
    records.append(published_record)
    
    return records

def batch_write_items(table, items, batch_size=25):
    """Write items in batches"""
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        with table.batch_writer() as writer:
            for item in batch:
                writer.put_item(Item=item)

def main():
    # Get table name
    table_name = get_table_name()
    if not table_name:
        print("❌ Could not determine table name. Is the Database stack deployed?")
        sys.exit(1)
    
    print(f"📊 Using table: {table_name}\n")
    
    # Load seed data
    with open('dynamodb-seed-stories.json') as f:
        stories = json.load(f)
    
    print(f"🌱 Seeding {len(stories)} stories to DynamoDB\n")
    
    # Create DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)
    
    # Generate all denormalized records
    all_records = []
    for story in stories:
        records = create_denormalized_records(story)
        all_records.extend(records)
    
    print(f"📝 Generated {len(all_records)} total records (denormalized)")
    print(f"   - {len(stories)} main records")
    print(f"   - ~{len(all_records) - len(stories)} denormalized records\n")
    
    # Batch write
    print("⏳ Writing to DynamoDB...")
    batch_write_items(table, all_records)
    
    print(f"\n✅ Successfully seeded {len(stories)} stories!")
    print(f"   Total records written: {len(all_records)}")

if __name__ == "__main__":
    main()
