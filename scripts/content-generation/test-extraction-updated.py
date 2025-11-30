#!/usr/bin/env python3
import requests
from io import BytesIO
import PyPDF2

CLOUDFRONT_BASE = "https://d3qawc7yl9x4zs.cloudfront.net"

def extract_text_from_pdf(pdf_url):
    response = requests.get(pdf_url, timeout=10)
    pdf_file = BytesIO(response.content)
    reader = PyPDF2.PdfReader(pdf_file)
    
    story_pages = []
    
    # Skip first 4 pages (cover, credits, metadata)
    for i in range(4, len(reader.pages)):
        text = reader.pages[i].extract_text().strip()
        
        if not text or len(text) < 10:
            continue
        
        text = text.replace('\n', ' ').strip()
        story_pages.append(text)
    
    return story_pages

slug = "a-beautiful-day"
pdf_url = f"{CLOUDFRONT_BASE}/{slug}/ebook/en_english/{slug}_en.pdf"

print("🧪 Testing Updated PDF Extraction\n")
pages = extract_text_from_pdf(pdf_url)

print(f"✅ Extracted {len(pages)} story pages:\n")
for i, text in enumerate(pages, 1):
    print(f"Page {i}: {text[:80]}...")
    print()
