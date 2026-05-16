# verify-eval-extraction Skill 优化实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复验证脚本的假阳性问题，新增自动证据提取功能，优化 Skill 工作流以避免 TEMPLATE → FABRICATED 死循环。

**Architecture:** 两处改动——`pdf_index.py` 的归一化函数增加换行处理；`verify_extraction.py` 新增 `--extract-evidence` 命令和扩展 `--fix` 能力；`SKILL.md` 增加逐字引用铁律和简化工作流。

**Tech Stack:** Python 3.12, PyMuPDF (fitz), uv

---

### Task 1: 修复 pdf_index.py 归一化

**Files:**
- Modify: `extract/pdf_index.py:40-45`

- [ ] **Step 1: 在 `_normalize_whitespace` 中添加换行符处理**

当前代码（line 40-45）：
```python
def _normalize_whitespace(s: str) -> str:
    s = s.replace('’', "'").replace('‘', "'")  # 弯引号 → 直引号
    s = s.replace("“", '"').replace("”", '"')    # 弯双引号 → 直双引号
    s = re.sub(r'-\s+', '', s)  # 移除 PDF 行尾连字符
    s = s.replace('-', '')       # 移除所有剩余连字符
    return re.sub(r'\s+', ' ', s.strip().lower())
```

改为：
```python
def _normalize_whitespace(s: str) -> str:
    s = s.replace('’', "'").replace('‘', "'")  # 弯引号 → 直引号
    s = s.replace("“", '"').replace("”", '"')    # 弯双引号 → 直双引号
    s = re.sub(r'-\s+', '', s)  # 移除 PDF 行尾连字符
    s = s.replace('-', '')       # 移除所有剩余连字符
    s = re.sub(r'\n', ' ', s)    # 换行符 → 空格（修复跨行匹配问题）
    return re.sub(r'\s+', ' ', s.strip().lower())
```

- [ ] **Step 2: 验证修复效果**

```bash
cd extract && uv run python3 -c "
from pdf_index import _normalize_whitespace as normalize
# 测试：PDF 中的 'excellent\nperformance' 应该能匹配 'excellent performance'
assert 'excellent performance' == normalize('excellent\nperformance')
# 测试：原有功能不变
assert 'psychological' == normalize('psychother-\napist')  # 连字符断行
assert "it's" == normalize(\"it's\")  # 弯引号
print('All normalization tests pass')
"
```

Expected: `All normalization tests pass`

- [ ] **Step 3: Commit**

```bash
git add extract/pdf_index.py
git commit -m "fix: handle cross-line whitespace in normalization"
```

---

### Task 2: 新增 --extract-evidence 功能

**Files:**
- Modify: `extract/.claude/skills/verify-eval-extraction/scripts/verify_extraction.py`

- [ ] **Step 1: 添加字段关键词映射常量**

在 `verify_extraction.py` 的 imports 之后（约 line 33）添加：

