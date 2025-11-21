#this code confirms that it can print out the required data from the webpage

import requests
from bs4 import BeautifulSoup
import re
import json

# 1. Fetch webpage content
url = "https://nocr.net/com_kor_hochma/139393"
response = requests.get(url)
html_content = response.text
# print("Successfully fetched HTML content.")

# 2. Parse HTML content
soup = BeautifulSoup(html_content, 'html.parser')
# print("HTML content parsed successfully into a BeautifulSoup object.")

# 3. Extract Bible Book and Chapter
title_tag = soup.find('title')
if title_tag:
    full_title = title_tag.get_text(strip=True)
    # Corrected Regular expression to extract the book name and chapter number
    # It looks for Korean characters (book name) followed by optional space, digits, and '\uc7a5' (chapter)
    match = re.search(r'([\uac00-\ud7a3]+)\s*(\d+\uc7a5)', full_title)
    if match:
        bible_book = match.group(1).strip()
        chapter_number_str = match.group(2).strip()
        chapter_number = int(chapter_number_str.replace('장', ''))
        # print(f"Extracted Bible Book: {bible_book}")
        # print(f"Extracted Chapter Number: {chapter_number}")
    else:
        # print("Could not find Bible book and chapter in title.")
        bible_book = "Unknown Book"
        chapter_number = 0
else:
    # print("Title tag not found.")
    bible_book = "Unknown Book"
    chapter_number = 0

# 4. Extract Commentary Text
commentaries = []
current_verse_reference = None
current_commentary_parts = []

# Find the main container for the commentary
xe_content_div = soup.find('div', class_='xe_content')

if xe_content_div:
    full_content_text_with_newlines = xe_content_div.get_text(separator='\n')
    # print("\n--- full_content_text_with_newlines (first 1000 chars) ---\n", full_content_text_with_newlines[:1000], "...")

    text_blocks = re.split(r'\n\s*\n+', full_content_text_with_newlines)
    # print("\n--- text_blocks (first 5 elements) ---\n", text_blocks[:5])

    # Compile a more precise regex for verse references at the very beginning of a block
    # It must start with the current chapter number, followed by a colon and digits,
    # allowing for comma-separated verse numbers, then optional whitespace.
    verse_pattern = re.compile(rf"^{chapter_number}:(\d+(?:,\d+)*)\s*")

    for block in text_blocks:
        block = block.strip()
        if not block:
            continue

        match = verse_pattern.match(block)

        if match:
            # Found a new verse reference
            # If we were already collecting a commentary, save the previous one
            if current_verse_reference is not None and current_commentary_parts:
                commentaries.append({
                    "verse_reference": current_verse_reference,
                    "commentary": " ".join(current_commentary_parts).strip()
                })

            # Use the full matched verse reference string directly as the reference key
            current_verse_reference = match.group(0).strip() # e.g., "1:1" or "1:12,13"
            
            # The commentary starts after the full matched verse reference in this block
            commentary_text_in_this_block = block[len(current_verse_reference):].strip()

            # Initialize current_commentary_parts with the text immediately following the verse reference
            current_commentary_parts = [commentary_text_in_this_block]

        elif current_verse_reference is not None:
            # This block is part of the current commentary (no new verse reference found)
            current_commentary_parts.append(block)

    # Add the last commentary entry after the loop finishes
    if current_verse_reference is not None and current_commentary_parts:
        commentaries.append({
            "verse_reference": current_verse_reference,
            "commentary": " ".join(current_commentary_parts).strip()
        })

    # print(f"Extracted {len(commentaries)} commentary entries.")
    # # Optionally, print the first few entries to verify
    # for i, entry in enumerate(commentaries[:5]):
    # #    print(f"Entry {i+1}:\n  Verse: {entry['verse_reference']}\n  Commentary: {entry['commentary'][:200]}...")

else:
    print("Could not find the main commentary content area (div.xe_content).")

# 5. Structure Extracted Data
extracted_data = {
    "bible_book": bible_book,
    "chapter_number": chapter_number,
    "commentaries": commentaries
}

# Convert the dictionary to a JSON string
json_output = json.dumps(extracted_data, ensure_ascii=False, indent=4)

print("\n--- Final JSON Output ---")
print(json_output)