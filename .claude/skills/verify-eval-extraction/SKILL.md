---
name: verify-eval-extraction
description: Verify LLM-extracted evaluation methodology results against original PDFs. Use when the user asks to verify, validate, or check the quality of extraction results from evaluate.py — specifically whether evidence quotes are verbatim from the source papers and whether judgment values are correct. Also use when the user says "验证", "核对", "检查提取结果", "verify extraction", or references eval_reports/*.md quality.
---

# Verify Eval Extraction Results

验证 evaluate.py 的提取结果。检查两件事：

1. **证据准确性**：每个 evidence 必须是 PDF 原文逐字引用（没有模板、没有编造）
2. **判断值正确性**：用已验证的证据 + 字段定义，判断 value 是否正确

## Workflow

### Step 1: Run verification script

```bash
# Single paper
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py 1

# Multiple papers
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py 1 28 35

# All papers
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py --all
```

脚本输出 JSON，包含每个字段的证据质量标签。

### Step 2: Present evidence quality table

```
## Verification: Paper {id} — {title}

### Evidence Quality

| Field | Value | Quality | Page Match | Issue |
|-------|-------|---------|------------|-------|
| eval_human_experts | YES | EXACT | ✅ p.5 | |
| eval_lay_users | NO | TEMPLATE | — | 需要从 PDF 找原文 |
| dim_consistency | YES | PARAPHRASED | — | partial: "consistent and logical" but changed subject |
| dim_utility | YES | FABRICATED | — | 证据未在 PDF 中找到 |
```

Quality labels:
- **EXACT** — verbatim match found
- **PARAPHRASED** — partial match, content OK but not exact
- **FABRICATED** — quote not found in PDF at all
- **TEMPLATE** — 使用模板文本，需要从 PDF 找真实原文（这是缺陷，不是安全状态）

### Step 3: AI judgment value verification

对每个字段，用已验证的证据 + 字段定义判断值是否正确。

**EXACT 字段**：证据已确认存在于 PDF → 读证据内容 + 字段定义 → 判定值对不对
- 例：`eval_human_experts: YES`，证据 "Two clinical psychologists evaluated..." → 符合 YES 定义（领域专家评估）→ CORRECT
- 例：`reliability_reported: Yes`，证据 "average agreement was 85%" → 不符合 Yes 定义（需要统计信度系数，百分比不算）→ WRONG → 应为 No

**PARAPHRASED 字段**：证据部分匹配 → 同上，但标注置信度较低

**FABRICATED 字段**：证据未找到 → 用 `fitz` 搜索 PDF 找相关原文 → 用找到的原文重新判定值

**TEMPLATE 字段**：声称"无证据" → 用 `fitz` 搜索 PDF 验证是否真的没有 →
- 确实没有 → 值正确，但证据需改为说明为什么没有（而非模板）
- 找到了 → 值可能错误，用找到的原文重新判定

搜索 PDF 的方法：

```bash
cd extract && uv run python3 -c "
import fitz
doc = fitz.open('paper/{id}.pdf')
for i, page in enumerate(doc):
    text = page.get_text().lower()
    if '{keyword}' in text:
        print(f'FOUND on page {i+1}:')
        print(page.get_text()[:500])
        break
else:
    print('NOT FOUND')
"
```

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

### Step 4: Fix — search PDF + correct

对 NEEDS PDF SEARCH 和 WRONG 的字段：

1. 用 `fitz` 搜索 PDF 相关页面，找到真实原文
2. 替换证据为真实原文
3. 如果值错了，修正值
4. 更新 Markdown 报告（`eval_reports/{id}.md`）
5. 如果值变了，同步 `eval_results.csv`（见 Step 4c）

然后重新运行验证脚本确认修复干净：

```bash
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py {ids}
```

### Step 4b: Handle false positives

脚本标记 FABRICATED 的字段，可能是误报（PDF 双栏排版、连字符断行、附录页码不同）。用 Step 3 的 `fitz` 搜索确认：

- **误报**：证据实际存在于 PDF → 报告 "脚本误报，证据在 p.X"
- **真编造**：证据确实不存在 → Step 4 已处理

### Step 4c: Sync CSV after value changes

如果判断值变了，必须同步 `eval_results.csv`：

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

CSV 列名格式：`Reliability_Reported`, `Eval_LLM_Judge`, `Theory_Grounding` 等。查表头确认。

### Step 5: Summary

```
Paper {id}: {exact_count} EXACT, {para_count} PARAPHRASED, {fab_count} FABRICATED, {tpl_count} TEMPLATE
Judgment corrections: {count}
Evidence replacements: {count}
```

Batch verification:
```
## Batch Summary

| Paper | EXACT | PARAPHRASED | FABRICATED | TEMPLATE | Page Wrong | Judgment Fix | Fixed |
|-------|-------|-------------|------------|----------|------------|--------------|-------|
| 1     | 14    | 3           | 0          | 0        | 1          | 1            | ✅    |
| 28    | 16    | 1           | 0          | 0        | 0          | 0            | —     |
```

## Field Definitions Reference

### BOOL fields (YES/NO)

| Field | YES when | NO when |
|-------|----------|---------|
| eval_human_experts | 治疗师、临床医生、领域专家、受过训练的标注员进行评估 | 众包工人、无专业知识的学生、LLM 评估 |
| eval_lay_users | MTurk/Prolific 众包工人、普通用户 | 领域专家、受过训练的标注员 |
| eval_user_study | 用户与系统发生交互，有明确任务/协议/实验设计 | 简单打分任务（无交互）、静态输出评估 |
| eval_llm_judge | 使用 GPT-4/Claude 等进行打分、比较、排序 | 提取向量相似度、特征提取、计算指标 |
| eval_automatic | BLEU, ROUGE, Accuracy, F1 等算法/数学计算 | LLM 打分、人类打分 |
| has_rubric | 有明确的评分量表、rubric、评分指南 | 仅说"让标注员打分"但无标准 |
| llm_judge_validated | LLM 打分与人类打分做了相关性/一致性分析 | 未使用 LLM judge，或使用了但未验证 |
| uses_standard_metrics | 使用 BLEU、ROUGE、BERTScore 等公认指标 | 仅用自创指标且未与标准指标对比 |

### Single-choice fields

| Field | Options | Key distinction |
|-------|---------|-----------------|
| reliability_reported | Yes / No / N/A | Yes = 报告了统计信度系数（kappa/alpha/ICC），百分比一致不算 |
| coding_options | Yes / No / N/A | Yes = 明确报告了评估者间一致性 |
| theory_grounding | Strong / Weak / None | Strong = 明确使用公认理论定义或测量 |
| theory_operationalized | Strong / Partial / Mentioned / None | Strong = 评估标准明确源于理论 |
| interaction_level | Single-turn / Short Multi-turn / Extended Dialogue / Longitudinal | Single-turn = 一次评估一个回复无历史 |
| prompt_disclosure | Full / Partial / No | Full = 清晰提供了所有必要提示词 |
| behavior_eval_depth | Dynamic / Pattern-level / Static / None | Dynamic = 分析行为如何随轮次变化 |

## Tips

- **证据必须是原文，没有例外。** TEMPLATE 不是安全状态，是需要修复的缺陷。
- **Always sync `eval_results.csv` when judgment values change.** Markdown + CSV 必须同时更新。
- 脚本处理 PDF 连字符（`psy-\nchological` → `psychological`）和弯引号归一化。
- 用 `...` 连接的分段证据，每段独立验证。
- 43 个结构化字段，7 个类别。重点关注信度、理论、交互层级等边界模糊字段。
