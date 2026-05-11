# summarize-research-notes Skill 改进实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 summarize-research-notes skill 添加批次管理和幂等性，通过两个 Python 脚本实现自动检测未总结论文和标记已总结论文。

**Architecture:** 两个独立脚本 + 更新 SKILL.md。`find_unsummarized.py` 扫描 eval_reports 找出未标记的论文，`mark_summarized.py` 在总结完成后打标记。SKILL.md 更新为三步工作流。

**Tech Stack:** Python 3.12, pathlib, re, argparse, json

---

### 文件结构

```
.claude/skills/summarize-research-notes/
├── SKILL.md                          (修改)
└── scripts/
    ├── find_unsummarized.py          (新建)
    └── mark_summarized.py            (新建)

extract/
└── test_summarize_scripts.py         (新建，测试两个脚本)
```

---

### Task 1: find_unsummarized.py

**Files:**
- Create: `.claude/skills/summarize-research-notes/scripts/find_unsummarized.py`

- [ ] **Step 1: 创建脚本**

```python
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

SUMMARY_MARKER_RE = re.compile(r"^> 已总结于 summary-.*\.md$", re.MULTILINE)
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
```

- [ ] **Step 2: 验证脚本可运行**

```bash
cd /Users/hand/project/LLM-Evaluate
uv run .claude/skills/summarize-research-notes/scripts/find_unsummarized.py extract/eval_reports
```

预期输出：JSON 列出当前未总结的论文（应该全部 10 篇都未总结）。

---

### Task 2: mark_summarized.py

**Files:**
- Create: `.claude/skills/summarize-research-notes/scripts/mark_summarized.py`

- [ ] **Step 1: 创建脚本**

```python
"""
在已总结论文的研究笔记中插入反向链接标记。

使用方式:
  uv run .claude/skills/summarize-research-notes/scripts/mark_summarized.py \
    --papers 1,6,10 --summary summary-1-6-10.md --dir extract/eval_reports
"""

import argparse
import re
import sys
from pathlib import Path

NOTES_SECTION_RE = re.compile(r"^(## 研究笔记\s*)$", re.MULTILINE)
SUMMARY_MARKER_RE = re.compile(r"^> 已总结于 summary-.*\.md$", re.MULTILINE)


def mark_paper(report_path: Path, summary_filename: str) -> bool:
    """在论文的 ## 研究笔记 下方插入标记。返回是否修改。"""
    content = report_path.read_text(encoding="utf-8")

    # 已有标记 → 跳过
    if SUMMARY_MARKER_RE.search(content):
        return False

    # 找到 ## 研究笔记 行，在其后插入标记
    marker_line = f"> 已总结于 {summary_filename}\n"
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
```

- [ ] **Step 2: 验证脚本可运行（dry run）**

先备份一篇论文，测试标记效果：

```bash
cd /Users/hand/project/LLM-Evaluate
cp extract/eval_reports/1.md /tmp/test_paper_1.md
uv run .claude/skills/summarize-research-notes/scripts/mark_summarized.py \
  --papers 1 --summary summary-1.md --dir extract/eval_reports
```

检查 `extract/eval_reports/1.md` 中 `## 研究笔记` 下方是否多了一行 `> 已总结于 summary-1.md`。

- [ ] **Step 3: 验证幂等性**

再运行一次，确认跳过（skipped 包含 "1"）：

```bash
uv run .claude/skills/summarize-research-notes/scripts/mark_summarized.py \
  --papers 1 --summary summary-1.md --dir extract/eval_reports
```

- [ ] **Step 4: 恢复测试文件**

```bash
cp /tmp/test_paper_1.md extract/eval_reports/1.md
```

---

### Task 3: 更新 SKILL.md

**Files:**
- Modify: `.claude/skills/summarize-research-notes/SKILL.md`

- [ ] **Step 1: 重写 SKILL.md**

```markdown
---
name: summarize-research-notes
description: Summarize and cross-compare research notes from eval_reports. Use when the user asks to summarize research notes, do cross-paper comparison, find commonalities/differences, or says "总结研究笔记", "跨论文对比", "求同求异", "总结评估方法论问题". Triggers on eval_reports/*.md analysis requests.
---

# Summarize Research Notes

你正在综合多篇 eval_reports 的评估方法论批判。目标是找出跨论文的共性模式——哪些做得好、哪些系统性缺失——为后续研究建议提供依据。

## 工作流

### Step 1: 检测未总结的论文

运行检测脚本，找出尚未被总结的研究笔记：

```bash
cd extract && uv run ../.claude/skills/summarize-research-notes/scripts/find_unsummarized.py eval_reports
```

脚本输出 JSON：
```json
{"unsummarized": ["1", "6", "10"], "total_with_notes": 10, "already_summarized": 7}
```

**如果 `unsummarized` 为空**：告诉用户"所有研究笔记都已总结，没有新论文需要处理"，结束。

### Step 2: 读取未总结论文的研究笔记

读取 `eval_reports/` 下 `unsummarized` 列表中的每篇 `.md` 文件。重点关注 `## 研究笔记` section。

