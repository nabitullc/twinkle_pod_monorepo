#!/usr/bin/env python3
"""
Scrape Book Dash stories directly from CloudFront
Extract text from PDF, download images, upload to S3
"""

import asyncio
import json
import uuid
from pathlib import Path
from playwright.async_api import async_playwright
import requests
from PIL import Image
from io import BytesIO
import boto3
import PyPDF2
import re

BOOKDASH_URL = "https://bookdash.org/book-source-files/"
CLOUDFRONT_BASE = "https://d3qawc7yl9x4zs.cloudfront.net"
OUTPUT_DIR = Path(__file__).parent / "content" / "bookdash"

# S3 Configuration
S3_BUCKET = "twinklepod-stories-beta"
S3_PREFIX = "images"
CLOUDFRONT_URL = "https://d1234567890.cloudfront.net"  # Replace with your CloudFront URL

s3_client = boto3.client('s3')

def extract_text_from_pdf(pdf_url):
    """Download and extract text from PDF"""
    try:
        response = requests.get(pdf_url, timeout=10)
        pdf_file = BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        
        story_pages = []
        
        # Skip first 4 pages (cover, credits, metadata)
        # Start from page 5 (index 4)
        for i in range(4, len(reader.pages)):
            text = reader.pages[i].extract_text().strip()
            
            # Skip empty pages
            if not text:
                continue
            
            # Clean up text
            text = text.replace('\n', ' ').strip()
            
            # Skip if it's just metadata/credits
            if len(text) < 10:
                continue
            
            story_pages.append(text)
        
        return story_pages
    except Exception as e:
        print(f"      ⚠️  PDF extraction failed: {e}")
        return []

def upload_to_s3(img, story_id, page_num):
    """Optimize and upload image to S3"""
    try:
        # Optimize image
        img.thumbnail((1200, 800), Image.Resampling.LANCZOS)
        
        # Convert to bytes
        buffer = BytesIO()
        img.convert('RGB').save(buffer, 'JPEG', quality=85, optimize=True)
        buffer.seek(0)
        
        # Upload to S3
        s3_key = f"{S3_PREFIX}/{story_id}/page-{page_num}.jpg"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=buffer,
            ContentType='image/jpeg'
        )
        
        return f"{CLOUDFRONT_URL}/{s3_key}"
    except Exception as e:
        print(f"      ⚠️  S3 upload failed: {e}")
        return None

async def get_books(page):
    """Get all book slugs from Book Dash"""
    print("🔍 Loading Book Dash source files page...")
    await page.goto(BOOKDASH_URL, wait_until="load")
    await page.wait_for_timeout(2000)
    
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
    
    print(f"  Found {len(books)} books\n")
    return books

def find_page_count(slug):
    """Find how many pages a book has by probing CloudFront"""
    for page_num in range(1, 50):  # Max 50 pages
        url = f"{CLOUDFRONT_BASE}/{slug}/ebook/en_english/images/{slug}_en_page{page_num:02d}.jpg"
        try:
            response = requests.head(url, timeout=5)
            if response.status_code != 200:
                return page_num - 1
        except:
            return page_num - 1
    return 50

def convert_book(book):
    """Convert a Book Dash book to TwinklePod format"""
    slug = book['slug']
    title = book['title']
    
    print(f"📚 {title}")
    print(f"  🔗 Slug: {slug}")
    
    # Extract text from PDF
    pdf_url = f"{CLOUDFRONT_BASE}/{slug}/ebook/en_english/{slug}_en.pdf"
    print(f"  📄 Extracting text from PDF...")
    story_pages = extract_text_from_pdf(pdf_url)
    
    if not story_pages:
        print(f"  ❌ No text extracted")
        return None
    
    print(f"  📖 Extracted {len(story_pages)} story pages")
    
    story_id = str(uuid.uuid4())
    pages = []
    
    # Process each story page
    for page_num, text in enumerate(story_pages, 1):
        # Image numbering starts from page05 (after metadata pages)
        image_page_num = page_num + 4
        image_url = f"{CLOUDFRONT_BASE}/{slug}/ebook/en_english/images/{slug}_en_page{image_page_num:02d}.jpg"
        
        print(f"    Page {page_num}: Download image...")
        
        # Download image
        try:
            response = requests.get(image_url, timeout=10)
            img = Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"      ⚠️  Download failed: {e}")
            continue
        
        # Upload to our S3
        s3_url = upload_to_s3(img, story_id, page_num)
        if not s3_url:
            continue
        
        pages.append({
            "text": text,
            "image": s3_url
        })
    
    # Create story JSON
    story = {
        "story_id": story_id,
        "title": title,
        "pages": pages,
        "age_range": "3-8",
        "category": "general",
        "tags": ["bookdash"],
        "duration_minutes": page_count,
        "page_count": page_count,
        "author": "Book Dash",
        "license": "CC-BY 4.0",
        "source": f"https://bookdash.org/books/{slug}"
    }
    
    # Save JSON
    json_path = OUTPUT_DIR / f"{story_id}.json"
    with open(json_path, 'w') as f:
        json.dump(story, f, indent=2)
    
    print(f"  ✅ Saved: {json_path.name}\n")
    return story

async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Book Dash CloudFront Scraper")
    print(f"📁 Output: {OUTPUT_DIR}\n")
    
    # Get book list
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        books = await get_books(page)
        await browser.close()
    
    # Convert each book
    LIMIT = 100
    converted = 0
    
    for i, book in enumerate(books[:LIMIT], 1):
        print(f"[{i}/{min(LIMIT, len(books))}]")
        story = convert_book(book)
        if story:
            converted += 1
    
    print(f"\n✅ Converted {converted}/{min(LIMIT, len(books))} stories")
    print(f"📁 Output: {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