```python
# 字段 → 搜索关键词映射，用于 --extract-evidence 从 PDF 提取候选证据
FIELD_KEYWORDS = {
    "eval_human_experts": ["professional", "expert", "clinician", "therapist", "psychologist", "psychiatrist", "annotator", "rater"],
    "eval_lay_users": ["volunteer", "participant", "mturk", "prolific", "crowd", "recruit", "user study"],
    "eval_user_study": ["interact", "session", "participant", "dialogue", "conversation", "task", "protocol"],
    "eval_llm_judge": ["gpt", "claude", "llm", "language model", "automatic", "score", "judge", "evaluat"],
    "eval_automatic": ["bleu", "rouge", "bertscore", "meteor", "f1", "accuracy", "precision", "recall", "metric"],
    "dim_realism": ["realism", "realistic", "natural", "human-like", "authentic", "plausible"],
    "dim_consistency": ["consist", "coherent", "stable", "maintain"],
    "dim_fidelity": ["fidelity", "accurate", "faithful", "adhere", "comply", "structure"],
    "dim_utility": ["useful", "helpful", "effective", "applicab", "beneficial", "practical"],
    "dim_human_learning": ["learn", "skill", "improve", "progress", "outcome", "training", "educat"],
    "dim_emotional_plausibility": ["emotion", "empathy", "affect", "sentiment", "mood", "feeling"],
    "dim_safety": ["safety", "harm", "toxic", "risk", "suicid", "crisis", "confidential"],
    "has_rubric": ["rubric", "scale", "criteria", "scoring", "rating", "likert", "criterion"],
    "reliability_reported": ["kappa", "alpha", "icc", "inter-rater", "inter-annotator", "agreement", "cohen", "fleiss"],
    "coding_options": ["inter-rater", "inter-annotator", "agreement", "cohen", "kappa", "iaa"],
    "theory_grounding": ["theory", "validated", "psychometric", "cbt", "clinical", "established", "framework"],
    "theory_operationalized": ["operationaliz", "measure", "assess", "metric", "scale", "instrument"],
    "interaction_level": ["turn", "round", "dialogue", "session", "multi-turn", "single-turn", "longitudinal"],
    "prompt_disclosure": ["prompt", "template", "appendix", "supplementary", "instruction"],
    "llm_judge_validated": ["correlat", "agreement", "pearson", "spearman", "validated", "human judgment"],
    "uses_standard_metrics": ["bleu", "rouge", "bertscore", "meteor", "standard", "established"],
    "metric_interpretable": ["interpret", "explain", "meaning", "coherence", "dimension"],
    "comparable_to_prior_work": ["baseline", "compar", "prior", "previous", "state-of-the-art", "sota"],
    "has_longitudinal_eval": ["longitudinal", "follow-up", "multiple session", "long-term", "over time"],
    "has_robustness_testing": ["robust", "adversar", "ablation", "sensitivity", "vary"],
    "has_failure_analysis": ["failure", "error", "limitation", "weakness", "flag", "incorrect"],
    "sim_behavior_realistic": ["realistic", "authentic", "simulation", "behavior", "real"],
    "dataset_available": ["available", "release", "public", "github", "hugging", "code", "data"],
    "clinical_theory": ["cbt", "dbt", "cognitive", "behavioral", "therapy", "clinical", "psychodynamic"],
    "focus_type": ["framework", "evaluation", "benchmark", "dataset", "model", "system"],
    "simulation_target": ["simulate", "agent", "patient", "therapist", "client", "persona"],
    "persona_model_depth": ["persona", "character", "profile", "trait", "dynamic", "static"],
    "uses_dynamic_state": ["dynamic", "state", "memory", "context", "temporal", "history"],
    "behavior_eval_depth": ["behavior", "dynamic", "pattern", "static", "change", "evolv"],
    "intervention_sensitivity": ["ablation", "intervention", "sensitivity", "component", "removal"],
    "raw_eval_metrics": ["metric", "score", "measure", "evaluation", "rating"],
    "temporal_modeling_details": ["temporal", "dynamic", "state", "memory", "iteration", "round"],
    "agreement_method": ["kappa", "alpha", "icc", "cohen", "fleiss", "agreement"],
    "sim_behavior_realistic": ["realistic", "simulation", "behavior", "authentic"],
}
```

- [ ] **Step 2: 实现 `extract_evidence_candidates` 函数**

在 `compute_fixes` 函数之前添加：

```python
def extract_evidence_candidates(pages: dict[int, str], field: str, value: str, evidence: str, top_n: int = 10) -> list[dict]:
    """从 PDF 中提取与字段相关的候选 verbatim 原文片段。"""
    keywords = FIELD_KEYWORDS.get(field, [])
    if not keywords:
        return []

    # 从 evidence 中提取额外关键词（去掉模板前缀）
    extra_kws = []
    if evidence.startswith("No evidence of") or evidence.startswith("论文中未") or evidence.startswith("未发现"):
        # TEMPLATE: 从 evidence 中提取有意义的词
        cleaned = re.sub(r'^(No evidence of |论文中未[^，]*，|未发现[^。]*。|未涉及[^。]*。)', '', evidence)
        extra_kws = [w for w in cleaned.split() if len(w) > 3][:5]
    else:
        # FABRICATED: 从 evidence 中提取名词短语
        words = evidence.split()
        extra_kws = [w for w in words if len(w) > 4 and w[0].isupper()][:5]

    all_keywords = keywords + extra_kws

    # 按句子分割 PDF 全文，计算每个句子的相关度
    candidates = []
    for pn, page_text in pages.items():
        # 按句号、感叹号、问号、换行分割
        sentences = re.split(r'(?<=[.!?])\s+|\n', page_text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 500:
                continue
            sentence_lower = sentence.lower()
            # 计算关键词命中数
            hits = sum(1 for kw in all_keywords if kw.lower() in sentence_lower)
            if hits >= 1:
                candidates.append({
                    "page": pn,
                    "text": sentence[:300],
                    "relevance": hits,
                })

    # 按相关度降序排序，去重，返回 top_n
    candidates.sort(key=lambda x: x["relevance"], reverse=True)
    seen = set()
    unique = []
    for c in candidates:
        key = c["text"][:80]
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique[:top_n]
```

