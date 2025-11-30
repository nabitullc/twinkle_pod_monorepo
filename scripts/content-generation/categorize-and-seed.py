#!/usr/bin/env python3
"""
Categorize BookDash stories and generate DynamoDB seed data

What it does:
1. Reads all story JSONs from bookdash folder
2. Downloads PDF from BookDash and extracts text for categorization
3. Auto-categorizes based on title + PDF content
4. Sets age_range to "3-6" for all
5. Generates DynamoDB seed JSON for stories table
6. Updates story JSONs with CloudFront URLs
"""

import json
from pathlib import Path
import requests
import re
try:
    import PyPDF2
    from io import BytesIO
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️  PyPDF2 not installed. Install with: pip install PyPDF2")

BOOKDASH_DIR = Path(__file__).parent / "content" / "bookdash"
OUTPUT_FILE = Path(__file__).parent / "dynamodb-seed-stories.json"
CLOUDFRONT_BASE = "https://cdn.twinklepod.com"

# Category keywords for auto-categorization
CATEGORY_KEYWORDS = {
    "animals": ["fish", "hippo", "monkey", "elephant", "lion", "bird", "cat", "dog", "rabbit", "bear", 
                "penguin", "tortoise", "ant", "bee", "meerkat", "owl", "goat", "pig", "ladybird"],
    "bedtime": ["dream", "sleep", "night", "moon", "star", "pillow", "lullaby", "tired", "sleepy"],
    "family": ["mama", "papa", "tata", "grandpa", "grandma", "baby", "brother", "sister", "auntie", 
               "mother", "father", "parent", "granny", "gogo", "ouma"],
    "adventure": ["journey", "explore", "discover", "quest", "travel", "top", "climb", "mountain", "road"],
    "friendship": ["friend", "together", "share", "help", "kind", "play"],
    "emotions": ["happy", "sad", "angry", "grumpy", "love", "hug", "smile", "scared", "brave", "laugh"],
    "learning": ["count", "color", "shape", "number", "letter", "learn", "teach", "school"],
    "fantasy": ["magic", "wizard", "fairy", "dragon", "giant", "castle", "monster", "alien"],
    "food": ["eat", "lunch", "breakfast", "dinner", "cook", "recipe", "cake", "egg", "pancake"],
}

def extract_slug_from_source(source_url):
    """Extract book slug from source URL"""
    match = re.search(r'/books/([^/]+)', source_url)
    return match.group(1) if match else None

def calculate_age_range(pdf_text):
    """Calculate age range based on text complexity"""
    if not pdf_text:
        return "3-6"  # Default
    
    # Split into words
    words = pdf_text.split()
    if len(words) < 10:
        return "3-6"
    
    # Calculate metrics
    total_words = len(words)
    avg_word_length = sum(len(word) for word in words) / total_words
    
    # Count sentences (approximate)
    sentences = pdf_text.count('.') + pdf_text.count('!') + pdf_text.count('?')
    if sentences == 0:
        sentences = 1
    
    words_per_sentence = total_words / sentences
    
    # Count complex words (>6 letters)
    complex_words = sum(1 for word in words if len(word) > 6)
    complex_ratio = complex_words / total_words
    
    # Age range logic:
    # 3-5: Short words (avg <4), short sentences (<5 words), few complex words (<10%)
    # 4-6: Medium words (avg 4-5), medium sentences (5-8 words), some complex words (10-20%)
    # 5-7: Longer words (avg >5), longer sentences (>8 words), more complex words (>20%)
    
    if avg_word_length < 4 and words_per_sentence < 5 and complex_ratio < 0.1:
        return "3-5"
    elif avg_word_length > 5 and words_per_sentence > 8 and complex_ratio > 0.2:
        return "5-7"
    else:
        return "4-6"

