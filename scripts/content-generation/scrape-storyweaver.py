#!/usr/bin/env python3
"""
Scrape stories from StoryWeaver using Playwright (bypasses Cloudflare)
"""

import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

STORY_URLS = {
    "level_1": "https://storyweaver.org.in/en/stories?level=1&sort=Ratings",  # Age 3-5
    "level_2": "https://storyweaver.org.in/en/stories?level=2&sort=Ratings",  # Age 5-7
    "level_3": "https://storyweaver.org.in/en/stories?level=3&sort=Ratings",  # Age 7-9
}

async def scrape_story_list(page, url, limit=20):
    """Scrape story links from listing page"""
    print(f"📖 Loading: {url}")
    await page.goto(url, wait_until="networkidle")
    
    # Wait for stories to load
    await page.wait_for_selector('[data-testid="story-card"]', timeout=10000)
    
    # Extract story links
    story_cards = await page.query_selector_all('[data-testid="story-card"]')
    
    stories = []
    for card in story_cards[:limit]:
        link = await card.query_selector('a')
        if link:
            href = await link.get_attribute('href')
            title = await link.text_content()
            stories.append({
                "url": f"https://storyweaver.org.in{href}",
                "title": title.strip()
            })
    
    print(f"  Found {len(stories)} stories")
    return stories

async def scrape_story_content(page, story_url):
    """Scrape individual story content"""
    print(f"  📄 Scraping: {story_url}")
    await page.goto(story_url, wait_until="networkidle")
    
    # Extract title
    title_elem = await page.query_selector('h1')
    title = await title_elem.text_content() if title_elem else "Untitled"
    
    # Extract pages
    pages = []
    page_elements = await page.query_selector_all('.story-page')
    
    for page_elem in page_elements:
        # Extract text
        text_elem = await page_elem.query_selector('.page-text')
        text = await text_elem.text_content() if text_elem else ""
        
        # Extract image
        img_elem = await page_elem.query_selector('img')
        image_url = await img_elem.get_attribute('src') if img_elem else ""
        
        if text or image_url:
            pages.append({
                "text": text.strip(),
                "image": image_url
            })
    
    # Extract metadata
    category_elem = await page.query_selector('[data-testid="category"]')
    category = await category_elem.text_content() if category_elem else "general"
    
    return {
        "title": title.strip(),
        "pages": pages,
        "category": category.strip().lower(),
        "source_url": story_url
    }

async def main():
    output_dir = Path("content/storyweaver-scraped")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        all_stories = []
        
        for level, url in STORY_URLS.items():
            print(f"\n🔍 Scraping {level}...")
            
            # Get story list
            story_links = await scrape_story_list(page, url, limit=10)
            
            # Scrape each story
            for story_link in story_links:
                try:
                    story_data = await scrape_story_content(page, story_link["url"])
                    story_data["level"] = level
                    all_stories.append(story_data)
                    
                    # Save individual story
                    filename = f"{level}_{len(all_stories)}.json"
                    with open(output_dir / filename, "w") as f:
                        json.dump(story_data, f, indent=2)
                    
                    print(f"    ✅ Saved: {story_data['title']}")
                    
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                
                # Rate limiting
                await asyncio.sleep(2)
        
        await browser.close()
    
    # Save manifest
    manifest = {
        "total_stories": len(all_stories),
        "source": "StoryWeaver (Pratham Books)",
        "license": "CC-BY 4.0",
        "stories": all_stories
    }
    
    with open(output_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Scraped {len(all_stories)} stories")
    print(f"📁 Saved to: {output_dir}")

if __name__ == "__main__":
    asyncio.run(main())
