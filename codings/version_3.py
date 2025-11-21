import requests
from bs4 import BeautifulSoup
import re
import json
import base64
import time # For exponential backoff

# ==============================================================================
# 1. GITHUB CONFIGURATION
# ==============================================================================
GITHUB_TOKEN = "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" # Replace with your token
REPO_OWNER = "yohhpark"
REPO_NAME = "familybiblestudy"
PATH_PREFIX = "bible_explanation" # Set to 'bible_explanation' as per instruction
BRANCH = "main"

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
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

    # 2. Check if the file exists to get its SHA (required for updating)
    sha = None
    max_retries = 3

    for attempt in range(max_retries):
        try:
            get_response = requests.get(api_url, headers=headers)
            if get_response.status_code == 200:
                sha = get_response.json().get('sha')
                print(f"File found. Retrieved SHA: {sha}")
            elif get_response.status_code == 404:
                print("File not found on GitHub. Preparing to create it.")
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
        payload["sha"] = sha

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