#!/usr/bin/env python3
"""
Automate downloading stories from StoryWeaver
Mimics user interaction: visit story -> click download -> click PDF
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import time

# Story URLs to download
STORY_URLS = [
    "https://storyweaver.org.in/en/stories?level=1&sort=Ratings",
    "https://storyweaver.org.in/en/stories?level=2&sort=Ratings",
    "https://storyweaver.org.in/en/stories?level=3&sort=Ratings",
]

async def download_story(page, story_url, download_dir):
    """Download a single story"""
    print(f"📖 Opening: {story_url}")
    
    try:
        await page.goto(story_url, wait_until="load", timeout=30000)
        await page.wait_for_timeout(2000)
        
        # Click Download button
        download_button = await page.query_selector('button:has-text("Download"), a:has-text("Download")')
        if download_button:
            print("  🖱️  Clicking Download...")
            await download_button.click()
            await page.wait_for_timeout(1000)
            
            # Click PDF option
            pdf_button = await page.query_selector('button:has-text("PDF"), a:has-text("PDF")')
            if pdf_button:
                print("  📄 Clicking PDF...")
                
                # Start waiting for download
                async with page.expect_download() as download_info:
                    await pdf_button.click()
                
                download = await download_info.value
                
                # Save to downloads folder
                filename = download.suggested_filename
                filepath = download_dir / filename
                await download.save_as(filepath)
                
                print(f"  ✅ Downloaded: {filename}")
                return True
            else:
                print("  ❌ PDF button not found")
        else:
            print("  ❌ Download button not found")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    return False

async def get_story_links(page, listing_url, limit=10):
    """Get story links from listing page"""
    print(f"\n🔍 Loading: {listing_url}")
    await page.goto(listing_url, wait_until="load", timeout=60000)
    await page.wait_for_timeout(5000)  # Wait for React to render
    
    # Scroll to load more stories
    for _ in range(3):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
    
    # Find all story links
    links = await page.evaluate("""
        () => {
            const storyLinks = [];
            const anchors = document.querySelectorAll('a[href*="/stories/"]');
            anchors.forEach(a => {
                const href = a.getAttribute('href');
                if (href && href.match(/\\/stories\\/\\d+/)) {
                    const fullUrl = href.startsWith('http') ? href : 'https://storyweaver.org.in' + href;
                    if (!storyLinks.includes(fullUrl)) {
                        storyLinks.push(fullUrl);
                    }
                }
            });
            return storyLinks;
        }
    """)
    
    print(f"  Found {len(links)} story links")
    return links[:limit]

async def main():
    download_dir = Path.home() / "Downloads" / "storyweaver-stories"
    download_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Starting StoryWeaver Auto-Downloader")
    print(f"📁 Downloads will be saved to: {download_dir}\n")
    
    async with async_playwright() as p:
        # Launch browser (visible so you can see progress)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            accept_downloads=True,
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        all_story_links = []
        
        # Get story links from each listing page
        for listing_url in STORY_URLS:
            links = await get_story_links(page, listing_url, limit=10)
            all_story_links.extend(links)
        
        print(f"\n📚 Total stories to download: {len(all_story_links)}\n")
        
        # Download each story
        downloaded = 0
        for i, story_url in enumerate(all_story_links, 1):
            print(f"\n[{i}/{len(all_story_links)}]")
            success = await download_story(page, story_url, download_dir)
            if success:
                downloaded += 1
            
            # Rate limiting
            await asyncio.sleep(3)
        
        await browser.close()
    
    print(f"\n✅ Downloaded {downloaded}/{len(all_story_links)} stories")
    print(f"📁 Saved to: {download_dir}")

if __name__ == "__main__":
    asyncio.run(main())
