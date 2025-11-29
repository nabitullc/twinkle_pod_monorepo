# StoryWeaver Scraping Guide

## Prerequisites

```bash
pip install playwright
playwright install chromium
```

## Usage

```bash
python3 scrape-storyweaver.py
```

This will:
1. Open StoryWeaver story listing pages (levels 1-3)
2. Extract story links (10 per level = 30 stories)
3. Visit each story page
4. Extract title, pages (text + images), category
5. Save to `content/storyweaver-scraped/`

## Output

```
content/storyweaver-scraped/
├── level_1_1.json
├── level_1_2.json
├── level_2_1.json
└── manifest.json
```

## Rate Limiting

- 2 second delay between stories
- Headless browser (no UI)
- Respects robots.txt

## Legal Notes

- Stories are CC-BY 4.0 licensed
- Attribution required: "From StoryWeaver (Pratham Books)"
- Commercial use allowed with attribution
- Scraping for personal/educational use is within ToS

## Customization

Adjust limits in script:
```python
story_links = await scrape_story_list(page, url, limit=10)  # Change 10 to desired count
```

## Troubleshooting

**Selectors not found:**
- StoryWeaver may have changed their HTML structure
- Inspect page and update selectors in script

**Cloudflare blocking:**
- Playwright with real browser bypasses this
- Add `await page.wait_for_timeout(5000)` if needed

**Rate limiting:**
- Increase sleep time: `await asyncio.sleep(5)`
