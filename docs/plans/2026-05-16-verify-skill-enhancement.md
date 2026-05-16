# Verify Skill 增强：判断值验证 + 全字段证据要求

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 消除模板证据，让每个字段都有原文证据，并用已验证的证据 + 字段定义自动判断值是否正确。

**整体流程：**
```
extract (evaluate.py)
    ↓ 生成 eval_reports/*.md + eval_results.csv
    ↓
verify skill
    ├─ Step 1: 脚本验证证据是否逐字存在 → EXACT / PARAPHRASED / FABRICATED / TEMPLATE
    ├─ Step 2: 修复证据 → FABRICATED/TEMPLATE 的回 PDF 找原文替换
    ├─ Step 3: 检验值是否正确 → 用已验证的证据 + 字段定义对照
    └─ Step 4: 修复 → 更新 Markdown + 同步 CSV
```

**Architecture:** 两层改动——(1) extract pipeline 的 prompt 和验证逻辑，确保 NO/N/A 字段也输出原文证据；(2) verify skill 的检测和修复逻辑，把 TEMPLATE 当缺陷处理，用证据+定义判定值正确性。

**Tech Stack:** Python 3.12, PyMuPDF (fitz), OpenAI API

---

## 问题根因

三处代码共同导致了模板证据：

| 文件 | 行 | 问题 |
|------|-----|------|
| `prompts.py` | 59 | prompt 明确告诉 LLM：NO 字段用模板 |
| `agent_loop.py` | 54 | `_verify_all_evidence` 跳过 NO/N/A 字段 |
| `verify_extraction.py` | 85-93 | TEMPLATE 被当作"安全"标签，不检查 |

---

## 文件变更清单

| 文件 | 操作 | 职责 |
|------|------|------|
| `extract/prompts.py:59` | 修改 | 删除 NO 字段模板指令，改为要求原文证据 |
| `extract/agent_loop.py:54` | 修改 | 删除 NO/N/A 跳过逻辑，全字段验证 |
| `.claude/skills/verify-eval-extraction/scripts/verify_extraction.py` | 重写 | 移除 TEMPLATE 安全状态，加判断值验证，改修复逻辑 |
| `.claude/skills/verify-eval-extraction/skill.md` | 重写 | 更新 workflow，加 Step 2.5 判断值验证 |

---

### Task 1: 修改 extract prompt — 删除 NO 字段模板指令

**Files:**
- Modify: `extract/prompts.py:59`

- [ ] **Step 1: 修改 `_build_output_format_section` 中的 NO 字段规则**

当前 `prompts.py:59`:
```python
- NO 字段的 evidence 严格使用模板: "No evidence of [具体方法/维度] found in the paper."，page 设为 null
```

改为：
```python
- 所有字段（包括 NO/N/A）的 evidence 都必须是论文原文的逐字引用。即使是判断为"不存在"的字段，也要引用论文中让你做出该判断的原文（如评估方法描述、参与者描述等）
- 仅当论文中确实完全没有相关内容时，才使用模板: "No evidence of [具体方法/维度] found in the paper."，page 设为 null
```

- [ ] **Step 2: 验证修改**

运行 `grep -n "No evidence" extract/prompts.py` 确认模板指令已更新。

- [ ] **Step 3: Commit**

```bash
git add extract/prompts.py
git commit -m "fix: require verbatim evidence for NO/N/A fields, not template"
```

---

### Task 2: 修改 extract 验证逻辑 — 全字段验证 + NO 字段负验证

**Files:**
- Modify: `extract/agent_loop.py:44-65`

核心改动：(1) 不再跳过 NO/N/A 字段；(2) 对 NO 字段做负验证——搜索 PDF 看是否真的没有相关内容。

- [ ] **Step 1: 修改 `_verify_all_evidence`**

当前 `agent_loop.py:54` 跳过 NO/N/A：
```python
if value.upper() in ("NO", "N/A") or not evidence.strip() or evidence.startswith("No evidence"):
    continue
```

