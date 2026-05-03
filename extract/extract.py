"""
从 paper/ 目录下的 PDF 提取文本，调用 OpenAI 兼容 API 提取论文元数据，输出 CSV。

使用方式:
  1. cp .env.example .env，填入 API 配置
  2. uv run extract.py
  3. 输出: paper_metadata.csv
"""

import asyncio
import csv
import json
import os
import re
import sys
from pathlib import Path

import fitz  # pymupdf
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

PAPER_DIR = Path(__file__).parent / "paper"
OUTPUT_CSV = Path(__file__).parent / "paper_metadata.csv"
EXTRACT_PAGES = 2
MAX_CONCURRENCY = 1
MAX_RETRIES = 3

SYSTEM_PROMPT = """\
你是一个学术论文元数据提取助手。从给定的论文文本中提取以下字段使用英文，以 JSON 对象返回。

字段说明：
- title: 论文标题
- year: 发表年份（数字）
- venue: 发表场所（会议名/期刊名）
- first_author: 第一作者姓名
- domain: 留空字符串 ""
- assigned_to: 留空字符串 ""
- status: 留空字符串 ""
- notes: 留空字符串 ""
- keywords: 根据论文内容推断检索这篇论文时可能使用的搜索关键词，用逗号分隔

只返回 JSON 对象，不要返回其他内容。示例格式：
{"title": "...", "year": 2024, "venue": "...", "first_author": "...", "domain": "", "assigned_to": "", "status": "", "notes": "", "keywords": "keyword1, keyword2, keyword3"}
"""

FIELDS = [
    "id", "title", "year", "venue", "first_author",
    "domain", "pdf_saved", "assigned_to", "status", "notes", "keywords",
]


def extract_text(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    pages_text = []
    for i in range(min(EXTRACT_PAGES, len(doc))):
        pages_text.append(doc[i].get_text())
    doc.close()
    return "\n\n".join(pages_text)


def parse_id(filename: str) -> str:
    match = re.match(r"(\d+)", filename)
    return match.group(1) if match else filename


async def call_llm(client: AsyncOpenAI, model: str, semaphore: asyncio.Semaphore, paper_id: str, pdf_path: Path) -> dict | None:
    async with semaphore:
        print(f"[{paper_id}] {pdf_path.name} ... ", end="", flush=True)
        text = extract_text(pdf_path)
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"请从以下论文文本中提取元数据：\n\n{text[:12000]}"},
                    ],
                    temperature=0,
                )
                content = resp.choices[0].message.content
                if content is None:
                    raise ValueError("API 返回内容为空")
                content = content.strip()
                if content.startswith("```"):
                    content = re.sub(r"^```\w*\n?", "", content)
                    content = re.sub(r"\n?```$", "", content)
                meta = json.loads(content)
                row = {
                    "id": paper_id,
                    "title": meta.get("title", ""),
                    "year": meta.get("year", ""),
                    "venue": meta.get("venue", ""),
                    "first_author": meta.get("first_author", ""),
                    "domain": meta.get("domain", ""),
                    "pdf_saved": "",
                    "assigned_to": meta.get("assigned_to", ""),
                    "status": meta.get("status", ""),
                    "notes": meta.get("notes", ""),
                    "keywords": meta.get("keywords", ""),
                }
                print("OK")
                return row
            except Exception as e:
                if attempt < MAX_RETRIES:
                    print(f"重试 {attempt}/{MAX_RETRIES} ({e}) ... ", end="", flush=True)
                    await asyncio.sleep(2 * attempt)
                else:
                    print(f"跳过: {e}")
                    return None


def load_existing_ids() -> set[str]:
    if not OUTPUT_CSV.exists():
        return set()
    with open(OUTPUT_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return {row["id"] for row in reader if row.get("id")}


async def main():
    base_url = os.environ.get("OPENAI_BASE_URL")
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")

    if not base_url or not api_key or not model:
        print("错误: 请在 .env 中设置 OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL")
        sys.exit(1)
    assert base_url and api_key and model

    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    pdfs = sorted(PAPER_DIR.glob("*.pdf"), key=lambda p: parse_id(p.name))
    if not pdfs:
        print(f"在 {PAPER_DIR} 中未找到 PDF 文件")
        sys.exit(1)

    existing_ids = load_existing_ids()
    new_pdfs = [p for p in pdfs if parse_id(p.name) not in existing_ids]

    if not new_pdfs:
        print("没有新增论文，全部已处理。")
        return

    print(f"共 {len(pdfs)} 篇，已有 {len(existing_ids)} 篇，新增 {len(new_pdfs)} 篇（并发数 {MAX_CONCURRENCY}）...\n")

    tasks = [
        call_llm(client, model, semaphore, parse_id(p.name), p)
        for p in new_pdfs
    ]
    results = await asyncio.gather(*tasks)
    new_rows = [r for r in results if r is not None]

    write_header = not OUTPUT_CSV.exists() or OUTPUT_CSV.stat().st_size == 0
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(new_rows)

    print(f"\n完成！{len(new_rows)}/{len(new_pdfs)} 篇新增记录已追加到 {OUTPUT_CSV}")


if __name__ == "__main__":
    asyncio.run(main())