- [ ] **Step 3: 验证函数可运行**

```bash
cd extract && uv run python3 -c "
import sys; sys.path.insert(0, '.')
sys.path.insert(0, str(__import__('pathlib').Path('../.claude/skills/verify-eval-extraction/scripts')))
from verify_extraction import extract_evidence_candidates, extract_pdf_pages
from pathlib import Path
pages = extract_pdf_pages(Path('paper/102.pdf'))
candidates = extract_evidence_candidates(pages, 'eval_llm_judge', 'NO', 'No evidence of using LLM as judge', top_n=3)
for c in candidates:
    print(f'p.{c[\"page\"]} (relevance={c[\"relevance\"]}): {c[\"text\"][:100]}...')
"
```

Expected: 输出 3 个包含 "gpt"/"llm"/"evaluat" 等关键词的句子

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/verify-eval-extraction/scripts/verify_extraction.py
git commit -m "feat: add extract_evidence_candidates for PDF evidence retrieval"
```

---

### Task 3: 添加 --extract-evidence 命令行支持

**Files:**
- Modify: `extract/.claude/skills/verify-eval-extraction/scripts/verify_extraction.py:343-406`

- [ ] **Step 1: 在 main() 中添加 --extract-evidence 参数处理**

修改 `main()` 函数：

```python
def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: verify_extraction.py <id> [<id> ...] | --all [--fix] [--extract-evidence]")
        sys.exit(1)

    do_fix = "--fix" in args
    do_extract = "--extract-evidence" in args
    args = [a for a in args if a not in ("--fix", "--extract-evidence")]

    if not args:
        print("Usage: verify_extraction.py <id> [<id> ...] | --all [--fix] [--extract-evidence]")
        sys.exit(1)

    if args[0] == "--all":
        ids = sorted(
            p.stem for p in REPORTS_DIR.glob("*.md") if p.stem.isdigit()
        )
    else:
        ids = args

    all_results = []
    all_fixes = {}
    all_extractions = {}
    for paper_id in ids:
        result = verify_paper(paper_id)
        if result:
            all_results.append(result)
            if do_fix:
                report_path = REPORTS_DIR / f"{paper_id}.md"
                if report_path.exists() and "fields" in result:
                    fixes = compute_fixes(result)
                    if fixes:
                        apply_fixes(paper_id, report_path, fixes)
                        all_fixes[paper_id] = fixes
            if do_extract and "fields" in result:
                pdf_path = PAPER_DIR / f"{paper_id}.pdf"
                if pdf_path.exists():
                    pages = extract_pdf_pages(pdf_path)
                    extractions = []
                    for field_data in result["fields"]:
                        if field_data["quality"] in ("TEMPLATE", "FABRICATED"):
                            candidates = extract_evidence_candidates(
                                pages, field_data["field"], field_data["value"],
                                field_data.get("detail", ""), top_n=10
                            )
                            if candidates:
                                extractions.append({
                                    "field": field_data["field"],
                                    "value": field_data["value"],
                                    "quality": field_data["quality"],
                                    "candidates": candidates,
                                })
                    if extractions:
                        all_extractions[paper_id] = extractions

    output = {
        "papers": all_results,
        "batch_summary": {
            "total_papers": len(all_results),
            "total_fields": sum(
                sum(1 for _ in p.get("fields", [])) for p in all_results
            ),
            "quality_counts": {
                "EXACT": sum(p["summary"]["EXACT"] for p in all_results if "summary" in p),
                "PARAPHRASED": sum(
                    p["summary"]["PARAPHRASED"] for p in all_results if "summary" in p
                ),
                "FABRICATED": sum(
                    p["summary"]["FABRICATED"] for p in all_results if "summary" in p
                ),
                "TEMPLATE": sum(
                    p["summary"]["TEMPLATE"] for p in all_results if "summary" in p
                ),
            },
        },
    }

    if do_fix:
        output["fixes_applied"] = all_fixes
    if do_extract:
        output["evidence_candidates"] = all_extractions

    print(json.dumps(output, ensure_ascii=False, indent=2))
