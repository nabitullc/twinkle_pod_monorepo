#!/usr/bin/env python3
"""
Convert Book Dash downloads to TwinklePod format
Extracts text from images using OCR
"""

import json
import zipfile
from pathlib import Path
from PIL import Image
import pytesseract
import uuid

DOWNLOADS_DIR = Path.home() / "Downloads" / "bookdash-books"
OUTPUT_DIR = Path(__file__).parent / "content" / "bookdash"

def extract_zip(zip_path):
    """Extract ZIP to temp directory"""
    extract_dir = zip_path.parent / zip_path.stem
    if not extract_dir.exists():
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    return extract_dir

def ocr_image(image_path):
    """Extract text from image using OCR"""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        print(f"    ⚠️  OCR failed: {e}")
        return ""

def convert_story(zip_path):
    """Convert a Book Dash story to TwinklePod format"""
    story_name = zip_path.stem
    print(f"\n📚 {story_name}")
    
    # Extract ZIP
    extract_dir = extract_zip(zip_path)
    
    # Find English images
    images_dir = extract_dir / "ebook" / "en_english" / "images"
    if not images_dir.exists():
        print(f"  ❌ No images found at {images_dir}")
        return None
    
    # Get all images sorted
    image_files = sorted(images_dir.glob("*.jpg")) + sorted(images_dir.glob("*.png"))
    if not image_files:
        print(f"  ❌ No image files found")
        return None
    
    print(f"  📄 Found {len(image_files)} pages")
    
    # Create story structure
    story_id = str(uuid.uuid4())
    pages = []
    
    # Process each image
    for i, img_path in enumerate(image_files, 1):
        print(f"    Page {i}: OCR...")
        text = ocr_image(img_path)
        
        # Copy image to output
        output_img_dir = OUTPUT_DIR / story_id / "images"
        output_img_dir.mkdir(parents=True, exist_ok=True)
        output_img_path = output_img_dir / f"page-{i}.jpg"
        
        # Copy and optimize image
        img = Image.open(img_path)
        img.thumbnail((1200, 800), Image.Resampling.LANCZOS)
        img.save(output_img_path, "JPEG", quality=85, optimize=True)
        
        pages.append({
            "text": text,
            "image": f"images/{story_id}/page-{i}.jpg"
        })
    
    # Create story JSON
    story = {
        "story_id": story_id,
        "title": story_name.replace("-", " ").title(),
        "pages": pages,
        "age_range": "3-8",
        "category": "general",
        "tags": ["bookdash"],
        "duration_minutes": len(pages),
        "page_count": len(pages),
        "author": "Book Dash",
        "license": "CC-BY 4.0",
        "source": "https://bookdash.org"
    }
    
    # Save JSON
    json_path = OUTPUT_DIR / f"{story_id}.json"
    with open(json_path, 'w') as f:
        json.dump(story, f, indent=2)
    
    print(f"  ✅ Converted: {json_path.name}")
    return story

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Book Dash to TwinklePod Converter")
    print(f"📁 Input: {DOWNLOADS_DIR}")
    print(f"📁 Output: {OUTPUT_DIR}\n")
    
    # Find all ZIPs
    zip_files = list(DOWNLOADS_DIR.glob("*.zip"))
    print(f"Found {len(zip_files)} ZIP files\n")
    
    converted = 0
    for zip_path in zip_files:
        story = convert_story(zip_path)
        if story:
            converted += 1
    
    print(f"\n✅ Converted {converted}/{len(zip_files)} stories")
    print(f"📁 Output: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
