---
name: verify-eval-extraction
description: Verify LLM-extracted evaluation methodology results against original PDFs. Use when the user asks to verify, validate, or check the quality of extraction results from evaluate.py — specifically whether evidence quotes are verbatim from the source papers and whether judgment values are correct. Also use when the user says "验证", "核对", "检查提取结果", "verify extraction", or references eval_reports/*.md quality.
---

# Verify Eval Extraction Results

验证 evaluate.py 的提取结果。检查两件事：

1. **证据准确性**：每个 evidence 必须是 PDF 原文逐字引用（没有模板、没有编造）
2. **判断值正确性**：用已验证的证据 + 字段定义，判断 value 是否正确

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

> ⚠️ **逐字引用铁律**
> 证据必须是 PDF 原文逐字引用。绝对不能自己写总结、改写、缩写。
> 如果你写出来的文字不是 PDF 里原封不动抄出来的，就是错的。
>
> ✅ 正确：`We recruited 7 mental health professionals with professional expertise.`
> ❌ 错误：`The paper uses human evaluation by mental health professionals.`
> （第二种是总结，不是原文，会被判为 FABRICATED）
>
> 使用 `--extract-evidence` 获取候选原文，从中选择，不要自己写。

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
