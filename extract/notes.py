"""
为论文 eval_report 生成 AI 研究笔记，追加到报告末尾。
课题组同学只需阅读笔记即可理解论文内容及其评估方法论问题。

使用方式:
  1. 确保 .env 中已配置 OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL
  2. uv run notes.py                      # 处理所有有 eval_report 的论文
  3. uv run notes.py --paper 1            # 仅处理论文 1
  4. uv run notes.py --force              # 强制重新生成已有笔记
"""

import argparse
import asyncio
import logging
import os
import re
import sys
import traceback
from pathlib import Path

import fitz
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

MAX_CONCURRENCY = 3
REPORTS_DIR = Path(__file__).parent / "eval_reports"
PAPER_DIR = Path(__file__).parent / "paper"
CODING_TABLE_PATH = Path(__file__).parent.parent / "docs" / "评估维度表.md"


def parse_id(filename: str) -> str:
    match = re.match(r"(\d+)", filename)
    return match.group(1) if match else Path(filename).stem


def has_notes_section(content: str) -> bool:
    return bool(re.search(r"^## 研究笔记\s*$", content, re.MULTILINE))


def build_notes_section(notes_text: str) -> str:
    return f"\n## 研究笔记\n\n{notes_text}\n"


def append_notes(report_path: Path, notes_text: str):
    section = build_notes_section(notes_text)
    with open(report_path, "a", encoding="utf-8") as f:
        f.write(section)


def remove_existing_notes(report_path: Path) -> None:
    content = report_path.read_text(encoding="utf-8")
    if not has_notes_section(content):
        return
    new_content = re.sub(r"\n## 研究笔记\s*\n[\s\S]*$", "", content)
    report_path.write_text(new_content, encoding="utf-8")


def extract_full_text(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages)


# --- Prompt Construction ---

def build_system_prompt() -> str:
    return """\
你是一个学术论文元评测研究助手。你的任务是从论文全文中生成研究笔记， \
使课题组同学无需阅读原文即可理解论文内容及其评估方法论问题。

你的研究视角：关注论文"声明的目标"与"实际采用的评估方法"之间的对齐程度。\
许多声称构建"有共情能力的 AI 心理咨询师"的论文，实际使用的评估指标 \
（ROUGE、BLEU、GPT-4 Likert 评分等）缺乏心理学效度。

笔记面向课题组同学，必须自成体系、大白话、避免堆砌学术黑话。\
用中文撰写。"""


def build_user_message(
    coding_table: str,
    eval_report: str,
    pdf_text: str,
) -> str:
    return f"""\
## 参考材料

### 1. 评估维度表（批判视角的参考框架）

{coding_table}

### 2. 已提取的评估信息（eval_report）

以下是已从本论文中结构化提取的评估方法字段，供参考但不要简单重复：

{eval_report}

### 3. 论文全文

{pdf_text}

---

## 生成要求

请在 eval_report 已有内容的基础上，生成以下两部分笔记：

### 概括（3 段）

1. **研究目标：** 这篇论文想解决什么问题？声称要实现什么？（1-2 句）
2. **方法概述：** 他们怎么做的？（重点展开，3-5 句。核心架构、数据、流程， \
用大白话说清楚，不要堆砌技术名词）
3. **主要结果：** 他们声称得到了什么结论？（2-3 句）

### 评价（2-4 段自然段落）

从元评测视角审视这篇论文的评估方法论。重点关注：

- **维度选取是否有理论依据：** 作者选择了哪些评估维度？有没有引用已有研究来 \
说明为什么这些维度能反映 AI 的能力？还是作者自己定义维度、自说自话？ \
如果维度选取缺乏理论支撑，可能存在挑选有利维度让结果好看的嫌疑。
- **评估方法与声明目标的匹配度：** 论文声称在评估"共情"、"治疗联盟"等心理建构， \
实际测的真的是这些吗？还是用文本相似度、流畅度等表面指标来替代？
- **信度和效度问题：** 有没有报告评分者间信度？评估量表有没有经过验证？ \
LLM-as-judge 有没有和人类专家校准？
- **实验设计的合理性：** 对照组设置、样本量、交互深度是否足以支撑论文的声明？

评价要具体，指出论文中具体的做法和问题，不要泛泛而谈。不要批评论文本身的研究动机，\
聚焦在评估方法论上。

直接输出笔记内容，不要包含 markdown 代码块标记。使用以下格式：

**研究目标：** ...

**方法概述：** ...

**主要结果：** ...

（评价部分直接写自然段落，不用小标题）"""


# --- Response Parsing ---

