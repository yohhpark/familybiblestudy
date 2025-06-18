import requests
from bs4 import BeautifulSoup
import json

# ✅ CONFIG
tripol_url = "https://tripol.tistory.com/76"  # 창세기 1장
output_path = r"D:\OneDrive\Yohhan\dz\git\genesis1_tripol.json"
headers = {"User-Agent": "Mozilla/5.0"}

# ✅ HTML 가져오기
print(f">> Downloading HTML from {tripol_url} ...")
response = requests.get(tripol_url, headers=headers, timeout=10)
response.encoding = "utf-8"

if response.status_code != 200:
    raise Exception(f"❌ Failed to download: Status code {response.status_code}")
print("✅ HTML download complete.")

# ✅ HTML 파싱
soup = BeautifulSoup(response.text, "html.parser")
content_div = soup.find("div", {"id": "tt-body-page"}) or soup.find("div", {"class": "tt_article_useless_p_margin"}) or soup.body
elements = content_div.find_all(["p", "span", "div"])

entries = []
current_entry = {}
current_commentary = []

def flush_entry():
    if current_entry.get("verse_id"):
        current_entry["commentary"] = "\n".join(current_commentary).strip()
        entries.append(current_entry.copy())

total_verses = 31  # 창세기 1장은 31절

for tag in elements:
    text = tag.get_text().strip()
    if not text:
        continue

    if text.startswith("창세기 1장 ") and "절" in text:
        flush_entry()
        verse_num = int(text.split("절")[0].strip().split()[-1])
        percent = round(verse_num / total_verses * 100, 1)
        print(f">>> GEN_1_{verse_num} [ {verse_num}/{total_verses} | {percent}% ] ...", end=" ")

        current_entry = {
            "verse_id": f"GEN_1_{verse_num}",
            "kor": "",
            "eng": "",
            "heb": "",
            "grk": ""
        }
        current_commentary = []
        print("Done ✅")

    elif text.startswith("개역개정:"):
        current_entry["kor"] = text.replace("개역개정:", "").strip()
    elif text.startswith("히브리어 구약:") or text.startswith("히브리어(구약):"):
        current_entry["heb"] = text.split(":", 1)[-1].strip()
    elif text.startswith("헬라어:"):
        current_entry["grk"] = text.replace("헬라어:", "").strip()
    elif text.startswith("영어 NIV:"):
        current_entry["eng"] = text.replace("영어 NIV:", "").strip()
    else:
        current_commentary.append(text)

flush_entry()

# ✅ JSON으로 저장
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f"\n✅ {len(entries)} verses saved to: {output_path}")