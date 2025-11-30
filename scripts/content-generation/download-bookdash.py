#!/usr/bin/env python3
"""
Download books from Book Dash
"""

import asyncio
import json
from playwright.async_api import async_playwright
from pathlib import Path

BOOKDASH_URL = "https://bookdash.org/book-source-files/"

async def get_book_links(page):
    """Get all book download links"""
    print("🔍 Loading Book Dash source files page...")
    await page.goto(BOOKDASH_URL, wait_until="load")
    await page.wait_for_timeout(3000)
    
    # Extract book links
    books = await page.evaluate("""
        () => {
            const bookLinks = [];
            const links = document.querySelectorAll('a[href*="?book="]');
            links.forEach(a => {
                const href = a.getAttribute('href');
                const title = a.textContent.trim();
                if (href && title) {
                    bookLinks.push({
                        title: title,
                        url: 'https://bookdash.org/book-source-files/' + href
                    });
                }
            });
            return bookLinks;
        }
    """)
    
    print(f"  Found {len(books)} books")
    return books

async def download_book(page, book, download_dir):
    """Download a single book's source files"""
    print(f"\n📚 {book['title']}")
    
    try:
        await page.goto(book['url'], wait_until="load")
        await page.wait_for_timeout(2000)
        
        # Click "Skip sharing details and proceed with download"
        skip_button = await page.query_selector('a:has-text("Skip sharing details")')
        if skip_button:
            print("  🖱️  Clicking skip...")
            
            # Wait for download
            async with page.expect_download(timeout=30000) as download_info:
                await skip_button.click()
            
            download = await download_info.value
            filename = download.suggested_filename
            filepath = download_dir / filename
            await download.save_as(filepath)
            
            print(f"  ✅ Downloaded: {filename}")
            return True
        else:
            print("  ❌ Skip button not found")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    return False

async def main():
    download_dir = Path.home() / "Downloads" / "bookdash-books"
    download_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Starting Book Dash Downloader")
    print(f"📁 Downloads will be saved to: {download_dir}\n")
    
    # How many books to download
    LIMIT = 100
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        
        # Get all book links
        books = await get_book_links(page)
        
        print(f"\n📚 Downloading {min(LIMIT, len(books))} books...\n")
        
        downloaded = 0
        for i, book in enumerate(books[:LIMIT], 1):
            print(f"[{i}/{min(LIMIT, len(books))}]")
            success = await download_book(page, book, download_dir)
            if success:
                downloaded += 1
            
            # Rate limiting
            await asyncio.sleep(2)
        
        await browser.close()
    
    print(f"\n✅ Downloaded {downloaded}/{min(LIMIT, len(books))} books")
    print(f"📁 Saved to: {download_dir}")

if __name__ == "__main__":
    asyncio.run(main())