def strip_response(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```\w*\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return content.strip()


# --- Idempotency ---

def load_existing_note_ids(reports_dir: Path) -> set[str]:
    if not reports_dir.exists():
        return set()
    ids = set()
    for f in reports_dir.glob("*.md"):
        content = f.read_text(encoding="utf-8")
        if has_notes_section(content):
            ids.add(parse_id(f.name))
    return ids


# --- Core Logic ---

async def generate_notes(
    client: AsyncOpenAI,
    model: str,
    paper_id: str,
    pdf_path: Path,
    report_path: Path,
    coding_table: str,
    semaphore: asyncio.Semaphore,
) -> bool:
    print(f"[{paper_id}] 生成笔记中...")
    try:
        pdf_text = extract_full_text(pdf_path)
    except Exception as e:
        print(f"[{paper_id}] PDF 读取失败: {e}")
        return False

    eval_report = report_path.read_text(encoding="utf-8")

    system_prompt = build_system_prompt()
    user_message = build_user_message(coding_table, eval_report, pdf_text)

    try:
        async with semaphore:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
            )
        notes_text = strip_response(response.choices[0].message.content)
    except Exception as e:
        print(f"[{paper_id}] LLM 调用失败: {e}")
        traceback.print_exc()
        return False

    append_notes(report_path, notes_text)
    print(f"[{paper_id}] 已追加到 {report_path.name}")
    return True


# --- Main ---

async def main():
    parser = argparse.ArgumentParser(description="为论文 eval_report 生成 AI 研究笔记")
    parser.add_argument("--dir", type=str, default=None, help="eval_reports 目录路径")
    parser.add_argument("--paper", type=str, default=None, help="仅处理指定论文ID")
    parser.add_argument("--force", action="store_true", help="强制重新生成已有笔记")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    base_url = os.environ.get("OPENAI_BASE_URL")
    api_key = os.environ.get("OPENAI_API_KEY")
    default_model = os.environ.get("OPENAI_MODEL")
    notes_model = os.environ.get("NOTES_MODEL", default_model)

    if not base_url or not api_key or not default_model:
        print("错误: 请在 .env 中设置 OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL")
        sys.exit(1)

    reports_dir = Path(args.dir) if args.dir else REPORTS_DIR
    if not reports_dir.exists():
        print(f"错误: 目录不存在: {reports_dir}")
        sys.exit(1)

    coding_table_path = CODING_TABLE_PATH
    if not coding_table_path.exists():
        print(f"错误: 评估维度表不存在: {coding_table_path}")
        sys.exit(1)
    coding_table = coding_table_path.read_text(encoding="utf-8")

    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    existing_ids = load_existing_note_ids(reports_dir) if not args.force else set()

    if args.force:
        if args.paper:
            remove_existing_notes(reports_dir / f"{args.paper}.md")
        else:
            for f in reports_dir.glob("*.md"):
                remove_existing_notes(f)

    if args.paper:
        report_path = reports_dir / f"{args.paper}.md"
        pdf_path = PAPER_DIR / f"{args.paper}.pdf"
        if not report_path.exists():
            print(f"错误: eval_report 不存在: {report_path}")
            sys.exit(1)
        if not pdf_path.exists():
            print(f"错误: PDF 不存在: {pdf_path}")
            sys.exit(1)
        if not args.force and args.paper in existing_ids:
            print(f"[{args.paper}] 已有笔记，跳过（使用 --force 强制重新生成）")
            return
        tasks = [(args.paper, pdf_path, report_path)]
    else:
        all_reports = sorted(reports_dir.glob("*.md"), key=lambda p: parse_id(p.name))
        tasks = []
        for r in all_reports:
            pid = parse_id(r.name)
            if pid in existing_ids:
                continue
            pdf = PAPER_DIR / f"{pid}.pdf"
            if not pdf.exists():
                print(f"[{pid}] 跳过: PDF 不存在 ({pdf.name})")
                continue
            tasks.append((pid, pdf, r))

    if not tasks:
        print("没有新增论文需要生成笔记。")
        return

    print(f"共 {len(tasks)} 篇待处理（并发数 {MAX_CONCURRENCY}）...\n")

    coros = [
        generate_notes(client, notes_model, pid, pdf, report, coding_table, semaphore)
        for pid, pdf, report in tasks
    ]
    results = await asyncio.gather(*coros)

    success = sum(results)
    failed = len(results) - success
    print(f"\n完成！{success}/{len(tasks)} 篇成功" + (f"，{failed} 篇失败" if failed else ""))


if __name__ == "__main__":
    asyncio.run(main())
