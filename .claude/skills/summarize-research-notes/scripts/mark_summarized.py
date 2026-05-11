"""
在已总结论文的研究笔记中插入反向链接标记。

使用方式:
  uv run .claude/skills/summarize-research-notes/scripts/mark_summarized.py \
    --papers 1,6,10 --summary summary-1-6-10.md --dir extract/eval_reports
"""

import argparse
import json
import re
import sys
from pathlib import Path

NOTES_SECTION_RE = re.compile(r"^(## 研究笔记\s*)$", re.MULTILINE)
SUMMARY_MARKER_RE = re.compile(r"^> 已总结于 \[summary-.*\.md\]\(summary-.*\.md\)$", re.MULTILINE)


def mark_paper(report_path: Path, summary_filename: str) -> bool:
    """在论文的 ## 研究笔记 下方插入标记。返回是否修改。"""
    content = report_path.read_text(encoding="utf-8")

    # 已有标记 → 跳过
    if SUMMARY_MARKER_RE.search(content):
        return False

    # 找到 ## 研究笔记 行，在其后插入标记
    marker_line = f"> 已总结于 [{summary_filename}]({summary_filename})\n"
    new_content, count = NOTES_SECTION_RE.subn(r"\1\n" + marker_line, content, count=1)

    if count == 0:
        return False

    report_path.write_text(new_content, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="在已总结论文中插入反向链接标记")
    parser.add_argument("--papers", required=True, help="论文 ID 列表，逗号分隔（如 1,6,10）")
    parser.add_argument("--summary", required=True, help="summary 文件名（如 summary-1-6-10.md）")
    parser.add_argument("--dir", type=Path, required=True, help="eval_reports 目录路径")
    args = parser.parse_args()

    paper_ids = [pid.strip() for pid in args.papers.split(",")]
    modified = []
    skipped = []

    for pid in paper_ids:
        report_path = args.dir / f"{pid}.md"
        if not report_path.exists():
            print(f"警告: {report_path} 不存在，跳过", file=sys.stderr)
            skipped.append(pid)
            continue

        if mark_paper(report_path, args.summary):
            modified.append(pid)
        else:
            skipped.append(pid)

    result = {"modified": modified, "skipped": skipped}
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
