# Content Sourcing Options for MVP

## Current Status

StoryWeaver API access needs investigation. Here are alternative approaches:

## Option 1: Manual Download from StoryWeaver

**Steps:**
1. Visit https://storyweaver.org.in/stories
2. Filter by:
   - Reading Level: 1, 2, 3 (ages 3-5, 5-7, 7-9)
   - Categories: Animals, Bedtime, etc.
   - License: CC-BY
3. Download stories manually (PDF format)
4. Extract text and images
5. Convert to JSON format

**Pros:** Legal, high-quality, free
**Cons:** Manual work

## Option 2: Book Dash

**URL:** https://bookdash.org/books/
**License:** CC-BY 4.0
**Count:** 100+ stories

**Steps:**
1. Download books from website
2. Extract content
3. Convert to JSON

## Option 3: African Storybook

**URL:** https://www.africanstorybook.org
**License:** CC-BY
**Count:** 1000+ stories
**API:** Available

## Option 4: Generate Original Content

**For MVP Testing:**
- Use `generate-sample-stories.py` for 2-5 test stories
- Test infrastructure and UI
- Replace with real content before launch

**For Production:**
- Hire writers to create original stories
- Commission illustrations
- Full ownership, no attribution needed

## Recommendation for MVP

**Short-term (Testing):**
- Use sample stories from `generate-sample-stories.py`
- Test all features with 2-5 stories
- Validate infrastructure

**Before Launch:**
- Manually download 100 stories from StoryWeaver
- Or use Book Dash content
- Or create original content

## Legal Requirements

All CC-BY content requires:
- Attribution to original source
- Link to license
- Indication if changes were made

**Example footer:**
```
Stories from StoryWeaver (Pratham Books)
Licensed under CC-BY 4.0
https://storyweaver.org.in
```

## Next Steps

1. Use sample stories for MVP development
2. Build and test all features
3. Before beta launch, source 100 real stories
4. Add proper attribution