```

- [ ] **Step 2: 测试 --extract-evidence**

```bash
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py 102 --extract-evidence 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
candidates = data.get('evidence_candidates', {}).get('102', [])
print(f'Found {len(candidates)} fields with candidates')
for c in candidates[:3]:
    print(f'  {c[\"field\"]} ({c[\"quality\"]}): {len(c[\"candidates\"])} candidates')
    if c['candidates']:
        print(f'    Top: p.{c[\"candidates\"][0][\"page\"]} ({c[\"candidates\"][0][\"relevance\"]}) {c[\"candidates\"][0][\"text\"][:80]}...')
"
```

Expected: 输出类似 `Found 25 fields with candidates`，每个字段有候选

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/verify-eval-extraction/scripts/verify_extraction.py
git commit -m "feat: add --extract-evidence command for PDF evidence retrieval"
```

---

### Task 4: 扩展 --fix 支持 TEMPLATE 自动修复

**Files:**
- Modify: `extract/.claude/skills/verify-eval-extraction/scripts/verify_extraction.py:324-340`

- [ ] **Step 1: 修改 `apply_fixes` 支持 template_fix**

```python
def apply_fixes(paper_id: str, report_path: Path, fixes: list[dict]) -> None:
    """Apply fixes to a report file in-place."""
    content = report_path.read_text(encoding="utf-8")
    for fix in fixes:
        if fix["type"] == "page_fix":
            lines = content.split("\n")
            new_lines = []
            for line in lines:
                if f"### {fix['field']}:" in line:
                    new_lines.append(line)
                elif f"**Evidence** (p.{fix['old_page']}):" in line:
                    line = line.replace(f"(p.{fix['old_page']})", f"(p.{fix['new_page']})")
                    new_lines.append(line)
                else:
                    new_lines.append(line)
            content = "\n".join(new_lines)
        elif fix["type"] == "template_fix":
            # 替换 TEMPLATE evidence 为最佳候选
            lines = content.split("\n")
            new_lines = []
            in_target_field = False
            for line in lines:
                if f"### {fix['field']}:" in line:
                    in_target_field = True
                    new_lines.append(line)
                elif in_target_field and line.startswith("**Evidence**"):
                    # 替换 evidence 行
                    new_evidence = fix["new_evidence"]
                    new_lines.append(f"**Evidence** {new_evidence} [AUTO-FIXED]")
                    in_target_field = False
                elif line.startswith("### ") and in_target_field:
                    in_target_field = False
                    new_lines.append(line)
                else:
                    new_lines.append(line)
            content = "\n".join(new_lines)
    report_path.write_text(content, encoding="utf-8")
```

- [ ] **Step 2: 修改 `compute_fixes` 为 TEMPLATE 字段生成 template_fix**

在 `compute_fixes` 中，对 TEMPLATE 字段添加 template_fix 逻辑：

```python
def compute_fixes(result: dict, pages: dict[int, str] | None = None) -> list[dict]:
    """Compute needed fixes for a single paper's verification result."""
    fixes = []
    for field_data in result.get("fields", []):
        field = field_data["field"]
        quality = field_data["quality"]
        claimed_page = field_data["claimed_page"]
        page_found_on = field_data.get("page_found_on")
        value = field_data["value"]

        # Fix page number
        if quality == "EXACT" and claimed_page is not None and page_found_on is not None and claimed_page != page_found_on:
            fixes.append({
                "field": field,
                "type": "page_fix",
                "old_page": claimed_page,
                "new_page": page_found_on,
                "description": f"p.{claimed_page} → p.{page_found_on}",
            })

        # Auto-fix TEMPLATE: extract best candidate from PDF
        if quality == "TEMPLATE" and pages is not None:
            candidates = extract_evidence_candidates(pages, field, value, "", top_n=10)
            if candidates:
                # 用相关度最高的候选构建新 evidence
                best = candidates[0]
                new_evidence = f"(p.{best['page']}): {best['text']}"
                fixes.append({
                    "field": field,
                    "type": "template_fix",
                    "new_evidence": new_evidence,
                    "description": f"TEMPLATE → auto-fix with best candidate (p.{best['page']})",
                })

        # Mark FABRICATED for PDF search (no auto-fix)
        if quality == "FABRICATED":
            fixes.append({
                "field": field,
                "type": "needs_pdf_search",
                "old_quality": quality,
                "value": value,
                "description": f"FABRICATED — need to search PDF for real evidence",
            })

    return fixes
```

