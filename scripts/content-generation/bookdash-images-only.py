#!/usr/bin/env python3
"""
Book Dash Scraper - Images Only (Storyberries Style)

What it does:
1. Scrapes book list from bookdash.org
2. For each book, downloads all page images from CloudFront
3. Creates TwinklePod JSON with empty text (text is in images)
4. Saves images locally (ready for S3 upload)

No PDF extraction needed - images already have text overlaid.
"""

import asyncio
import json
import uuid
from pathlib import Path
from playwright.async_api import async_playwright
import requests
from PIL import Image
from io import BytesIO

BOOKDASH_URL = "https://bookdash.org/book-source-files/"
CLOUDFRONT_BASE = "https://d3qawc7yl9x4zs.cloudfront.net"
OUTPUT_DIR = Path(__file__).parent / "content" / "bookdash"

def save_image_locally(img, story_id, page_num):
    """Optimize and save image locally"""
    try:
        # Resize to max 1200x800 while maintaining aspect ratio
        img.thumbnail((1200, 800), Image.Resampling.LANCZOS)
        
        output_dir = OUTPUT_DIR / story_id / "images"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"page-{page_num}.jpg"
        img.convert('RGB').save(output_path, 'JPEG', quality=85, optimize=True)
        
        return f"images/{story_id}/page-{page_num}.jpg"
    except Exception as e:
        print(f"      ⚠️  Save failed: {e}")
        return None

async def get_books(page):
    """Scrape book list from Book Dash website"""
    print("🔍 Scraping Book Dash website...")
    print("  📡 Opening browser...")
    await page.goto(BOOKDASH_URL, wait_until="load")
    print("  ⏳ Waiting for page to load...")
    await page.wait_for_timeout(2000)
    
    print("  🔎 Extracting book links...")
    books = await page.evaluate("""
        () => {
            const bookLinks = [];
            const links = document.querySelectorAll('a[href*="?book="]');
            links.forEach(a => {
                const href = a.getAttribute('href');
                const title = a.textContent.trim();
                if (href && title) {
                    const match = href.match(/\?book=([^&]+)/);
                    if (match) {
                        bookLinks.push({
                            title: title,
                            slug: match[1]
                        });
                    }
                }
            });
            return bookLinks;
        }
    """)
    
    print(f"  ✅ Found {len(books)} books\n")
    return books

def find_all_images(slug):
    """Find all available images by scraping Book Dash page"""
    images = []
    
    print(f"  🔍 Scraping Book Dash page...", end="", flush=True)
    
    # Try different folder paths
    folder_paths = [
        '/ebook/en_english/images',
        '/ebook/en-english/images',
        '/e-book/en_english/images',
        '/e-book/en-english/images',
        '/e_book/en_english/images',
        '/e_book/en-english/images'
    ]
    
    for folder_path in folder_paths:
        try:
            url = f"https://bookdash.org/book-source-files/?book={slug}&folder={folder_path}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                continue
            
            # Extract image filenames from HTML
            import re
            pattern = r'href="\?view-file=' + re.escape(slug) + r'([^"]+\.jpg)"'
            matches = re.findall(pattern, response.text)
            
            if matches:
                # Found images in this folder
                for match in matches:
                    full_path = slug + match
                    image_url = f"{CLOUDFRONT_BASE}/{full_path}"
                    
                    # Determine if it's cover or page
                    if 'cover' in match.lower():
                        images.append(('cover', image_url))
                    else:
                        images.append((match, image_url))
                    
                    print(".", end="", flush=True)
                
                break  # Found images, stop trying other folders
        except Exception as e:
            continue
    
    print()  # New line
    return images

def is_already_downloaded(title):
    """Check if story already exists by title"""
    for json_file in OUTPUT_DIR.glob("*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)
                if data.get('title') == title:
                    return True
        except:
            pass
    return False

def convert_book(book):
    """Convert a Book Dash book to TwinklePod format"""
    slug = book['slug']
    title = book['title']
    
    # Skip if already downloaded
    if is_already_downloaded(title):
        print(f"📚 {title}")
        print(f"  ⏭️  Already downloaded, skipping\n")
        return None
    
    print(f"📚 {title}")
    print(f"  🔗 Slug: {slug}")
    
    # Find all images on CloudFront
    image_list = find_all_images(slug)
    
    if not image_list:
        print(f"  ❌ No images found")
        return None
    
    print(f"  📸 Found {len(image_list)} images")
    
    story_id = str(uuid.uuid4())
    pages = []
    
    # Download each image
    print(f"  📥 Downloading {len(image_list)} images...", end="", flush=True)
    for page_num, (img_name, image_url) in enumerate(image_list, 1):
        
        try:
            response = requests.get(image_url, timeout=30)
            img = Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"\n      ⚠️  {img_name} failed: {e}")
            continue
        
        # Save locally
        local_path = save_image_locally(img, story_id, page_num)
        if not local_path:
            continue
        
        print(".", end="", flush=True)
        
        # Empty text - text is in the image
        pages.append({
            "index": page_num - 1,  # 0-indexed
            "text": "",
            "image": local_path
        })
    
    print()  # New line after dots
    
    if not pages:
        print(f"  ❌ No pages saved")
        return None
    
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
        "source": f"https://bookdash.org/books/{slug}",
        "note": "Text is overlaid on images (Storyberries style)"
    }
    
    # Save JSON
    json_path = OUTPUT_DIR / f"{story_id}.json"
    with open(json_path, 'w') as f:
        json.dump(story, f, indent=2)
    
    print(f"  ✅ Saved: {json_path.name}\n")
    return story

async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Book Dash Image Scraper (Storyberries Style)")
    print(f"📁 Output: {OUTPUT_DIR}\n")
    
    # Get book list
    print("=" * 60)
    print("STEP 1: Scraping Book List")
    print("=" * 60)
    
    async with async_playwright() as p:
        print("🌐 Launching browser...")
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage']
        )
        page = await browser.new_page()
        books = await get_books(page)
        print("🔒 Closing browser...")
        await browser.close()
    
    # Convert books
    LIMIT = len(books)  # Download ALL books
    converted = 0
    
    print("\n" + "=" * 60)
    print(f"STEP 2: Downloading {LIMIT} Stories")
    print("=" * 60 + "\n")
    
    for i, book in enumerate(books[:LIMIT], 1):
        print(f"[{i}/{LIMIT}] ", end="")
        story = convert_book(book)
        if story:
            converted += 1
        print()  # Extra line between stories
    
    print("=" * 60)
    print(f"✅ COMPLETE: {converted}/{LIMIT} stories converted")
    print("=" * 60)
    print(f"📁 Output: {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