改为全字段验证，NO 字段做负验证：
```python
def _verify_all_evidence(extracted: dict, index: PDFIndex) -> dict[str, dict]:
    """Verify evidence quotes against PDF. Returns {field: {"current": data, "error": detail}}."""
    failures = {}
    for field, data in extracted.items():
        if not isinstance(data, dict):
            continue
        value = data.get("value", "")
        evidence = data.get("evidence", "")
        page = data.get("page")

        if not evidence.strip():
            continue

        # 模板证据（旧数据兼容）：跳过验证，由 verify skill 后续处理
        if evidence.startswith("No evidence") and value.upper() in ("NO", "N/A"):
            continue

        # NO/N/A 字段负验证：搜索 PDF 看是否真的没有相关内容
        if value.upper() in ("NO", "N/A"):
            has_relevant, found_text = _check_negative_claim(field, evidence, index)
            if has_relevant:
                failures[field] = {
                    "current": data,
                    "error": f"Claimed NO but found relevant text: {found_text[:200]}",
                }
            continue

        # YES 字段正验证：确认证据原文存在
        if page is None:
            continue
        result = index.verify_quote(evidence, page)
        if result["matched"]:
            continue
        detail = result.get("detail", "")
        if "No similar text found" in detail:
            failures[field] = {"current": data, "error": detail}
    return failures
```

- [ ] **Step 2: 新增 `_check_negative_claim` 函数**

在 `agent_loop.py` 中添加 NO 字段负验证逻辑：

```python
# 字段 → 搜索关键词映射
NEGATIVE_FIELD_KEYWORDS = {
    "eval_human_experts": ["therapist", "clinician", "psychologist", "psychiatrist", "expert", "professional", "counselor", "practitioner"],
    "eval_lay_users": ["crowdwork", "mturk", "amazon mechanical", "prolific", "lay user", "naive participant"],
    "eval_user_study": ["user study", "user experiment", "participant interact", "interaction study"],
    "eval_llm_judge": ["gpt-4", "gpt-3", "claude", "llm-as-judge", "llm evaluator", "language model evaluat"],
    "eval_automatic": ["bleu", "rouge", "bertscore", "f1 score", "accuracy", "cosine similarity"],
    "dim_safety": ["safety", "harmful", "toxic", "bias", "ethical", "risk"],
    "dim_realism": ["realism", "naturalness", "human-like", "authentic"],
    "dim_consistency": ["consistency", "coherent", "stable across"],
    "dim_fidelity": ["fidelity", "adherence", "faithful", "aligned with"],
    "dim_utility": ["utility", "usefulness", "effective", "helpful"],
    "dim_human_learning": ["learning outcome", "knowledge gain", "skill improvement", "behavior change"],
    "dim_emotional_plausibility": ["empathy", "emotional", "affect", "sentiment"],
    "reliability_reported": ["kappa", "krippendorff", "icc", "inter-rater", "inter-annotator agreement"],
    "has_rubric": ["rubric", "scoring guide", "rating scale", "evaluation criteria", "scoring criteria"],
    "theory_grounding": ["cbt", "cognitive-behavioral", "motivational interview", "validated scale", "psychometric"],
    "has_longitudinal_eval": ["longitudinal", "follow-up", "multiple session", "over time"],
    "has_failure_analysis": ["failure case", "error analysis", "failure mode", "limitation"],
}


def _check_negative_claim(field: str, evidence: str, index: PDFIndex) -> tuple[bool, str]:
    """Check if a NO/N/A claim is correct by searching PDF for relevant keywords.
    Returns (has_relevant_evidence, found_text)."""
    keywords = NEGATIVE_FIELD_KEYWORDS.get(field, [])
    if not keywords:
        return False, ""

    full_text = index.get_full_text().lower()
    for kw in keywords:
        if kw.lower() in full_text:
            # 找到关键词，提取上下文
            idx = full_text.index(kw.lower())
            context = full_text[max(0, idx - 100):idx + 200]
            return True, context
    return False, ""
```

- [ ] **Step 3: 验证修改**

运行 `grep -n "def _verify_all_evidence\|def _check_negative_claim" extract/agent_loop.py` 确认两个函数都存在。

- [ ] **Step 4: Commit**

```bash
git add extract/agent_loop.py
git commit -m "feat: add negative verification for NO fields in extract pipeline"
```

---

### Task 3: 重写 verify_extraction.py — 移除 TEMPLATE 安全状态

**Files:**
- Rewrite: `.claude/skills/verify-eval-extraction/scripts/verify_extraction.py`

- [ ] **Step 1: 修改 `verify_evidence` 函数 — TEMPLATE 不再安全**

当前逻辑（line 85-93）把 TEMPLATE 当安全标签跳过。改为：TEMPLATE 也是一种缺陷，需要标记。

