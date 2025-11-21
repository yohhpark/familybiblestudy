import requests
from bs4 import BeautifulSoup
import re

all_extracted_chapters = []
current_id = 139393 # Starting ID as per instructions
base_url = "https://nocr.net/com_kor_hochma/"

print(f"Starting dynamic scrape from ID {current_id} to find '요한계시록 22장'...")

while True:
    full_url = f"{base_url}{current_id}"
    bible_book = "N/A"
    chapter_number = "N/A"
    
    try:
        response = requests.get(full_url, timeout=10) # Added timeout for robustness
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        title_tag = soup.find('title')

        if title_tag:
            full_title = title_tag.get_text(strip=True)
            # Pattern for Korean book name + digits + '장' (chapter)
            match = re.search(r'([가-힣]+)\s*(\d+)\s*장', full_title)
            if match:
                bible_book = match.group(1).strip()
                chapter_number = int(match.group(2).strip())

        if bible_book != "N/A" and chapter_number != "N/A":
            entry = {
                "url": full_url,
                "bible_book": bible_book,
                "chapter_number": chapter_number
            }
            all_extracted_chapters.append(entry)
            print(f"SUCCESS: {full_url} -> Book: {bible_book}, Chapter: {chapter_number}")

            # Check for stop condition
            if bible_book == '요한계시록' and chapter_number == 22:
                print(f"\nStopping: Successfully extracted '요한계시록 22장' from {full_url}.")
                break

    except requests.exceptions.RequestException:
        # Suppress error message printing as per instructions
        pass
    except Exception:
        # Suppress error message printing as per instructions
        pass

    current_id += 1

print(f"\nFinished processing. Total chapters successfully extracted: {len(all_extracted_chapters)}")
