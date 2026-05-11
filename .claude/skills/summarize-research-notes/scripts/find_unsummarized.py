"""
扫描 eval_reports/ 目录，找出尚未被总结的研究笔记。

使用方式:
  uv run .claude/skills/summarize-research-notes/scripts/find_unsummarized.py extract/eval_reports
  uv run .claude/skills/summarize-research-notes/scripts/find_unsummarized.py extract/eval_reports --summary summary-1-6.md
"""

import argparse
import json
import re
import sys
from pathlib import Path

SUMMARY_MARKER_RE = re.compile(r"^> 已总结于 \[summary-.*\.md\]\(summary-.*\.md\)$", re.MULTILINE)
NOTES_SECTION_RE = re.compile(r"^## 研究笔记\s*$", re.MULTILINE)


def find_unsummarized(reports_dir: Path) -> dict:
    """扫描目录，返回未总结的论文信息。"""
    unsummarized = []
    total_with_notes = 0
    already_summarized = []

    for md_file in sorted(reports_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")

        # 必须有 ## 研究笔记 section
        if not NOTES_SECTION_RE.search(content):
            continue

        total_with_notes += 1
        paper_id = md_file.stem

        # 检查是否有已总结标记
        if SUMMARY_MARKER_RE.search(content):
            already_summarized.append(paper_id)
        else:
            unsummarized.append(paper_id)

    return {
        "unsummarized": unsummarized,
        "total_with_notes": total_with_notes,
        "already_summarized": already_summarized,
    }


def main():
    parser = argparse.ArgumentParser(description="扫描 eval_reports，找出未总结的研究笔记")
    parser.add_argument("reports_dir", type=Path, help="eval_reports 目录路径")
    parser.add_argument(
        "--summary",
        type=str,
        default=None,
        help="如果指定，检查该 summary 文件是否已存在（用于覆盖提示）",
    )
    args = parser.parse_args()

    if not args.reports_dir.is_dir():
        print(f"错误: {args.reports_dir} 不是有效目录", file=sys.stderr)
        sys.exit(1)

    result = find_unsummarized(args.reports_dir)

    if args.summary:
        summary_path = args.reports_dir / args.summary
        result["summary_exists"] = summary_path.exists()

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
