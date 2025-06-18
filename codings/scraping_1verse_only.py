from bs4 import BeautifulSoup
import json

# ✅ [1] HTML 파일 경로 설정
html_path = r"D:\OneDrive\Yohhan\dz\git\tripol_genesis1_raw.html"

# ✅ [2] HTML 불러오기
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# ✅ [3] BeautifulSoup 파싱
soup = BeautifulSoup(html, "html.parser")
content_div = (
    soup.find("div", {"id": "tt-body-page"}) or
    soup.find("div", {"class": "tt_article_useless_p_margin"}) or
    soup.body
)

text_lines = content_div.get_text(separator="\n").splitlines()

# ✅ [4] 창세기 1장 1절 블록 추출
current_block = []
record = False
for line in text_lines:
    line = line.strip()
    if "창세기 1장 1절" in line:
        record = True
        continue
    if "창세기 1장 2절" in line:
        break
    if record:
        current_block.append(line)

# ✅ [5] 번역/본문 추출 함수
def extract_translation(block, keyword):
    for line in block:
        if keyword in line:
            parts = line.split(keyword + ",")
            if len(parts) > 1:
                return parts[1].strip()
    return ""

def extract_next_line_after_keyword(block, keyword):
    for i, line in enumerate(block):
        if keyword in line and i + 1 < len(block):
            return block[i + 1].strip()
    return ""

# ✅ [6] 결과 구성
parsed = {
    "verse": "GEN_1_1",
    "kor": extract_translation(current_block, "개역개정"),
    "eng": extract_translation(current_block, "영어NIV"),
    "heb": extract_translation(current_block, "히브리어구약BHS"),
    "heb_pronunciation": extract_next_line_after_keyword(current_block, "히브리어구약BHS"),
    "grk": extract_translation(current_block, "헬라어구약Septuagint"),
    "commentary": "\n".join([
        line for line in current_block
        if not any(kw in line for kw in [
            "개역개정,", "영어NIV", "히브리어구약BHS", "헬라어구약Septuagint", "창세기 1장 1절"
        ])
    ]).strip()
}

# ✅ [7] JSON으로 저장
output_path = r"D:\OneDrive\Yohhan\dz\git\genesis1_verse1_parsed.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(parsed, f, ensure_ascii=False, indent=2)

print("✅ 저장 완료:", output_path)