- [ ] **Step 3: 修改 main() 中 --fix 的调用，传入 pages**

```python
# 在 main() 的 do_fix 块中：
if do_fix:
    report_path = REPORTS_DIR / f"{paper_id}.md"
    if report_path.exists() and "fields" in result:
        pdf_path = PAPER_DIR / f"{paper_id}.pdf"
        pages_for_fix = extract_pdf_pages(pdf_path) if pdf_path.exists() else None
        fixes = compute_fixes(result, pages=pages_for_fix)
        if fixes:
            apply_fixes(paper_id, report_path, fixes)
            all_fixes[paper_id] = fixes
```

- [ ] **Step 4: 测试 --fix 对 TEMPLATE 的修复效果**

```bash
# 备份一份报告用于测试
cp extract/eval_reports/106.md /tmp/106_backup.md

# 运行 --fix
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py 106 --fix 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
fixes = data.get('fixes_applied', {}).get('106', [])
for f in fixes:
    print(f'{f[\"type\"]}: {f[\"field\"]} — {f[\"description\"]}')
"

# 检查修复后的报告
grep -A 2 "AUTO-FIXED" extract/eval_reports/106.md | head -20

# 恢复
cp /tmp/106_backup.md extract/eval_reports/106.md
```

Expected: TEMPLATE 字段的 evidence 行被替换为 PDF 候选，标记 `[AUTO-FIXED]`

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/verify-eval-extraction/scripts/verify_extraction.py
git commit -m "feat: extend --fix to auto-replace TEMPLATE evidence from PDF"
```

---

### Task 5: 更新 SKILL.md — 添加铁律和简化工作流

**Files:**
- Modify: `.claude/skills/verify-eval-extraction/SKILL.md`

- [ ] **Step 1: 在 Step 4 前添加逐字引用铁律**

在 `### Step 4: Fix` 之前插入：

```markdown
> ⚠️ **逐字引用铁律**
> 证据必须是 PDF 原文逐字引用。绝对不能自己写总结、改写、缩写。
> 如果你写出来的文字不是 PDF 里原封不动抄出来的，就是错的。
>
> ✅ 正确：`We recruited 7 mental health professionals with professional expertise.`
> ❌ 错误：`The paper uses human evaluation by mental health professionals.`
> （第二种是总结，不是原文，会被判为 FABRICATED）
>
> 使用 `--extract-evidence` 获取候选原文，从中选择，不要自己写。
```

- [ ] **Step 2: 简化工作流步骤**

将当前的 Step 1-5 重构为更清晰的优先级流程。替换从 `## Workflow` 到 `## Field Definitions Reference` 之间的内容：

