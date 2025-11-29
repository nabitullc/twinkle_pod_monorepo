# Auto-Download StoryWeaver Stories

This script automates downloading stories from StoryWeaver by mimicking your clicks.

## How It Works

1. Opens StoryWeaver listing pages (levels 1-3)
2. Extracts story links from the page
3. For each story:
   - Opens story page
   - Clicks "Download" button
   - Clicks "PDF" option
   - Saves file to Downloads folder

## Usage

```bash
python3 auto-download-storyweaver.py
```

## What You'll See

- Browser window opens (not headless)
- Script navigates through stories
- Downloads happen automatically
- Progress shown in terminal

## Configuration

Edit the script to customize:

```python
# Number of stories per level
links = await get_story_links(page, listing_url, limit=10)  # Change 10

# Story levels to download
STORY_URLS = [
    "https://storyweaver.org.in/en/stories?level=1&sort=Ratings",  # Age 3-5
    "https://storyweaver.org.in/en/stories?level=2&sort=Ratings",  # Age 5-7
    "https://storyweaver.org.in/en/stories?level=3&sort=Ratings",  # Age 7-9
]

# Rate limiting (seconds between downloads)
await asyncio.sleep(3)  # Change 3 to higher for slower
```

## Output

```
~/Downloads/storyweaver-stories/
├── 446500-leela-learns-to-ride.zip
├── 123456-another-story.zip
└── ...
```

## Next Steps

After downloading:

1. Run `extract-storyweaver-pdf.py` to process ZIPs
2. Manually add text to story JSONs
3. Run `upload-to-s3.py` to upload to S3

## Troubleshooting

**Downloads not starting:**
- Check if Download/PDF buttons have different text
- Inspect page and update selectors in script

**Cloudflare blocking:**
- Script uses real browser, should bypass
- Add longer delays if needed

**Too slow:**
- Reduce `limit=10` to fewer stories
- Increase `await asyncio.sleep(3)` for rate limiting
