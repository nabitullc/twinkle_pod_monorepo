#!/usr/bin/env python3
"""Inspect StoryWeaver page structure"""

import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Show browser
        page = await browser.new_page()
        
        print("🔍 Loading StoryWeaver...")
        await page.goto("https://storyweaver.org.in/en/stories?level=1&sort=Ratings", wait_until="load")
        
        print("⏳ Waiting 10 seconds for page to load...")
        await page.wait_for_timeout(10000)
        
        # Take screenshot
        await page.screenshot(path="storyweaver-page.png")
        print("📸 Screenshot saved: storyweaver-page.png")
        
        # Get page HTML
        html = await page.content()
        with open("storyweaver-page.html", "w") as f:
            f.write(html)
        print("📄 HTML saved: storyweaver-page.html")
        
        print("\n✅ Inspect the files to see page structure")
        print("   Then update selectors in scrape-storyweaver.py")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