```markdown
## Workflow

### Step 1: 跑脚本

```bash
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py {ids}
```

脚本输出 JSON，包含每个字段的证据质量标签（EXACT / PARAPHRASED / FABRICATED / TEMPLATE）。

### Step 2: 按优先级处理

看结果，按优先级分类处理：

| 质量标签 | 优先级 | 处理方式 |
|----------|--------|----------|
| EXACT | 跳过 | 证据已确认 |
| PARAPHRASED | 低 | 内容 OK，可接受 |
| TEMPLATE | **最高** | 必须修复 → Step 3a |
| FABRICATED | 高 | 先检查假阳性 → Step 3b |

### Step 3a: 修复 TEMPLATE

用 `--extract-evidence` 获取候选原文：

```bash
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py {id} --extract-evidence
```

从候选中选择 verbatim 文本，替换 evidence。**逐字引用！不要总结！**

### Step 3b: 处理 FABRICATED

1. 先检查是否假阳性（归一化问题）→ 重新跑脚本确认
2. 不是假阳性？→ 用 `--extract-evidence` 获取候选，选择 verbatim 文本替换
3. 值可能错了？→ Step 4

### Step 4: 判断值验证

对每个字段，用已验证的证据 + 字段定义判断值是否正确。

- EXACT 字段：读证据内容 + 字段定义 → 判定值对不对
- PARAPHRASED 字段：同上，置信度较低
- FABRICATED / TEMPLATE 字段：用修复后的证据重新判定

如果值错了，修正值 + 同步 CSV：

```bash
cd extract && uv run python3 -c "
import csv
rows = []
with open('eval_results.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        if row['Paper_ID'] == '{id}':
            row['{CSV_Column_Name}'] = '{new_value}'
        rows.append(row)
with open('eval_results.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
"
```

### Step 5: 重新跑脚本确认

```bash
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py {ids}
```

确认 TEMPLATE = 0，FABRICATED 尽可能低。

### 证据修复示例

#### ✅ 正确做法（TEMPLATE → EXACT）

原始 evidence：
> **Evidence** (N/A): No evidence of using LLM as judge for evaluation found in the paper.

用 `--extract-evidence` 获取候选，选择 PDF 原文：
> p.6: To comprehensively evaluate the model's performance...we adopted a series of automatic evaluation metrics.
> p.7: Our evaluation team consisted of four senior psychology students and an experienced psychotherapist.

修复后（逐字引用）：
> **Evidence** (p.6-7): To comprehensively evaluate the model's performance...we adopted a series of automatic evaluation metrics. Our evaluation team consisted of four senior psychology students and an experienced psychotherapist.

#### ❌ 错误做法（TEMPLATE → FABRICATED）

修复后（AI 总结，不是原文）：
> **Evidence** (p.6-7): The paper uses automatic metrics and human expert evaluation, with no LLM judge employed.
> ↑ 这是 AI 总结的，不是 PDF 原文，会被判为 FABRICATED
```

- [ ] **Step 3: 验证 SKILL.md 格式正确**

```bash
# 检查 markdown 格式
head -50 .claude/skills/verify-eval-extraction/SKILL.md
# 确认无语法错误
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/verify-eval-extraction/SKILL.md
git commit -m "docs: add verbatim rule and simplify verify workflow in SKILL.md"
```

---

### Task 6: 端到端测试

- [ ] **Step 1: 测试归一化修复效果**

```bash
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py 104 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
for p in data['papers']:
    fab = [f for f in p['fields'] if f['quality'] == 'FABRICATED']
    tpl = [f for f in p['fields'] if f['quality'] == 'TEMPLATE']
    print(f'Paper {p[\"id\"]}: FABRICATED={len(fab)}, TEMPLATE={len(tpl)}')
    for f in fab:
        print(f'  FABRICATED: {f[\"field\"]} — {f[\"detail\"][:100]}')
"
```

Expected: Paper 104 的 FABRICATED 数量应该减少（归一化假阳性修复）

- [ ] **Step 2: 测试 --extract-evidence 输出质量**

```bash
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py 102 --extract-evidence 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
candidates = data.get('evidence_candidates', {}).get('102', [])
print(f'Total fields with candidates: {len(candidates)}')
for c in candidates[:5]:
    print(f'  {c[\"field\"]} ({c[\"quality\"]}): {len(c[\"candidates\"])} candidates')
    if c['candidates']:
        best = c['candidates'][0]
        print(f'    Best: p.{best[\"page\"]} (rel={best[\"relevance\"]}): {best[\"text\"][:80]}...')
"
```

Expected: 每个 TEMPLATE/FABRICATED 字段有 1-10 个候选，top 候选包含相关内容

- [ ] **Step 3: 测试 --fix 对 TEMPLATE 的自动修复**

```bash
# 用 Paper 106 测试（只有 2 个 TEMPLATE 字段，风险低）
cp extract/eval_reports/106.md /tmp/106_backup.md

cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py 106 --fix 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
fixes = data.get('fixes_applied', {}).get('106', [])
for f in fixes:
    print(f'{f[\"type\"]}: {f[\"field\"]} — {f[\"description\"]}')
"

# 检查修复后的报告
echo '--- AUTO-FIXED evidence ---'
grep -B 1 "AUTO-FIXED" extract/eval_reports/106.md

# 恢复
cp /tmp/106_backup.md extract/eval_reports/106.md
```

Expected: 2 个 TEMPLATE 字段被自动修复，evidence 替换为 PDF 候选

- [ ] **Step 4: 完整验证 Paper 102（最差质量论文）**

```bash
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py 102 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
for p in data['papers']:
    s = p['summary']
    print(f'Paper {p[\"id\"]}: EXACT={s[\"EXACT\"]}, PARAPHRASED={s[\"PARAPHRASED\"]}, FABRICATED={s[\"FABRICATED\"]}, TEMPLATE={s[\"TEMPLATE\"]}')
"
```

Expected: TEMPLATE = 0（归一化修复后），FABRICATED 应该比之前减少

- [ ] **Step 5: 最终 Commit**

```bash
git add -A
git commit -m "feat: verify-eval-extraction skill optimization complete"
```
