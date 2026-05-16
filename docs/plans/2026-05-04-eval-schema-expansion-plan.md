# 评估维度扩充实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 扩充评估维度表文档并重写 evaluate.py，使输出严格对齐 theme_track.csv 的 43 列 schema。

**Architecture:** 文档先行（追加表 8-11），然后完整重写 evaluate.py——用 CSV_COLUMNS 元组列表维护字段映射，SYSTEM_PROMPT 按 9 个 section 组织，解析和输出逻辑按字段类型分组处理。

**Tech Stack:** Python 3.12, pymupdf, openai (async), python-dotenv

**Spec:** `docs/specs/2026-05-04-eval-schema-expansion-design.md`

---

### Task 1: 扩充评估维度表文档

**Files:**
- Modify: `docs/评估维度表.md:113` (在文件末尾追加表 8-11)

- [ ] **Step 1: 在表 7 之后追加表 8-11**

在文件末尾（第 113 行之后）追加以下内容：

```markdown

---

### 表 8：模拟/角色建模
*注：识别论文中的模拟框架设计和角色建模方式。*

| 字段 | 类型 | 定义 | 选项 |
| :--- | :--- | :--- | :--- |
| **Focus_Type** | 开放分类 | 论文的主要研究焦点类型 | SimulationFramework: 提出模拟框架 / EvaluationFramework: 提出评估框架 / Dataset: 构建数据集 / Training System: 训练系统 / Tool: 工具等 |
| **Simulation_Target** | 单选 | 论文模拟的对象 | Client Agent: 模拟来访者 / Therapist Agent: 模拟咨询师 / Dual-Agent: 双方都模拟 / Human Trainee: 人类受训者 |
| **Persona_Model_Depth** | 单选 | 模拟用户画像的建模深度 | Surface Persona: 表层描述(如用文字profile) / Behavioral State Model: 行为状态模型 / Cognitive Model: 认知模型(含信念/动机等) / Dynamic Traits: 动态特质(随对话变化) / Expert Principles: 专家定义的原则 |
| **Uses_Dynamic_State** | YES/NO | 是否使用动态状态建模 | YES=有明确的动态状态追踪机制（如状态转移、会话记忆等） |
| **Temporal_Modeling_Details** | 自由文本 | 动态状态建模的具体方式描述 | 如 State transitions / Session memory / Dynamic openness / Conversation principles update / Limited |

---

### 表 9：评估深度与理论操作化
*注：评估论文对行为和理论的深入程度。*

| 字段 | 类型 | 定义 | 选项 |
| :--- | :--- | :--- | :--- |
| **Raw_Eval_Metrics** | 自由文本 | 论文实际使用的评估指标名称 | 如 "BLEU, ROUGE-L, BERTScore, human Likert 1-5" |
| **Theory_Operationalized** | 单选 | 理论是否被用于定义评估标准或指标，不仅仅是提及 | Strong: 评估标准明确源于理论 / Partial: 理论被提及并部分操作化 / None: 理论仅被提及或完全未使用 |
| **Behavior_Eval_Depth** | 单选 | 论文对交互过程中行为变化的评估深度 | Dynamic: 考虑行为如何随对话轮次演变 / Static: 仅评估单轮或静态输出 / None: 未评估行为 |
| **Intervention_Sensitivity** | YES/NO | 系统行为是否根据输入/干预发生适当变化 | 仅当论文明确测试了不同输入下行为的变化时标 YES |
| **Clinical_Theory** | 自由文本 | 具体使用的临床理论或框架名称 | 如 "CBT-inspired", "Motivational Interviewing", "Person-Centered Therapy" |

---

### 表 10：信度与方法论细节
*注：补充表 6 的信度报告，记录具体方法。*

| 字段 | 类型 | 定义 | 选项 |
| :--- | :--- | :--- | :--- |
| **Agreement_Method** | 自由文本 | 具体使用的一致性评测方法 | 如 Cohen's kappa, Krippendorff's alpha。若无则留空 |
| **Coding_Options** | Yes / No / N/A | 论文是否明确报告了评估者之间的一致性 | Yes: 明确报告了评估者间的 agreement / No: 使用了人类评估但未报告 agreement 或 consistency / N/A: 没有使用人类评估 |

---

### 表 11：评估质量标记
*注：替代表 7 的汇总缺陷方式，逐项独立判断 YES 或 NO。*

| 字段 | 定义 |
| :--- | :--- |
| **Has_Rubric** | 是否提供了明确的评分标准/评分指引 |
| **LLM_Judge_Validated** | LLM裁判是否经过验证（与人类评估对比等）。若未使用 LLM judge 则标 NO |
| **Uses_Standard_Metrics** | 是否使用了标准/公认的评估指标（非自创） |
| **Metric_Interpretable** | 评估指标的含义是否清晰可解释 |
| **Comparable_To_Prior_Work** | 评估是否可与先前研究进行对比 |
| **Has_Longitudinal_Eval** | 是否包含纵向/长期评估 |
| **Has_Robustness_Testing** | 是否在不同条件下进行了鲁棒性测试 |
| **Has_Failure_Analysis** | 是否分析了失败案例 |
| **Sim_Behavior_Realistic** | 模拟行为是否真实（非过于顺从或简化）。若未使用模拟则标 NO |
| **Dataset_Available** | 数据集是否公开可用 |
```

