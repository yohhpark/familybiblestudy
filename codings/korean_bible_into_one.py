import os

def is_valid_line(line):
    return len(line) >= 5 and ":" in line  # 예: "창1:1 내용"

input_dir = r"D:\OneDrive\Yohhan\dz\git\개역개정"
output_path = r"D:\OneDrive\Yohhan\dz\git\kr_bible_verses.txt"

files = sorted(
    [f for f in os.listdir(input_dir) if f.endswith(".txt")],
    key=lambda x: (
        int(x.split("-")[0]),
        int(x.split("-")[1][:2])
    )
)

failures = []

with open(output_path, "w", encoding="utf-8") as outfile:
    for fname in files:
        book_name = fname.split("-")[1].replace(".txt", "")
        print(f">> {book_name} 처리 중...", end=" ")

        file_path = os.path.join(input_dir, fname)
        line_count = 0
        invalid_lines = 0

        try:
            with open(file_path, "r", encoding="cp949") as infile:
                for line in infile:
                    cleaned = line.strip()
                    if cleaned:
                        line_count += 1
                        if is_valid_line(cleaned):
                            outfile.write(cleaned + "\n")
                        else:
                            invalid_lines += 1

            if line_count == 0:
                print("⚠️ 내용 없음! 처리 못함!")
                failures.append((book_name, "내용 없음"))
            elif invalid_lines > 0:
                print(f"⚠️ {invalid_lines}개 줄 이상함! 처리 실패!")
                failures.append((book_name, f"{invalid_lines}개 줄 포맷 오류"))
            else:
                print("처리완료! ✅")

        except Exception as e:
            print("처리 못함! ❌")
            failures.append((book_name, f"에러: {str(e)}"))

# 파이널 검토
print("\n>> 파이널 체크...", end=" ")
if failures:
    print("❌ 실패 항목 있음!")
    for book, reason in failures:
        print(f"   - {book}: {reason}")
else:
    print("✅ 전체 문제 없이 완료!")

print(f"\n📝 최종 파일 위치: {output_path}")