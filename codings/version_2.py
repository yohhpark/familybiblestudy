#this code confirms that it can upload to my personal git repository:familybiblestudy onto json_results folder

import requests
from bs4 import BeautifulSoup
import re
import json
import base64
import time # For exponential backoff

# ==============================================================================
# 1. GITHUB CONFIGURATION
# ==============================================================================
# NOTE: Replace 'YOUR_GITHUB_PAT' with your actual Personal Access Token
GITHUB_TOKEN = "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" 
REPO_OWNER = "yohhpark"
REPO_NAME = "familybiblestudy"
# The target directory within the repository
PATH_PREFIX = "bible_explanation"
BRANCH = "main" # Target branch

def upload_to_github(repo_owner, repo_name, file_path, content, token, commit_message):
    """
    Uploads or updates a file in a GitHub repository using the REST API.

    Args:
        repo_owner (str): The owner of the repository.
        repo_name (str): The name of the repository.
        file_path (str): The full path to the file in the repo (e.g., 'json_results/file.json').
        content (str): The raw string content of the file (will be base64 encoded).
        token (str): The GitHub Personal Access Token.
        commit_message (str): The commit message.
    """
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    # 1. Base64 encode the content
    # We must encode the content bytes, not the string directly.
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    # 2. Check if the file exists to get its SHA (required for updating)
    sha = None
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            get_response = requests.get(api_url, headers=headers)
            if get_response.status_code == 200:
                # File exists, retrieve its SHA
                sha = get_response.json().get('sha')
                print(f"File found. Retrieved SHA: {sha}")
            elif get_response.status_code == 404:
                # File does not exist, proceed with creation
                print("File not found on GitHub. Preparing to create it.")
            
            # Break retry loop if successful or 404
            break
        except requests.exceptions.RequestException as e:
            print(f"Error fetching file metadata (Attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Failed to fetch file metadata after multiple retries. Aborting upload.")
                return

    # 3. Construct the upload payload
    payload = {
        "message": commit_message,
        "content": encoded_content,
        "branch": BRANCH
    }
    
    if sha:
        payload["sha"] = sha # Include SHA for updates

    # 4. Perform the PUT request to upload/update the file
    for attempt in range(max_retries):
        try:
            put_response = requests.put(api_url, headers=headers, json=payload)
            if put_response.status_code in [200, 201]:
                action = "Updated" if sha else "Created"
                print(f"SUCCESS: File {action} on GitHub at: {put_response.json()['content']['html_url']}")
                return put_response.json()
            else:
                print(f"GitHub API Error (Attempt {attempt + 1}): Status {put_response.status_code}")
                print(f"Response Body: {put_response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error during GitHub upload (Attempt {attempt + 1}): {e}")
        
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(f"Retrying upload in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print("Failed to upload file to GitHub after multiple retries.")
            return None


# ==============================================================================
# 2. WEB SCRAPING AND DATA EXTRACTION (Mostly unchanged)
# ==============================================================================
url = "https://nocr.net/com_kor_hochma/139393"
response = requests.get(url)
html_content = response.text
print(f"Successfully fetched HTML content from: {url}")

# Parse HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Extract Bible Book and Chapter
title_tag = soup.find('title')
if title_tag:
    full_title = title_tag.get_text(strip=True)
    # Regular expression to extract the book name and chapter number (e.g., 잠언 1장)
    # The pattern looks for Korean characters (book name) followed by optional space, digits, and '장' (chapter)
    match = re.search(r'([\uac00-\ud7a3]+)\s*(\d+)\s*장', full_title)
    if match:
        bible_book = match.group(1).strip()
        chapter_number_str = match.group(2).strip()
        chapter_number = int(chapter_number_str)
        print(f"Extracted Bible Book: {bible_book}")
        print(f"Extracted Chapter Number: {chapter_number}")
    else:
        print("Could not find Bible book and chapter in title. Defaulting.")
        bible_book = "Unknown Book"
        chapter_number = 0
else:
    print("Title tag not found. Defaulting.")
    bible_book = "Unknown Book"
    chapter_number = 0

# Extract Commentary Text
commentaries = []
current_verse_reference = None
current_commentary_parts = []

xe_content_div = soup.find('div', class_='xe_content')

if xe_content_div:
    # Use separator='\n' to ensure block separation is maintained for reliable parsing
    full_content_text_with_newlines = xe_content_div.get_text(separator='\n')

    # Split into blocks separated by two or more newlines (common for commentary structure)
    text_blocks = re.split(r'\n\s*\n+', full_content_text_with_newlines)

    # Compile a precise regex for verse references at the very beginning of a block
    # It must start with the current chapter number, followed by a colon and digits,
    # allowing for comma-separated verse numbers, then optional whitespace.
    # Example match: "1:1" or "1:12,13"
    verse_pattern = re.compile(rf"^{chapter_number}:(\d+(?:,\d+)*)\s*")

    for block in text_blocks:
        block = block.strip()
        if not block:
            continue

        match = verse_pattern.match(block)

        if match:
            # Found a new verse reference
            # 1. Save the previous commentary entry if one exists
            if current_verse_reference is not None and current_commentary_parts:
                commentaries.append({
                    "verse_reference": current_verse_reference,
                    # Join parts with a single space and clean up excess whitespace
                    "commentary": " ".join(part for part in current_commentary_parts if part).strip()
                })

            # 2. Start new commentary
            current_verse_reference = match.group(0).strip() 
            
            # The commentary starts immediately after the verse reference in this block
            commentary_text_in_this_block = block[len(current_verse_reference):].strip()

            # Initialize current_commentary_parts with the text immediately following the verse reference
            current_commentary_parts = [commentary_text_in_this_block]

        elif current_verse_reference is not None:
            # This block is a continuation of the current commentary
            current_commentary_parts.append(block)

    # 3. Add the last commentary entry after the loop finishes
    if current_verse_reference is not None and current_commentary_parts:
        commentaries.append({
            "verse_reference": current_verse_reference,
            "commentary": " ".join(part for part in current_commentary_parts if part).strip()
        })
    
    print(f"Extracted {len(commentaries)} commentary entries.")

else:
    print("Could not find the main commentary content area (div.xe_content).")

# Structure Extracted Data
extracted_data = {
    "bible_book": bible_book,
    "chapter_number": chapter_number,
    "commentaries": commentaries
}

# Convert the dictionary to a JSON string with proper indentation and Korean support
json_output = json.dumps(extracted_data, ensure_ascii=False, indent=4)


# ==============================================================================
# 3. UPLOAD TO GITHUB
# ==============================================================================

if bible_book != "Unknown Book" and chapter_number != 0:
    # Generate the dynamic filename (e.g., '잠언_1.json')
    filename = f"{bible_book}_{chapter_number}.json"
    # Create the full file path (e.g., 'json_results/잠언_1.json')
    github_file_path = f"{PATH_PREFIX}/{filename}"
    commit_message = f"Add commentary for {bible_book} Chapter {chapter_number}"

    print(f"\n--- Starting GitHub Upload ---\nTarget File: {github_file_path}")

    # Check if the token is the placeholder
    if GITHUB_TOKEN == "YOUR_GITHUB_PAT":
        print("\n!!! ERROR !!!")
        print("Please replace 'YOUR_GITHUB_PAT' in the GITHUB_TOKEN variable with your actual GitHub Personal Access Token before running.")
    else:
        upload_to_github(
            REPO_OWNER, 
            REPO_NAME, 
            github_file_path, 
            json_output, 
            GITHUB_TOKEN, 
            commit_message
        )
else:
    print("\nSkipping GitHub upload because Bible book or chapter could not be determined.")