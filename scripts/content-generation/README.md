# Content Generation Scripts

Scripts to download CC-BY licensed stories from StoryWeaver and upload to TwinklePod.

## Source

**StoryWeaver (Pratham Books)**
- URL: https://storyweaver.org.in
- License: CC-BY 4.0
- 20,000+ free stories

## Prerequisites

```bash
pip install requests boto3
```

## Usage

### 1. Download Stories from StoryWeaver

```bash
python3 download-storyweaver.py
```

This will:
- Search StoryWeaver API for stories by category/age
- Download 100 stories (matching our distribution)
- Convert to TwinklePod JSON format
- Save to `content/storyweaver/`

### 2. Upload to S3

```bash
# Set AWS credentials
export AWS_PROFILE=twinklepod

# Upload stories and images
python3 upload-to-s3.py
```

This will:
- Download images from StoryWeaver
- Upload to S3: `s3://twinklepod-stories-beta/`
- Organize by category/age
- Update CloudFront URLs
- Save manifest to `content/upload-manifest.json`

### 3. Seed DynamoDB

```bash
python3 seed-dynamodb.py
```

This will:
- Read upload manifest
- Add story metadata to DynamoDB
- Mark stories as published

## Output Structure

```
content/
├── storyweaver/
│   ├── bedtime_3+_123.json
│   ├── animals_5+_456.json
│   └── manifest.json
├── upload-manifest.json
└── temp/
    └── images/
```

## S3 Structure

```
s3://twinklepod-stories-beta/
├── stories/
│   ├── bedtime/
│   │   ├── age-3/
│   │   │   └── 123.json
│   │   ├── age-5/
│   │   └── age-7/
│   └── animals/
└── images/
    └── 123/
        ├── page-1.jpg
        └── page-2.jpg
```

## Attribution

All stories must include attribution:

```
Stories from StoryWeaver (Pratham Books)
License: CC-BY 4.0
https://storyweaver.org.in
```

Add to footer of story reader page.

## Distribution Target

- Bedtime: 20 stories
- Animals: 20 stories
- Moral: 15 stories
- Fantasy: 15 stories
- Short: 10 stories
- Funny: 10 stories
- Adventure: 10 stories

**Total: 100 stories**

Age ranges:
- 3+: 40 stories
- 5+: 40 stories
- 7+: 20 stories

## Notes

- StoryWeaver API may have rate limits
- Images are downloaded and re-uploaded to our S3
- Original source URLs are preserved in JSON
- License requires attribution (already included in JSON)
