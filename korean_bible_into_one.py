import os

input_dir = r"D:\OneDrive\Yohhan\dz\git\개역개정"  # <- 파일이 있는 폴더 경로
output_path = r"D:\OneDrive\Yohhan\dz\git\kr_bible_verses.txt"  # 출력 경로

# .txt 파일들 정렬 (숫자 기준으로 정렬됨)
files = sorted(
    [f for f in os.listdir(input_dir) if f.endswith(".txt")],
    key=lambda x: (
        int(x.split("-")[0]),   # 1 or 2 (구약/신약)
        int(x.split("-")[1][:2])  # 책 번호
    )
)

with open(output_path, "w", encoding="utf-8") as outfile:
    for fname in files:
        file_path = os.path.join(input_dir, fname)
        try:
            with open(file_path, "r", encoding="cp949") as infile:
                for line in infile:
                    line = line.strip()
                    if line:  # 빈 줄 제거
                        outfile.write(line + "\n")
        except Exception as e:
            print(f"❌ {fname} 읽는 중 에러: {e}")

print(f"✅ 완료! 출력 파일 위치: {output_path}")
