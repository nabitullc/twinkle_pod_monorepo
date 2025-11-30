#!/usr/bin/env python3
"""
Test single Book Dash story conversion
"""

import json
import uuid
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO
import PyPDF2

CLOUDFRONT_BASE = "https://d3qawc7yl9x4zs.cloudfront.net"
OUTPUT_DIR = Path(__file__).parent / "content" / "bookdash"

def extract_text_from_pdf(pdf_url):
    """Download and extract text from PDF"""
    try:
        response = requests.get(pdf_url, timeout=10)
        pdf_file = BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        
        story_pages = []
        
        # Skip first 4 pages (cover, credits, metadata)
        for i in range(4, len(reader.pages)):
            text = reader.pages[i].extract_text().strip()
            
            if not text or len(text) < 10:
                continue
            
            text = text.replace('\n', ' ').strip()
            story_pages.append(text)
        
        return story_pages
    except Exception as e:
        print(f"  ⚠️  PDF extraction failed: {e}")
        return []

def save_image_locally(img, story_id, page_num):
    """Save image to local directory"""
    try:
        img.thumbnail((1200, 800), Image.Resampling.LANCZOS)
        
        output_dir = OUTPUT_DIR / story_id / "images"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"page-{page_num}.jpg"
        img.convert('RGB').save(output_path, 'JPEG', quality=85, optimize=True)
        
        return f"images/{story_id}/page-{page_num}.jpg"
    except Exception as e:
        print(f"  ⚠️  Save failed: {e}")
        return None

def convert_book(slug, title):
    """Convert a Book Dash book to TwinklePod format"""
    print(f"📚 {title}")
    print(f"  🔗 Slug: {slug}")
    
    # Extract text from PDF
    pdf_url = f"{CLOUDFRONT_BASE}/{slug}/ebook/en_english/{slug}_en.pdf"
    print(f"  📄 Extracting text from PDF...")
    story_pages = extract_text_from_pdf(pdf_url)
    
    if not story_pages:
        print(f"  ❌ No text extracted")
        return None
    
    print(f"  📖 Extracted {len(story_pages)} text pages")
    
    story_id = str(uuid.uuid4())
    pages = []
    
    # Process each story page
    for page_num, text in enumerate(story_pages, 1):
        # Image numbering starts from page10 (PDF pages 5-14 map to images 10-19)
        image_page_num = page_num + 9
        image_url = f"{CLOUDFRONT_BASE}/{slug}/ebook/en_english/images/{slug}_en_page{image_page_num:02d}.jpg"
        
        print(f"    Page {page_num}: Download image...")
        
        # Download image
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                print(f"      ⚠️  Image not found (404)")
                break  # Stop if we hit missing images
            img = Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"      ⚠️  Download failed: {e}")
            break  # Stop on error
        
        # Save locally
        local_path = save_image_locally(img, story_id, page_num)
        if not local_path:
            continue
        
        pages.append({
            "text": text,
            "image": local_path
        })
    
    # Create story JSON
    story = {
        "story_id": story_id,
        "title": title,
        "pages": pages,
        "age_range": "3-8",
        "category": "general",
        "tags": ["bookdash"],
        "duration_minutes": len(pages),
        "page_count": len(pages),
        "author": "Book Dash",
        "license": "CC-BY 4.0",
        "source": f"https://bookdash.org/books/{slug}"
    }
    
    # Save JSON
    json_path = OUTPUT_DIR / f"{story_id}.json"
    with open(json_path, 'w') as f:
        json.dump(story, f, indent=2)
    
    print(f"  ✅ Saved: {json_path.name}")
    print(f"  📁 Location: {json_path}")
    return story

# Test with a-beautiful-day
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("🚀 Single Story Test\n")
story = convert_book("a-beautiful-day", "A Beautiful Day")

if story:
    print(f"\n✅ Success!")
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"\nStory structure:")
    print(f"  - {story['page_count']} pages")
    print(f"  - First page text: {story['pages'][0]['text'][:80]}...")