```python
def verify_evidence(
    evidence: str, norm_full: str, pages: dict[int, str], claimed_page: int | None
) -> dict:
    """Verify a single evidence claim. Returns verification result."""
    is_template = (
        evidence.startswith("No evidence of")
        or evidence.startswith("论文中未")
        or evidence.startswith("未发现")
        or evidence.startswith("未涉及")
    )

    if is_template:
        return {"quality": "TEMPLATE", "page_match": None, "detail": "Template text — needs real evidence from PDF"}

    # Handle ellipsis: split on "..." and verify each part independently
    parts = [p.strip() for p in evidence.split("...") if p.strip()]
    all_exact = True
    details = []
    page_found_on = None

    for part in parts:
        part_norm = normalize(part)
        if part_norm in norm_full:
            details.append(f'exact: "{_truncate(part, 40)}"')
        else:
            all_exact = False
            matched = _find_longest_partial(part_norm, norm_full)
            if matched:
                details.append(f'partial: "{_truncate(part, 30)}" → matched "{_truncate(matched, 40)}"')
            else:
                details.append(f'NOT FOUND: "{_truncate(part, 50)}"')

    # Page verification
    page_match = None
    if claimed_page is not None and all_exact:
        if claimed_page in pages:
            page_text = normalize(_clean_footnote_breaks(pages[claimed_page]))
            first_part_norm = normalize(parts[0]) if parts else ""
            if first_part_norm and first_part_norm in page_text:
                page_match = True
                page_found_on = claimed_page
            else:
                for pn, pt in pages.items():
                    if first_part_norm in normalize(_clean_footnote_breaks(pt)):
                        page_found_on = pn
                        break
                page_match = page_found_on == claimed_page
        else:
            page_match = False

    if all_exact:
        quality = "EXACT"
    elif any("partial:" in d for d in details):
        quality = "PARAPHRASED"
    else:
        quality = "FABRICATED"

    return {
        "quality": quality,
        "page_match": page_match,
        "page_found_on": page_found_on,
        "detail": "; ".join(details),
    }
```

- [ ] **Step 2: 修改 `compute_fixes` — 不再生成模板证据**

当前逻辑（line 323）把 FABRICATED NO/N/A 替换为模板。改为标记为需要搜索 PDF：

```python
def compute_fixes(result: dict) -> list[dict]:
    """Compute needed fixes for a single paper's verification result."""
    fixes = []
    for field_data in result.get("fields", []):
        field = field_data["field"]
        quality = field_data["quality"]
        claimed_page = field_data["claimed_page"]
        page_found_on = field_data.get("page_found_on")
        value = field_data["value"]

        # Fix page number: evidence is EXACT but on wrong page
        if quality == "EXACT" and claimed_page is not None and page_found_on is not None and claimed_page != page_found_on:
            fixes.append({
                "field": field,
                "type": "page_fix",
                "old_page": claimed_page,
                "new_page": page_found_on,
                "description": f"p.{claimed_page} → p.{page_found_on}",
            })

        # Mark TEMPLATE and FABRICATED fields for PDF search
        if quality in ("TEMPLATE", "FABRICATED"):
            fixes.append({
                "field": field,
                "type": "needs_pdf_search",
                "old_quality": quality,
                "value": value,
                "description": f"{quality} — need to search PDF for real evidence",
            })

    return fixes
```

- [ ] **Step 3: 修改 `apply_fixes` — 只处理页码修复，PDF 搜索留给 skill**

```python
def apply_fixes(paper_id: str, report_path: Path, fixes: list[dict]) -> None:
    """Apply fixes to a report file in-place. Only handles page fixes."""
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
    report_path.write_text(content, encoding="utf-8")
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/verify-eval-extraction/scripts/verify_extraction.py
git commit -m "refactor: remove TEMPLATE safety, mark all non-EXACT as needing PDF search"
```

---

### Task 4: 重写 skill.md — 加入判断值验证流程

**Files:**
- Rewrite: `.claude/skills/verify-eval-extraction/skill.md`

- [ ] **Step 1: 重写 skill.md**

新的 workflow：

```markdown
# Verify Eval Extraction Results

验证 evaluate.py 的提取结果。检查两件事：
1. **证据准确性**：每个 evidence 必须是 PDF 原文逐字引用（没有模板、没有编造）
2. **判断值正确性**：用已验证的证据 + 字段定义，判断 value 是否正确

## Workflow

### Step 1: Run verification script

```bash
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py {ids}
```

脚本输出 JSON，包含每个字段的证据质量（EXACT/PARAPHRASED/FABRICATED/TEMPLATE）。

### Step 2: Present evidence quality table

格式化脚本输出为表格：

```
## Verification: Paper {id} — {title}

