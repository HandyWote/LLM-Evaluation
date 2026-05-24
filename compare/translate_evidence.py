"""Translate English evidence columns in disagreement_cn.csv to Chinese using LLM API."""

import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)
MODEL = os.getenv("OPENAI_MODEL", "deepseek-v4-flash")

INPUT = "compare/disagreement_cn.csv"
OUTPUT = INPUT
CONCURRENCY = 20


def translate(text: str) -> str:
    """Translate English text to Chinese."""
    if not text or not text.strip():
        return text
    chinese_chars = sum(1 for c in text if '一' <= c <= '鿿')
    if chinese_chars / max(len(text), 1) > 0.3:
        return text

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "你是学术翻译专家。将以下英文学术文本翻译成中文，保持学术风格，保留术语和引用。只输出翻译结果，不要解释。",
            },
            {"role": "user", "content": text},
        ],
        temperature=0.1,
    )
    return resp.choices[0].message.content.strip()


def translate_row(idx_row):
    """Translate a single row's evidence columns. Returns (idx, col, translated)."""
    idx, row = idx_row
    results = []
    for col in ["原始证据", "cxt补充证据"]:
        original = row.get(col, "")
        if original and original.strip():
            try:
                translated = translate(original)
                results.append((idx, col, translated))
            except Exception as e:
                print(f"  [!] Row {idx} {col}: {e}")
    return results


def main():
    with open(INPUT, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    total = len(rows)
    print(f"共 {total} 行, 并发={CONCURRENCY}")

    tasks = [(i, row) for i, row in enumerate(rows)]
    done = 0

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futures = {pool.submit(translate_row, t): t[0] for t in tasks}
        for future in as_completed(futures):
            results = future.result()
            for idx, col, translated in results:
                rows[idx][col] = translated
            done += 1
            if done % 20 == 0 or done == total:
                print(f"  [{done}/{total}] 完成, 保存中...")
                with open(OUTPUT, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)

    print(f"\n完成! 已写入 {OUTPUT}")


if __name__ == "__main__":
    main()