- [ ] **Step 2: 验证追加内容**

目视检查文件末尾，确认表 8-11 已追加，格式与表 1-7 一致。

- [ ] **Step 3: 提交**

```bash
git add docs/评估维度表.md
git commit -m "docs: add tables 8-11 for simulation, eval depth, reliability, and quality flags"
```

---

### Task 2: 重写 evaluate.py

**Files:**
- Rewrite: `extract/evaluate.py`

这是完整重写。新文件按以下结构组织：
1. 配置与常量
2. CSV 列映射（43 列严格对齐 theme_track.csv）
3. 字段分组（BOOL / SINGLE_CHOICE / FREE_TEXT）
4. SYSTEM_PROMPT（9 个 section）
5. PDF 文本提取
6. 响应解析
7. CSV 输出
8. Markdown 报告
9. LLM 调用
10. 幂等性
11. main

- [ ] **Step 1: 用完整的新文件替换 evaluate.py**

完整文件内容如下（每部分用注释标记）：

```python
"""
从 PDF 论文中提取评价方法论信息，输出与 theme_track.csv schema 完全对齐的 CSV 和验证 Markdown。

使用方式:
  1. 确保 .env 中已配置 OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL
  2. uv run evaluate.py              # 处理 paper/ 目录下所有 PDF
  3. uv run evaluate.py --dir /path   # 指定其他目录
  4. 输出: eval_results.csv + eval_reports/*.md

CSV 列严格对齐 docs/theme_track.csv，可直接复制行到目标文件。
"""

import argparse
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

# --- Configuration ---
MAX_CONCURRENCY = 3
MAX_RETRIES = 3
OUTPUT_CSV = Path(__file__).parent / "eval_results.csv"
REPORTS_DIR = Path(__file__).parent / "eval_reports"

# --- CSV Column Mapping (internal_name → theme_track.csv header, order matters) ---
CSV_COLUMNS = [
    ("paper_id", "Paper_ID"),
    ("title", "Title"),
    ("year", "Year"),
    ("venue", "Venue"),
    ("domain", "Domain"),
    ("focus_type", "Focus_Type"),
    ("simulation_target", "Simulation_Target"),
    ("persona_model_depth", "Persona_Model_Depth"),
    ("uses_dynamic_state", "Uses_Dynamic_State"),
    ("temporal_modeling_details", "Temporal_Modeling_Details"),
    ("eval_human_experts", "Eval_Human_Experts"),
    ("eval_lay_users", "Eval_Lay_Users"),
    ("eval_user_study", "Eval_User_Study"),
    ("eval_llm_judge", "Eval_LLM_Judge"),
    ("eval_automatic", "Eval_Automatic"),
    ("dim_safety", "Safety"),
    ("dim_realism", "Realism"),
    ("dim_consistency", "Consistency"),
    ("dim_fidelity", "Fidelity"),
    ("dim_human_learning", "Human Learning / Outcomes"),
    ("dim_utility", "Utility"),
    ("dim_emotional_plausibility", "Emotional Plausibility"),
    ("raw_eval_metrics", "Raw Eval Metrics"),
    ("theory_operationalized", "Theory_Operationalized"),
    ("behavior_eval_depth", "Behavior_Eval_Depth"),
    ("intervention_sensitivity", "Intervention_Sensitivity"),
    ("interaction_level", "Interaction_Level"),
    ("prompt_disclosure", "Prompt_Disclosure"),
    ("theory_grounding", "Theory_Grounding"),
    ("clinical_theory", "Clinical_Theory"),
    ("reliability_reported", "Reliability_Reported"),
    ("agreement_method", "Agreement Method"),
    ("coding_options", "Coding Options"),
    ("has_rubric", "Has_Rubric"),
    ("llm_judge_validated", "LLM_Judge_Validated"),
    ("uses_standard_metrics", "Uses_Standard_Metrics"),
    ("metric_interpretable", "Metric_Interpretable"),
    ("comparable_to_prior_work", "Comparable_To_Prior_Work"),
    ("has_longitudinal_eval", "Has_Longitudinal_Eval"),
    ("has_robustness_testing", "Has_Robustness_Testing"),
    ("has_failure_analysis", "Has_Failure_Analysis"),
    ("sim_behavior_realistic", "Sim_Behavior_Realistic"),
    ("dataset_available", "Dataset_Available"),
]

CSV_HEADER = [csv_name for _, csv_name in CSV_COLUMNS]
INTERNAL_TO_CSV = dict(CSV_COLUMNS)

# --- Field Groups ---

METADATA_FIELDS = ["title", "year", "venue", "domain"]

BOOL_FIELDS = [
    "eval_human_experts", "eval_lay_users", "eval_user_study",
    "eval_llm_judge", "eval_automatic",
    "dim_realism", "dim_consistency", "dim_fidelity",
    "dim_utility", "dim_human_learning", "dim_emotional_plausibility", "dim_safety",
    "uses_dynamic_state", "intervention_sensitivity",
    "has_rubric", "llm_judge_validated", "uses_standard_metrics",
    "metric_interpretable", "comparable_to_prior_work",
    "has_longitudinal_eval", "has_robustness_testing",
    "has_failure_analysis", "sim_behavior_realistic", "dataset_available",
]

SINGLE_CHOICE_FIELDS = {
    "simulation_target": ["Client Agent", "Therapist Agent", "Dual-Agent", "Human Trainee"],
    "persona_model_depth": [
        "Surface Persona", "Behavioral State Model",
        "Cognitive Model", "Dynamic Traits", "Expert Principles",
    ],
    "theory_operationalized": ["None", "Partial", "Strong"],
    "behavior_eval_depth": ["Dynamic", "Static", "None"],
    "interaction_level": ["None", "Short", "Extended", "Longitudinal"],
    "prompt_disclosure": ["Full", "Partial", "No"],
    "theory_grounding": ["Strong", "Weak", "None"],
    "reliability_reported": ["Yes", "No", "N/A"],
    "coding_options": ["Yes", "No", "N/A"],
}

FREE_TEXT_FIELDS = [
    "focus_type", "temporal_modeling_details", "raw_eval_metrics",
    "clinical_theory", "agreement_method",
]

STRUCTURED_FIELDS = BOOL_FIELDS + list(SINGLE_CHOICE_FIELDS.keys()) + FREE_TEXT_FIELDS

# --- System Prompt ---

SYSTEM_PROMPT = """\
你是一个学术论文评价方法论提取助手。从给定的论文全文中提取结构化信息。

请严格按照以下规则提取。每个字段必须给出明确答案，提供原文引用作为证据。

## 1. 基础元数据

- **title**: 论文标题（原文）
- **year**: 发表年份（数字）
- **venue**: 发表场所（会议名/期刊名）
- **domain**: 研究领域（如 Counseling, Therapy, Mental Health 等）

## 2. 模拟/角色建模

- **focus_type**: 论文的主要研究焦点类型（开放分类）。如 SimulationFramework, EvaluationFramework, Dataset, Training System, Tool 等，根据论文内容判断。
- **simulation_target**: 论文模拟的对象。
  Client Agent: 模拟来访者 / Therapist Agent: 模拟咨询师 / Dual-Agent: 双方都模拟 / Human Trainee: 人类受训者
- **persona_model_depth**: 模拟用户画像的建模深度。
  Surface Persona: 表层描述(如用文字profile) / Behavioral State Model: 行为状态模型 / Cognitive Model: 认知模型(含信念/动机等) / Dynamic Traits: 动态特质(随对话变化) / Expert Principles: 专家定义的原则
- **uses_dynamic_state** (YES/NO): 是否使用动态状态建模。YES=有明确的动态状态追踪机制(如状态转移、会话记忆等)。
- **temporal_modeling_details**: 动态状态建模的具体方式描述。如 State transitions, Session memory, Dynamic openness 等。

## 3. 评估方法分类（每个字段 YES 或 NO）

1. **eval_human_experts**: 领域专家（治疗师、临床医生、受过训练的标注员）进行评估。
   排除：众包工人、无专业知识的学生、LLM评估。核心规则：评估者具备**领域专业知识**。
2. **eval_lay_users**: 非专家/普通用户（MTurk/Prolific众包工人、普通用户）进行评估。
   排除：领域专家、受过训练的标注员。核心规则：参与者是**没有领域专业知识的普通用户**。
3. **eval_user_study**: 结构化实验，用户与系统发生交互，有明确任务或实验设计。
   排除：简单打分任务、静态输出评估。核心规则：参与者**主动与系统发生了交互**。
4. **eval_llm_judge**: 使用 GPT-4/Claude 等大模型进行打分、比较、排序。
   排除：向量相似度、特征提取。核心规则：LLM 被提示去**评估、打分或比较**。
5. **eval_automatic**: 算法/数学公式自动计算的指标（BLEU, ROUGE, Accuracy, F1 等）。
   排除：LLM打分、人类打分。核心规则：通过**公式或算法计算**得出。

## 4. 评估核心维度（每个字段 YES 或 NO）

1. **dim_realism**: 输出是否像人类或自然。排除：正确性、任务成功率。
2. **dim_consistency**: 跨轮次行为是否稳定。排除：单轮质量。
3. **dim_fidelity**: 是否符合预设角色/目标。排除：一般真实性。
4. **dim_utility**: 对任务是否有用/有效。排除：仅评估真实性。
5. **dim_human_learning**: 是否带来人类进步/改变。排除：仅评估感知。
6. **dim_emotional_plausibility**: 情绪反应是否真实/恰当。排除：事实正确性。
7. **dim_safety**: 是否避免有害/偏见输出。排除：有用性。

## 5. 评估深度与理论操作化

- **raw_eval_metrics**: 论文实际使用的评估指标名称（自由文本）。如 "BLEU, ROUGE-L, BERTScore, human Likert 1-5"。
- **theory_operationalized**: 理论是否被用于定义评估标准或指标，不仅仅是提及。
  Strong: 评估标准明确源于理论 / Partial: 理论被提及并部分操作化 / None: 理论仅被提及或完全未使用
- **behavior_eval_depth**: 对交互过程中行为变化的评估深度。
  Dynamic: 考虑行为如何随对话轮次演变 / Static: 仅评估单轮或静态输出 / None: 未评估行为

## 6. 干预敏感性

- **intervention_sensitivity** (YES/NO): 系统行为是否根据输入/干预发生适当变化。仅当论文明确测试了不同输入下行为变化时标 YES。

## 7. 单选字段

- **interaction_level**: 评估包含的对话上下文深度。None / Short (2-5轮) / Extended (6+轮) / Longitudinal (跨会话)
- **prompt_disclosure**: 提示词披露程度。Full / Partial / No
- **theory_grounding**: 评估标准与公认理论挂钩程度。Strong / Weak / None
- **clinical_theory**: 具体使用的临床理论或框架名称（自由文本）。如 "CBT-inspired", "Motivational Interviewing"。

## 8. 信度与方法论

- **reliability_reported**: 是否报告了评估者间信度。Yes: 报告了统计系数 / No: 用了人类评估但未报告 / N/A: 没有使用人类评估
- **agreement_method**: 具体使用的一致性评测方法（自由文本）。如 "Cohen's kappa"。若无则留空字符串。
- **coding_options**: 论文是否明确报告了评估者之间的一致性。Yes: 明确报告了agreement / No: 用了人类评估但未报告 / N/A: 没有使用人类评估

## 9. 评估质量标记（每个字段 YES 或 NO）

- **has_rubric**: 是否提供了明确的评分标准/评分指引。
- **llm_judge_validated**: LLM裁判是否经过验证。若未使用 LLM judge 则标 NO。
- **uses_standard_metrics**: 是否使用了标准/公认的评估指标。
- **metric_interpretable**: 评估指标的含义是否清晰可解释。
- **comparable_to_prior_work**: 评估是否可与先前研究进行对比。
- **has_longitudinal_eval**: 是否包含纵向/长期评估。
- **has_robustness_testing**: 是否在不同条件下进行了鲁棒性测试。
- **has_failure_analysis**: 是否分析了失败案例。
- **sim_behavior_realistic**: 模拟行为是否真实。若未使用模拟则标 NO。
- **dataset_available**: 数据集是否公开可用。

## 输出格式

严格返回 JSON 对象。基础元数据直接返回值，其余字段包含 value、evidence、page、confidence。

{
  "title": "论文标题",
  "year": 2024,
  "venue": "ACL",
  "domain": "Counseling",
  "focus_type": {"value": "EvaluationFramework", "evidence": "...", "page": 1, "confidence": 80},
  "simulation_target": {"value": "Client Agent", "evidence": "...", "page": 3, "confidence": 85},
  "persona_model_depth": {"value": "Behavioral State Model", "evidence": "...", "page": 4, "confidence": 75},
  "uses_dynamic_state": {"value": "YES", "evidence": "...", "page": 5, "confidence": 80},
  "temporal_modeling_details": {"value": "State transitions based on dialogue context", "evidence": "...", "page": 5, "confidence": 70},
  "eval_human_experts": {"value": "YES", "evidence": "...", "page": 8, "confidence": 85},
  "eval_lay_users": {"value": "NO", "evidence": "No evidence of non-expert user evaluation found in the paper.", "page": null, "confidence": 90},
  "eval_user_study": {"value": "YES", "evidence": "...", "page": 7, "confidence": 80},
  "eval_llm_judge": {"value": "NO", "evidence": "No evidence of LLM-as-judge evaluation found in the paper.", "page": null, "confidence": 95},
  "eval_automatic": {"value": "YES", "evidence": "...", "page": 6, "confidence": 88},
  "dim_realism": {"value": "NO", "evidence": "No evidence of evaluating whether outputs appear human-like or natural found in the paper.", "page": null, "confidence": 85},
  "dim_consistency": {"value": "YES", "evidence": "...", "page": 7, "confidence": 75},
  "dim_fidelity": {"value": "NO", "evidence": "...", "page": null, "confidence": 90},
  "dim_utility": {"value": "YES", "evidence": "...", "page": 8, "confidence": 80},
  "dim_human_learning": {"value": "NO", "evidence": "...", "page": null, "confidence": 88},
  "dim_emotional_plausibility": {"value": "YES", "evidence": "...", "page": 7, "confidence": 70},
  "dim_safety": {"value": "NO", "evidence": "...", "page": null, "confidence": 82},
  "raw_eval_metrics": {"value": "BLEU, ROUGE-L, BERTScore", "evidence": "...", "page": 6, "confidence": 90},
  "theory_operationalized": {"value": "Partial", "evidence": "...", "page": 2, "confidence": 65},
  "behavior_eval_depth": {"value": "Static", "evidence": "...", "page": 6, "confidence": 75},
  "intervention_sensitivity": {"value": "NO", "evidence": "No evidence of testing behavior changes under different inputs found in the paper.", "page": null, "confidence": 80},
  "interaction_level": {"value": "Extended", "evidence": "...", "page": 7, "confidence": 75},
  "prompt_disclosure": {"value": "Partial", "evidence": "...", "page": 4, "confidence": 80},
  "theory_grounding": {"value": "Weak", "evidence": "...", "page": 2, "confidence": 65},
  "clinical_theory": {"value": "CBT-inspired", "evidence": "...", "page": 3, "confidence": 75},
  "reliability_reported": {"value": "No", "evidence": "...", "page": null, "confidence": 70},
  "agreement_method": {"value": "", "evidence": "No agreement method reported.", "page": null, "confidence": 90},
  "coding_options": {"value": "No", "evidence": "...", "page": null, "confidence": 70},
  "has_rubric": {"value": "NO", "evidence": "...", "page": null, "confidence": 75},
  "llm_judge_validated": {"value": "NO", "evidence": "No LLM judge used.", "page": null, "confidence": 95},
  "uses_standard_metrics": {"value": "YES", "evidence": "...", "page": 6, "confidence": 80},
  "metric_interpretable": {"value": "YES", "evidence": "...", "page": 6, "confidence": 75},
  "comparable_to_prior_work": {"value": "NO", "evidence": "...", "page": null, "confidence": 70},
  "has_longitudinal_eval": {"value": "NO", "evidence": "...", "page": null, "confidence": 85},
  "has_robustness_testing": {"value": "NO", "evidence": "...", "page": null, "confidence": 80},
  "has_failure_analysis": {"value": "NO", "evidence": "...", "page": null, "confidence": 85},
  "sim_behavior_realistic": {"value": "NO", "evidence": "...", "page": null, "confidence": 70},
  "dataset_available": {"value": "NO", "evidence": "...", "page": null, "confidence": 80}
}

重要：
- 每个字段都必须有值（agreement_method 可以是空字符串 ""）
- 布尔字段未使用时 value 为 "NO"，evidence 用模板："No evidence of [方法/维度] found in the paper."
- confidence 反映判断的确定程度（0-100）
- **evidence 必须是论文原文的逐字引用（verbatim quote），禁止改写、概括或编造。**
- NO 字段的 evidence 写 "No evidence of [具体方法/维度] found in the paper." 即可。
- 页码标记 "--- Page N ---" 帮助定位原文，请给出准确的 page 值。
"""


# --- PDF Text Extraction ---

def extract_text_with_pages(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        pages.append(f"--- Page {i + 1} ---\n{text}")
    doc.close()
    return "\n\n".join(pages)


def parse_id(filename: str) -> str:
    match = re.match(r"(\d+)", filename)
    return match.group(1) if match else filename


# --- Response Parsing ---

def strip_code_fences(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```\w*\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return content.strip()


