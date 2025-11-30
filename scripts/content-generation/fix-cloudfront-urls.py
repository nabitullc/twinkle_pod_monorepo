#!/usr/bin/env python3
"""Fix duplicate CloudFront URLs in story JSONs"""

import json
import re
from pathlib import Path

BOOKDASH_DIR = Path(__file__).parent / "content" / "bookdash"
CLOUDFRONT_BASE = "https://d3lncscy0tzgzt.cloudfront.net"

def fix_url(url):
    """Remove duplicate CloudFront prefixes"""
    # Extract the path after all the duplicate prefixes
    match = re.search(r'(images/[^/]+/page-\d+\.jpg)$', url)
    if match:
        return f"{CLOUDFRONT_BASE}/{match.group(1)}"
    return url

def fix_story_json(json_file):
    """Fix URLs in a story JSON"""
    with open(json_file) as f:
        story = json.load(f)
    
    # Fix page image URLs
    for page in story.get('pages', []):
        if 'image' in page:
            page['image'] = fix_url(page['image'])
    
    # Fix thumbnail URL
    if 'thumbnail_url' in story:
        story['thumbnail_url'] = fix_url(story['thumbnail_url'])
    
    # Write back
    with open(json_file, 'w') as f:
        json.dump(story, f, indent=2, ensure_ascii=False)
    
    return story['title']

def main():
    json_files = list(BOOKDASH_DIR.glob("*.json"))
    print(f"🔧 Fixing CloudFront URLs in {len(json_files)} stories\n")
    
    for json_file in json_files:
        title = fix_story_json(json_file)
        print(f"✅ {title}")
    
    print(f"\n✅ Fixed {len(json_files)} stories")

if __name__ == "__main__":
    main()
