#!/usr/bin/env python3
"""
Test PDF text extraction from Book Dash
"""

import requests
from io import BytesIO
import PyPDF2

CLOUDFRONT_BASE = "https://d3qawc7yl9x4zs.cloudfront.net"

def extract_text_from_pdf(pdf_url):
    """Download and extract text from PDF"""
    print(f"📄 Downloading: {pdf_url}")
    
    try:
        response = requests.get(pdf_url, timeout=10)
        print(f"  ✅ Downloaded {len(response.content)} bytes")
        
        pdf_file = BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        
        print(f"  📖 Pages in PDF: {len(reader.pages)}\n")
        
        # Extract text from each page
        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            print(f"--- Page {i} ---")
            print(text)
            print()
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

# Test with a-beautiful-day
slug = "a-beautiful-day"
pdf_url = f"{CLOUDFRONT_BASE}/{slug}/ebook/en_english/{slug}_en.pdf"

print("🧪 Testing PDF Text Extraction\n")
extract_text_from_pdf(pdf_url)