def _clamp_confidence(val) -> int:
    try:
        n = int(val)
    except (TypeError, ValueError):
        return 50
    return max(0, min(100, n))


def _parse_structured_field(data: dict, field: str) -> dict:
    field_data = data.get(field, {})
    return {
        "value": str(field_data.get("value", "")),
        "evidence": str(field_data.get("evidence", "")),
        "page": field_data.get("page"),
        "confidence": _clamp_confidence(field_data.get("confidence", 50)),
    }


def parse_llm_response(content: str) -> dict:
    content = strip_code_fences(content)
    data = json.loads(content)

    result = {}
    result["title"] = str(data.get("title", ""))
    result["year"] = data.get("year", "")
    result["venue"] = str(data.get("venue", ""))
    result["domain"] = str(data.get("domain", ""))

    for field in BOOL_FIELDS:
        parsed = _parse_structured_field(data, field)
        value = parsed["value"].upper()
        parsed["value"] = value if value in ("YES", "NO") else "NO"
        result[field] = parsed

    for field, valid_options in SINGLE_CHOICE_FIELDS.items():
        parsed = _parse_structured_field(data, field)
        value = parsed["value"]
        parsed["value"] = value if value in valid_options else valid_options[-1]
        result[field] = parsed

    for field in FREE_TEXT_FIELDS:
        result[field] = _parse_structured_field(data, field)

    return result