### Evidence Quality

| Field | Value | Quality | Page Match | Issue |
|-------|-------|---------|------------|-------|
| eval_human_experts | YES | EXACT | ✅ p.5 | |
| eval_lay_users | NO | TEMPLATE | — | 需要从 PDF 找原文 |
| dim_consistency | YES | FABRICATED | — | 证据未在 PDF 中找到 |
```

### Step 3: AI 判断值验证

对每个字段，用已验证的证据 + 字段定义判断值是否正确：

**EXACT 字段**：证据已确认存在于 PDF → 读证据内容 + 字段定义 → 判定值对不对
- 例：`eval_human_experts: YES`，证据 "Two clinical psychologists evaluated..." → 符合 YES 定义（领域专家评估）→ CORRECT
- 例：`reliability_reported: Yes`，证据 "average agreement was 85%" → 不符合 Yes 定义（需要统计信度系数，百分比不算）→ WRONG → 应为 No

**PARAPHRASED 字段**：证据部分匹配 → 同上，但标注置信度较低

**FABRICATED 字段**：证据未找到 → 用 `fitz` 搜索 PDF 找相关原文 → 用找到的原文重新判定值

**TEMPLATE 字段**：声称"无证据" → 用 `fitz` 搜索 PDF 验证是否真的没有 →
- 确实没有 → 值正确，但证据需改为说明为什么没有（而非模板）
- 找到了 → 值可能错误，用找到的原文重新判定

输出判断值验证表：

```
### Judgment Verification

| Field | Value | Evidence Quality | Judgment | Fix |
|-------|-------|-----------------|----------|-----|
| eval_human_experts | YES | EXACT | CORRECT | — |
| reliability_reported | Yes | EXACT | WRONG → No | 证据是百分比一致，不是信度系数 |
| eval_lay_users | NO | TEMPLATE | NEEDS PDF SEARCH | — |
| dim_consistency | YES | FABRICATED | NEEDS PDF SEARCH | — |
```

### Step 4: Fix — 搜索 PDF + 修正

对 NEEDS PDF SEARCH 和 WRONG 的字段：

1. 用 `fitz` 搜索 PDF 相关页面，找到真实原文
2. 替换证据为真实原文
3. 如果值错了，修正值
4. 更新 Markdown 报告
5. 如果值变了，同步 `eval_results.csv`

```bash
# 修正后重新验证
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py {ids}
```

### Step 5: Summary

```
Paper {id}: {exact_count} EXACT, {para_count} PARAPHRASED, {fab_count} FABRICATED, {tpl_count} TEMPLATE
Judgment corrections: {count}
Evidence replacements: {count}
```

## 字段定义参考

（嵌入 schemas.py 中的 FIELD_DEFINITIONS 和 SINGLE_CHOICE_FIELDS）
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/verify-eval-extraction/skill.md
git commit -m "docs: rewrite verify skill with judgment value verification"
```

---

### Task 5: 端到端测试 — 用一篇论文验证完整流程

**Files:**
- Test: `extract/eval_reports/108.md` (已有数据，含 TEMPLATE 证据)

- [ ] **Step 1: 运行验证脚本**

```bash
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py 108
```

确认 TEMPLATE 字段被正确标记（不再是"安全跳过"）。

- [ ] **Step 2: 按 skill.md 流程走一遍**

对 Paper 108 执行完整验证流程：
- Step 2: 展示证据质量表
- Step 3: 对 EXACT 字段做判断值验证
- Step 4: 对 TEMPLATE 字段搜索 PDF 找原文
- 输出最终 summary

- [ ] **Step 3: 确认 CSV 同步**

如果判断值有变化，确认 `eval_results.csv` 已同步更新。

- [ ] **Step 4: Commit**

```bash
git add extract/eval_reports/108.md extract/eval_results.csv
git commit -m "fix: verify and fix paper 108 evidence and judgments"
```

---

## 自检清单

- [ ] `prompts.py` 不再要求 NO 字段用模板
- [ ] `agent_loop.py` 不再跳过 NO/N/A 字段的证据验证
- [ ] `agent_loop.py` 对 NO 字段做负验证（搜索 PDF 看是否真的没有）
- [ ] `verify_extraction.py` 把 TEMPLATE 当缺陷而非安全标签
- [ ] `skill.md` 包含判断值验证步骤（Step 3）
- [ ] 修复逻辑只做页码修正和标记 PDF 搜索，不再生成模板证据
- [ ] CSV 同步覆盖判断值修正