def download_pdf_text(slug):
    """Download and extract text from BookDash PDF by scraping actual filename"""
    if not PDF_AVAILABLE:
        return ""
    
    # Try different folder patterns to find PDF
    folder_patterns = ['/ebook/en-english', '/ebook/en_english', '/e-book/en-english', '/e-book/en_english']
    
    for folder in folder_patterns:
        try:
            # Scrape the BookDash page to find actual PDF filename
            page_url = f"https://bookdash.org/book-source-files/?book={slug}&folder={folder}"
            response = requests.get(page_url, timeout=10)
            
            if response.status_code == 200:
                # Look for PDF filename in the HTML
                pdf_match = re.search(rf'{slug}[^"<>]*\.pdf', response.text)
                if pdf_match:
                    pdf_path = pdf_match.group(0)
                    pdf_url = f"https://d3qawc7yl9x4zs.cloudfront.net/{pdf_path}"
                    
                    # Download and extract text
                    pdf_response = requests.get(pdf_url, timeout=10)
                    if pdf_response.status_code == 200:
                        pdf_file = BytesIO(pdf_response.content)
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        
                        text = ""
                        # Read first 5 pages
                        for page_num in range(min(5, len(pdf_reader.pages))):
                            text += pdf_reader.pages[page_num].extract_text()
                        
                        return text.lower()
        except:
            continue
    
    return ""

def categorize_story(title, pages, pdf_text=""):
    """Auto-categorize based on title, pages, and PDF text"""
    # Combine title + first 5 pages text + PDF text
    text = title.lower()
    for page in pages[:5]:
        text += " " + page.get("text", "").lower()
    text += " " + pdf_text
    
    categories = []
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            categories.append(category)
    
    # Default to "general" if no match
    if not categories:
        categories.append("general")
    
    return categories

def process_stories():
    """Process all stories and generate seed data"""
    stories = []
    
    print("🔍 Processing BookDash stories...")
    
    for json_file in sorted(BOOKDASH_DIR.glob("*.json")):
        try:
            with open(json_file) as f:
                story = json.load(f)
            
            story_id = story["story_id"]
            title = story["title"]
            pages = story.get("pages", [])
            source = story.get("source", "")
            
            # Extract slug and download PDF text
            slug = extract_slug_from_source(source)
            pdf_text = ""
            if slug:
                print(f"  📄 Downloading PDF...", end="", flush=True)
                pdf_text = download_pdf_text(slug)
                if pdf_text:
                    print(" ✓", end="")
                else:
                    print(" ✗", end="")
            
            # Auto-categorize using title + pages + PDF text
            categories = categorize_story(title, pages, pdf_text)
            
            # Calculate age range based on text complexity
            age_range = calculate_age_range(pdf_text)
            
            # Update story JSON with categories and age range
            story["categories"] = categories
            story["age_range"] = age_range
            
            # Update story JSON with CloudFront URLs
            for page in story.get("pages", []):
                if "image" in page:
                    # Convert relative path to CloudFront URL
                    page["image"] = f"{CLOUDFRONT_BASE}/{page['image']}"
            
            # Save updated story JSON
            with open(json_file, 'w') as f:
                json.dump(story, f, indent=2)
            
            # Create DynamoDB item
            dynamodb_item = {
                "story_id": story_id,
                "title": title,
                "age_range": age_range,
                "categories": categories,
                "tags": story.get("tags", []),
                "s3_key": f"stories/{story_id}.json",
                "thumbnail_url": f"{CLOUDFRONT_BASE}/images/{story_id}/page-1.jpg",
                "duration_minutes": story.get("duration_minutes", story.get("page_count", 5)),
                "page_count": story.get("page_count", len(story.get("pages", []))),
                "author": story.get("author", "Book Dash"),
                "license": story.get("license", "CC-BY 4.0"),
                "source": story.get("source", ""),
                "published": True,
                "created_at": story.get("created_at", "2025-01-01T00:00:00Z")
            }
            
            stories.append(dynamodb_item)
            
            print(f"  ✅ {title}")
            print(f"     Age: {age_range} | Categories: {', '.join(categories)}")
            
        except Exception as e:
            print(f"  ❌ {json_file.name}: {e}")
    
    # Save DynamoDB seed data
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(stories, f, indent=2)
    
    print(f"\n✅ Processed {len(stories)} stories")
    print(f"📄 DynamoDB seed: {OUTPUT_FILE}")
    
    # Print category distribution
    print("\n📊 Category Distribution:")
    category_counts = {}
    for story in stories:
        for cat in story["categories"]:
            category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")

if __name__ == "__main__":
    process_stories()