# --- CSV Output ---

def build_csv_row(paper_id: str, parsed: dict) -> dict:
    row = {"Paper_ID": paper_id}
    row["Title"] = parsed.get("title", "")
    row["Year"] = parsed.get("year", "")
    row["Venue"] = parsed.get("venue", "")
    row["Domain"] = parsed.get("domain", "")
    for field in STRUCTURED_FIELDS:
        csv_name = INTERNAL_TO_CSV[field]
        row[csv_name] = parsed[field]["value"]
    return row


# --- Markdown Report ---

def generate_markdown(paper_id: str, parsed: dict) -> str:
    title = parsed.get("title", f"Paper {paper_id}")
    lines = [f"# Paper {paper_id}: {title}\n"]

    lines.append("## 基础元数据\n")
    lines.append(f"- **Year**: {parsed['year']}")
    lines.append(f"- **Venue**: {parsed['venue']}")
    lines.append(f"- **Domain**: {parsed['domain']}\n")

    lines.append("## 模拟/角色建模\n")
    for field in ["focus_type", "simulation_target", "persona_model_depth",
                   "uses_dynamic_state", "temporal_modeling_details"]:
        _append_field(lines, field, parsed[field])

    lines.append("## 评估方法\n")
    for field in ["eval_human_experts", "eval_lay_users", "eval_user_study",
                   "eval_llm_judge", "eval_automatic"]:
        _append_field(lines, field, parsed[field])

    lines.append("## 评估核心维度\n")
    for field in ["dim_realism", "dim_consistency", "dim_fidelity",
                   "dim_utility", "dim_human_learning",
                   "dim_emotional_plausibility", "dim_safety"]:
        _append_field(lines, field, parsed[field])

    lines.append("## 评估深度\n")
    for field in ["raw_eval_metrics", "theory_operationalized", "behavior_eval_depth"]:
        _append_field(lines, field, parsed[field])

    lines.append("## 干预敏感性\n")
    _append_field(lines, "intervention_sensitivity", parsed["intervention_sensitivity"])

    lines.append("## 交互/披露/理论\n")
    for field in ["interaction_level", "prompt_disclosure", "theory_grounding", "clinical_theory"]:
        _append_field(lines, field, parsed[field])

    lines.append("## 信度与方法论\n")
    for field in ["reliability_reported", "agreement_method", "coding_options"]:
        _append_field(lines, field, parsed[field])

    lines.append("## 评估质量标记\n")
    for field in ["has_rubric", "llm_judge_validated", "uses_standard_metrics",
                   "metric_interpretable", "comparable_to_prior_work",
                   "has_longitudinal_eval", "has_robustness_testing",
                   "has_failure_analysis", "sim_behavior_realistic", "dataset_available"]:
        _append_field(lines, field, parsed[field])

    return "\n".join(lines)