### Step 3: 逐篇提取优缺点

对每篇论文，从研究笔记中提取具体的优点和缺点。不预设维度，用论文自己的语言。

每篇通常 2-4 个优点、3-5 个缺点。提取实际存在的内容，不编造。

### Step 4: 跨论文聚类

按语义相似度把优点/缺点归类。每个聚类包含：
- 标签（短中文短语）
- 一句话描述
- 涉及的论文 ID 列表

### Step 5: 生成总结文档

文件名：`summary-{id1}-{id2}-...-{idN}.md`（ID 排序，`-` 连接）

输出到 `extract/eval_reports/summary-{ids}.md`，结构如下：

```markdown
# 研究笔记总结：Paper {id1}, {id2}, ..., {idN}

> 生成时间：{date}
> 论文列表：{id1} — {title1}，{id2} — {title2}，...

## 一、各论文要点

### Paper {id}: {title}
**优点：**
- ...
**缺点：**
- ...

## 二、跨论文模式

### 优点模式
#### {标签}（{M}/{N} 篇）
{解释}
- Paper {id}: {表现}

### 缺点模式
#### {标签}（{M}/{N} 篇）
{解释}
- Paper {id}: {表现}

## 三、量化矩阵
| Paper | 模式1 | 模式2 | ... |
|-------|:-----:|:-----:|:---:|

## 四、关键发现
{2-3 段洞察}
```

如果 summary 文件已存在，提示用户是否覆盖。

### Step 6: 打标记

运行标记脚本，在已总结论文的 `## 研究笔记` 下方插入反向链接：

```bash
cd extract && uv run ../.claude/skills/summarize-research-notes/scripts/mark_summarized.py \
  --papers {id1},{id2},... --summary summary-{ids}.md --dir eval_reports
```

### Step 7: 告知用户

告诉用户：
1. 总结文件的位置
2. Top 3 最常见优点（按论文数）
3. Top 3 最常见缺点（按论文数）
4. 哪篇论文表现突出（特别好或特别差）

## 写作风格

- 文字说人话，不要学术八股
- 表格做量化，打勾打叉清晰
- 缺点分析要尖锐但有建设性
- 引用具体论文用 Paper {id} 格式

## 注意事项

- 一篇论文可以同时出现在不同维度的优点和缺点里
- 只出现 1 次的优点/缺点单独列出，标注"仅见于 Paper {id}"，不强行归类
- 频次统计是辅助，不为凑数字合并不同类项
- 没有研究笔记的论文跳过，在开头注明
```

- [ ] **Step 2: 验证 SKILL.md 格式**

确认 YAML frontmatter 正确，Markdown 渲染无误。

---

### Task 4: 端到端验证

- [ ] **Step 1: 模拟完整工作流**

用当前 10 篇 eval_reports 跑一次完整流程：

```bash
cd /Users/hand/project/LLM-Evaluate

# Step 1: 检测
uv run .claude/skills/summarize-research-notes/scripts/find_unsummarized.py extract/eval_reports
# 预期: 10 篇都在 unsummarized 中

# Step 2-5: 由 Claude 执行（读取、提取、聚类、写 summary）

# Step 6: 打标记
# (假设生成了 summary-1-6-10-13-15-18-58-80-81-83.md)
uv run .claude/skills/summarize-research-notes/scripts/mark_summarized.py \
  --papers 1,6,10,13,15,18,58,80,81,83 \
  --summary summary-1-6-10-13-15-18-58-80-81-83.md \
  --dir extract/eval_reports
```

- [ ] **Step 2: 验证幂等性**

再次运行检测脚本，确认所有论文都已标记：

```bash
uv run .claude/skills/summarize-research-notes/scripts/find_unsummarized.py extract/eval_reports
# 预期: unsummarized 为空
```

- [ ] **Step 3: 清理测试数据**

删除测试生成的 summary 文件和论文中的标记（恢复原状）：

```bash
# 删除 summary 文件
rm extract/eval_reports/summary-*.md

# 恢复论文（从 git）
git checkout extract/eval_reports/
```

---

### Task 5: 提交

- [ ] **Step 1: 提交所有变更**

```bash
git add .claude/skills/summarize-research-notes/ docs/specs/summarize-research-notes-design.md
git commit -m "feat: add batch management and idempotency to summarize-research-notes skill

- Add find_unsummarized.py script for detecting un-summarized papers
- Add mark_summarized.py script for adding reverse-link markers
- Update SKILL.md with three-step workflow
- Add design spec to docs/specs/"
```
