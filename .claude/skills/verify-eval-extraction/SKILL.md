---
name: verify-eval-extraction
description: Verify LLM-extracted evaluation methodology results against original PDFs. Use when the user asks to verify, validate, or check the quality of extraction results from evaluate.py — specifically whether evidence quotes are verbatim from the source papers and whether judgment values are correct. Also use when the user says "验证", "核对", "检查提取结果", "verify extraction", or references eval_reports/*.md quality.
---

# Verify Eval Extraction Results

验证 evaluate.py 的提取结果。检查两件事：

1. **证据准确性**：每个 evidence 必须是 PDF 原文逐字引用（没有模板、没有编造）
2. **判断值正确性**：用已验证的证据 + 字段定义，判断 value 是否正确

## How Verification Works

验证脚本的检查逻辑（理解这个才能写出通过的证据）：

```
evidence = "段落A ... 段落B ... 段落C"
                        ↓ split on "..."
parts = ["段落A", "段落B", "段落C"]
                        ↓ 每段独立检查
每个 part 是否是 PDF 全文（所有页拼接）的子串？
```

- **`...` 是分隔符**：用 `...` 分隔的每段独立验证
- **子串匹配**：每段必须是归一化后 PDF 全文的连续子串
- **不能跨段拼接**：如果 PDF 中有 "A 中间文字 B"，你不能写 "A B"（会判 FABRICATED），必须写 "A ... B"
- **TEMPLATE 判定**：evidence 以 "No evidence of"、"论文中未"、"未发现"、"未涉及" 开头 → 直接判 TEMPLATE

## Workflow

### Step 1: 跑脚本

```bash
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py {ids}
```

脚本输出 JSON，包含每个字段的证据质量标签（EXACT / PARAPHRASED / FABRICATED / TEMPLATE）。

### Step 2: 按优先级处理

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

> ⚠️ **只改 evidence，不改 confidence**
> 修复 TEMPLATE/FABRICATED 时，只替换证据文本。confidence 反映的是判断值的置信度，不是证据质量。除非你在 Step 4 中改变了判断值，否则不要动 confidence。

### Step 3b: 处理 FABRICATED

1. 先检查是否假阳性（归一化问题）→ 重新跑脚本确认
2. 不是假阳性？→ 用下面的策略获取 verbatim 文本替换
3. 值可能错了？→ Step 4

### Step 4: 判断值验证（全量，必须执行）

**这一步不是可选的，也不是只验证修过证据的字段。** 你必须对论文的**所有字段**（包括 EXACT 和 PARAPHRASED 的）用已验证的证据 + 字段定义验证判断值。

为什么全量？因为证据质量高不代表判断值正确。EXACT 的证据可能支持的是另一个值。

#### 必检清单

对每个字段，问自己：**"基于这篇论文实际做了什么，这个值对吗？"**

重点关注以下易错字段：

| 字段 | 常见错误 | 正确判断方法 |
|------|----------|--------------|
| `prompt_disclosure` | 论文在附录提供了 prompt 却标 No | 如果附录/补充材料中有完整 prompt → **Full**；部分提供 → **Partial**；完全没有 → **No** |
| `reliability_reported` | 百分比一致率被当作信度系数 | 只有报告了 kappa/alpha/ICC 等统计系数才是 **Yes**；百分比一致、简单计数 → **No** |
| `theory_grounding` | 框架被引用但未用于定义/测量 | Strong = 理论明确指导了评估设计；Weak = 提及但未深入使用 |
| `llm_judge_validated` | 使用了 LLM judge 但未验证就标 YES | YES 必须有 LLM 打分与人类打分的一致性分析 |
| `eval_user_study` | 静态打分任务被当作用户研究 | 用户必须与系统有交互，有明确任务/协议 |
| `dim_*` 系列 | 维度不存在就标 NO | NO 是正确的，但要确认论文确实没有评估该维度 |

#### prompt_disclosure 判断规则

这是最容易出错的字段。判断流程：

```
论文是否在正文/附录/补充材料中提供了 prompt？
├── 是，完整提供了所有必要 prompt → Full
├── 是，但只提供了部分或示例 → Partial
└── 否，完全没有提供 → No
```

**关键**：附录中的 prompt 模板、Table A5 等都算"提供了"。很多论文会写 "Full prompts are shown in the Appendix"——这就是 Full，不是 No。

#### 如果值错了

修正值 + 同步 CSV：

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

> **注意**：CSV 列名可能和 markdown 字段名不同（如 `Raw Eval Metrics` vs `raw_eval_metrics`）。先用 `head -1 eval_results.csv` 检查列名。

### Step 5: 重新跑脚本确认

```bash
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py {ids}
```

确认 TEMPLATE = 0，FABRICATED 尽可能低。

## 获取 Verbatim 证据的策略

> ⚠️ **逐字引用铁律**
> 证据必须是 PDF 原文逐字引用。绝对不能自己写总结、改写、缩写。
> 如果你写出来的文字不是 PDF 里原封不动抄出来的，就是错的。

### 策略 1：使用 `--extract-evidence` 候选（推荐）

候选是脚本从 PDF 提取的相关片段。**直接使用，不要扩展。**

候选格式示例：
```
{page: 5, text: "accuracy in suicide risk assessment", relevance: 2}
```

直接用 `text` 字段的值作为 evidence 分段，不要试图补全句子。

### 策略 2：用 PyMuPDF 读取 PDF 原文（精确控制）

当候选不够用时，直接从 PDF 提取精确文本：

```python
import fitz
doc = fitz.open("paper/{id}.pdf")
page = doc[page_num - 1]  # 0-indexed
text = page.get_text()
# 搜索关键词，获取包含该关键词的完整句子
```

提取后做子串归一化检查：去掉换行、合并连字符，确认是 PDF 子串。

### 策略 3：复用同一论文已验证为 EXACT 的文本（NO 字段专用）

对于 NO/No/N/A 字段，最可靠的方法是**复用同一论文中已验证为 EXACT 的文本**。

例如，如果 `focus_type` 的 evidence 是：
> `**Evidence** (p.1): This review introduces a conceptual taxonomy dividing psychotherapy into interconnected stages–assessment, diagnosis, and treatment–to systematically examine LLM advancements and challenges.`

这段已验证为 EXACT，可以复用于 `eval_human_experts: NO`、`eval_automatic: NO` 等字段。文本内容虽不直接说明"为什么 NO"，但它描述了论文的性质（综述），间接支持 NO 的判断。

### 策略 4：组合多个候选片段（用 `...` 分隔）

如果需要组合多个候选片段，用 ` ... ` 分隔。每个片段独立验证：

```
**Evidence** (p.6-7): Quantitative Performance Metrics: Our analysis identified three primary performance indicators. ... • Response Quality: This metric assesses the coherence, authenticity, and relevance of CA-generated dialogue. ... • System Reliability: This measures the stability and predictability of CA responses.
```

**关键**：每个 `...` 之间的片段必须是 PDF 中连续出现的文本。如果 PDF 中两段之间有其他文字，必须用 `...` 分隔。

### ❌ 绝对不要做的事

| 做法 | 结果 | 原因 |
|------|------|------|
| 用自己的话总结 | FABRICATED | 不是 PDF 原文 |
| 扩展候选片段为完整句子 | FABRICATED | 扩展部分不是 PDF 原文 |
| 把 PDF 中不连续的文本拼成一段 | FABRICATED | 中间有文字不匹配 |
| 用 "No evidence of..." 开头 | TEMPLATE | 脚本直接判定为模板 |

### ✅ 正确示例

**TEMPLATE → EXACT（NO 字段，复用已验证文本）**：
```
# 原始
**Evidence** (N/A): No evidence of safety evaluation found in the paper.

# 修复：复用 focus_type 已验证的 EXACT 文本
**Evidence** (p.1): This review introduces a conceptual taxonomy dividing psychotherapy into interconnected stages–assessment, diagnosis, and treatment–to systematically examine LLM advancements and challenges.
```

**FABRICATED → EXACT（YES 字段，用 `...` 分隔非连续片段）**：
```
# 原始（一整段，中间跳过了 PDF 中的文字）
**Evidence** (p.6): Quantitative Performance Metrics: Our analysis identified three primary performance indicators. • Diagnostic Accuracy: This metric assesses... • Response Quality: This metric assesses... • System Reliability: This measures...

# 修复：用 ... 分隔
**Evidence** (p.6-7): Quantitative Performance Metrics: Our analysis identified three primary performance indicators. ... • Diagnostic Accuracy: This metric assesses... ... • Response Quality: This metric assesses... ... • System Reliability: This measures...
```

**FABRICATED → EXACT（用 PyMuPDF 提取精确文本）**：
```python
# 找到 PDF 中的精确文本
import fitz
doc = fitz.open("paper/96.pdf")
page = doc[8]  # page 9
text = page.get_text()
# 搜索 "The strengths and limitations"
idx = text.find("The strengths and limitations")
# 提取到句号
end = text.find('.', idx)
exact = text[idx:end+1].strip()
# "The strengths and limitations of various evaluation approaches explain the field's preference for mixed-method evaluations"
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
| prompt_disclosure | Full / Partial / No | Full = 在正文或附录中清晰提供了所有必要提示词；Partial = 部分提供；No = 完全没有 |
| behavior_eval_depth | Dynamic / Pattern-level / Static / None | Dynamic = 分析行为如何随轮次变化 |

## Tips

- **证据必须是原文，没有例外。** TEMPLATE 不是安全状态，是需要修复的缺陷。
- **Always sync `eval_results.csv` when judgment values change.** Markdown + CSV 必须同时更新。
- 脚本处理 PDF 连字符（`psy-\nchological` → `psychological`）和弯引号归一化。
- 用 `...` 连接的分段证据，每段独立验证。
- 43 个结构化字段，7 个类别。重点关注信度、理论、交互层级等边界模糊字段。
- **NO 字段不需要"解释为什么 NO"的证据**——只需提供论文中已有的、可验证的文本。该文本描述了论文的性质或方法，间接支持 NO 的判断。

## 常见错误案例

### prompt_disclosure: 附录有 prompt 却标 No

**错误模式**：论文写 "Full prompts are shown in the Appendix A.1" 或 "Table A5: Template for zero-shot prompting"，但 `prompt_disclosure` 被标为 No。

**正确判断**：附录中的 prompt 模板 = 已提供 = Full 或 Partial，不是 No。

**实际案例**（Paper 47）：
```
# 错误
prompt_disclosure: No
**Evidence** (p.5): Full prompts are shown in the Appendix A.1.
# ↑ 证据自己说了 "Full prompts"，值却标 No，矛盾

# 正确
prompt_disclosure: Full
```

### confidence: 修证据时被误改

**错误模式**：修复 TEMPLATE/FABRICATED 证据时，把 confidence 从 85/90/95 改成了 100。

**正确做法**：confidence 反映判断值的置信度，不是证据质量。只改 evidence，不改 confidence。除非你在 Step 4 中改变了判断值本身。

### reliability_reported: 百分比一致被当作信度

**错误模式**：论文写 "Three experts agree with the given label" 或 "inter-annotator agreement was 85%"，被标为 Yes。

**正确判断**：百分比一致率不是统计信度系数。只有 kappa/alpha/ICC 等才是 Yes。