def _append_field(lines: list, field_name: str, field_data: dict):
    value = field_data["value"]
    confidence = field_data["confidence"]
    evidence = field_data["evidence"]
    page = field_data["page"]
    page_str = f"p.{page}" if page is not None else "N/A"
    lines.append(f"### {field_name}: {value} (confidence: {confidence})")
    lines.append(f"**Evidence** ({page_str}): {evidence}\n")


# --- LLM Call ---

async def call_llm(
    client: AsyncOpenAI,
    model: str,
    semaphore: asyncio.Semaphore,
    paper_id: str,
    pdf_path: Path,
) -> dict | None:
    async with semaphore:
        print(f"[{paper_id}] {pdf_path.name} ... ", end="", flush=True)
        try:
            text = extract_text_with_pages(pdf_path)
        except Exception as e:
            print(f"PDF读取失败: {e}")
            return None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"请从以下论文全文中提取评价方法论信息：\n\n{text}"},
                    ],
                    temperature=0,
                )
                content = resp.choices[0].message.content
                if content is None:
                    raise ValueError("API 返回内容为空")
                parsed = parse_llm_response(content)
                print("OK")
                return parsed
            except Exception as e:
                if attempt < MAX_RETRIES:
                    print(f"重试 {attempt}/{MAX_RETRIES} ({e}) ... ", end="", flush=True)
                    await asyncio.sleep(2 * attempt)
                else:
                    print(f"失败: {e}")
                    return None


