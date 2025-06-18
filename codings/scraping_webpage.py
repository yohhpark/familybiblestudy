import requests
import os

# ✅ CONFIG
url = "https://tripol.tistory.com/76"  # 창세기 1장
output_dir = r"D:\OneDrive\Yohhan\dz\git"
output_filename = "tripol_genesis1_raw.html"
output_path = os.path.join(output_dir, output_filename)

# ✅ HEADERS
headers = {
    "User-Agent": "Mozilla/5.0"
}

# ✅ START SCRAPING
print(f">> Starting download from: {url}")
print(f">> Saving to: {output_path}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = "utf-8"

    # Check response status
    if response.status_code == 200:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print("✅ Success! HTML content saved.")
    else:
        print(f"❌ Failed to download page. Status code: {response.status_code}")

except Exception as e:
    print(f"❌ Failed to retrieve page due to error: {str(e)}")