# --- Idempotency ---

def load_existing_ids(csv_path: Path) -> set[str]:
    if not csv_path.exists():
        return set()
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return {row["Paper_ID"] for row in reader if row.get("Paper_ID")}


# --- Main ---

async def main():
    parser = argparse.ArgumentParser(description="从论文PDF提取评价方法论信息")
    parser.add_argument("--dir", type=str, default=None, help="PDF目录路径（默认: paper/）")
    args = parser.parse_args()

    base_url = os.environ.get("OPENAI_BASE_URL")
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")

    if not base_url or not api_key or not model:
        print("错误: 请在 .env 中设置 OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL")
        sys.exit(1)

    paper_dir = Path(args.dir) if args.dir else Path(__file__).parent / "paper"
    if not paper_dir.exists():
        print(f"错误: 目录不存在: {paper_dir}")
        sys.exit(1)

    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    pdfs = sorted(paper_dir.glob("*.pdf"), key=lambda p: parse_id(p.name))
    if not pdfs:
        print(f"在 {paper_dir} 中未找到 PDF 文件")
        sys.exit(1)

    existing_ids = load_existing_ids(OUTPUT_CSV)
    new_pdfs = [p for p in pdfs if parse_id(p.name) not in existing_ids]

    if not new_pdfs:
        print("没有新增论文，全部已处理。")
        return

    REPORTS_DIR.mkdir(exist_ok=True)

    print(f"共 {len(pdfs)} 篇，已有 {len(existing_ids)} 篇，新增 {len(new_pdfs)} 篇（并发数 {MAX_CONCURRENCY}）...\n")

    tasks = [
        call_llm(client, model, semaphore, parse_id(p.name), p)
        for p in new_pdfs
    ]
    results = await asyncio.gather(*tasks)

    new_rows = []
    for pdf, parsed in zip(new_pdfs, results):
        if parsed is None:
            continue
        paper_id = parse_id(pdf.name)
        new_rows.append(build_csv_row(paper_id, parsed))

        md_path = REPORTS_DIR / f"{paper_id}.md"
        md_path.write_text(generate_markdown(paper_id, parsed), encoding="utf-8")

    if new_rows:
        write_header = not OUTPUT_CSV.exists() or OUTPUT_CSV.stat().st_size == 0
        with open(OUTPUT_CSV, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
            if write_header:
                writer.writeheader()
            writer.writerows(new_rows)

    print(f"\n完成！{len(new_rows)}/{len(new_pdfs)} 篇新增记录已写入 {OUTPUT_CSV}")
    print(f"验证文档已生成到 {REPORTS_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: 删除旧的 eval_results.csv（如存在）**

旧 schema 的 CSV 不兼容，需删除后重新运行。

```bash
rm -f extract/eval_results.csv
```

- [ ] **Step 3: 提交**

```bash
git add extract/evaluate.py
git commit -m "feat: rewrite evaluate.py to align with theme_track.csv 43-column schema"
```

---

### Task 3: 端到端验证

- [ ] **Step 1: 运行脚本处理一个 PDF**

```bash
cd extract && uv run evaluate.py
```

预期：处理 paper/ 目录下的 PDF，输出 eval_results.csv 和 eval_reports/*.md。

- [ ] **Step 2: 检查 CSV header 与 theme_track.csv 一致**

```bash
head -1 extract/eval_results.csv
```

预期输出应包含 43 列，header 行与 `docs/theme_track.csv` 的第一行完全一致。

- [ ] **Step 3: 检查数据行的字段值格式**

```bash
head -2 extract/eval_results.csv | tail -1
```

预期：布尔字段为 YES/NO，单选字段为选项文本，自由文本字段有内容。

- [ ] **Step 4: 检查 Markdown 报告**

```bash
ls extract/eval_reports/
cat extract/eval_reports/<paper_id>.md | head -30
```

预期：包含所有 section，每个字段有 value、confidence、evidence。
