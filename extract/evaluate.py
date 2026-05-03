"""
从 PDF 论文中提取评价方法论信息，输出 CSV 和验证 Markdown。

使用方式:
  1. 确保 .env 中已配置 OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL
  2. uv run evaluate.py              # 处理 paper/ 目录下所有 PDF
  3. uv run evaluate.py --dir /path   # 指定其他目录
  4. 输出: eval_results.csv + eval_reports/*.md
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

# --- Field Definitions ---
EVAL_METHOD_FIELDS = [
    "eval_human_experts",
    "eval_lay_users",
    "eval_user_study",
    "eval_llm_judge",
    "eval_automatic",
]

DIMENSION_FIELDS = [
    "dim_realism",
    "dim_consistency",
    "dim_fidelity",
    "dim_utility",
    "dim_human_learning",
    "dim_emotional_plausibility",
    "dim_safety",
]

SINGLE_CHOICE_FIELDS = {
    "interaction_level": ["None", "Short", "Extended", "Longitudinal"],
    "prompt_disclosure": ["Full", "Partial", "No"],
    "theoretical_grounding": ["Strong", "Weak", "None"],
    "inter_rater_reliability": ["Yes", "No", "N/A"],
}

DEFECT_OPTIONS = [
    "lacks evaluation rubric",
    "limited sample size",
    "participant expertise unclear",
    "relies on subjective ratings only",
    "LLM judge not validated",
    "evaluation prompt not specified",
    "assumes LLM evaluation is reliable",
    "uses custom metric without benchmark",
    "metric lacks interpretability",
    "evaluation not comparable across studies",
    "no real-world human outcomes evaluated",
    "lacks long-term interaction evaluation",
    "no evaluation under diverse conditions",
    "lacks analysis of failure cases",
    "evaluated only in simulated settings",
    "simulated behavior not realistic",
    "not tested in real-world scenarios",
    "prompts not disclosed",
    "dataset not available",
    "evaluation procedure not clearly described",
]

BOOL_FIELDS = EVAL_METHOD_FIELDS + DIMENSION_FIELDS
ALL_EXTRACTION_FIELDS = BOOL_FIELDS + list(SINGLE_CHOICE_FIELDS.keys()) + ["defects"]

CSV_FIELDS = ["id"] + ALL_EXTRACTION_FIELDS


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


# --- System Prompt ---

SYSTEM_PROMPT = """\
你是一个学术论文评价方法论提取助手。你的任务是从给定的论文全文中提取评价方法论相关的结构化信息。

请严格按照以下规则和输出格式提取信息。对于每个字段，你必须给出一个明确的答案（不允许留空），并提供原文引用作为证据。

## 提取字段与判断规则

### 评估方法分类（每个字段 YES 或 NO）

1. **eval_human_experts**: 领域专家（治疗师、临床医生、受过训练的标注员）进行了评估。
   排除：众包工人、无专业知识的学生、LLM评估。
   核心规则：评估者具备与任务相关的**领域专业知识**。

2. **eval_lay_users**: 非专家/普通用户（MTurk/Prolific众包工人、普通用户、未提及专业背景的"参与者"）进行了评估。
   排除：领域专家、受过训练的标注员。
   核心规则：参与者是**没有领域专业知识的普通用户**。

3. **eval_user_study**: 进行了结构化实验，用户与系统发生了交互，有明确任务、协议或实验设计。
   排除：简单的打分任务（无交互）、静态输出评估。
   核心规则：参与者在实验环境中**主动与系统发生了交互**。

4. **eval_llm_judge**: 使用 GPT-4/Claude 等大模型进行打分、比较、排序。
   排除：提取向量相似度、特征提取、计算指标。
   核心规则：LLM 被提示去**评估、打分或比较**输出结果。

5. **eval_automatic**: 通过算法/数学公式自动计算的指标（BLEU, ROUGE, Accuracy, F1, Cosine相似度, 任务成功率）。
   排除：LLM打分、人类打分。
   核心规则：通过**公式或算法计算**得出，无人类或LLM主观判断。

### 评估核心维度（每个字段 YES 或 NO）

1. **dim_realism**: 评估输出是否像人类或自然（human-like, natural, believable）。
   排除：正确性、任务成功率。核心规则：评估输出是否**类似于人类的行为或语言**。

2. **dim_consistency**: 评估跨轮次行为是否稳定（consistency, persona stability, drift）。
   排除：单轮质量。核心规则：评估在**多轮交互中的稳定性**。

3. **dim_fidelity**: 评估输出是否符合预设角色/目标（alignment, fidelity, adherence）。
   排除：一般真实性。核心规则：评估输出与**预设身份或模型匹配**的程度。

4. **dim_utility**: 评估系统对任务是否有用/有效（helpful, useful, effective）。
   排除：仅评估真实性。核心规则：评估系统的**有用性或有效性**。

5. **dim_human_learning**: 评估是否带来人类进步/改变（learning, skill improvement, confidence, outcomes）。
   排除：仅评估感知。核心规则：测量人类在知识、技能或行为上的**实质变化**。

6. **dim_emotional_plausibility**: 评估情绪反应是否真实/恰当（empathy, emotion, affect, emotional realism）。
   排除：事实正确性。核心规则：评估**情绪行为或共情能力**。

7. **dim_safety**: 评估是否避免有害/偏见输出（safety, harmful, bias, ethical）。
   排除：有用性。核心规则：评估**有害性或伦理问题**。

### 交互层级（单选）

- **None**: 一次只评估一个回复，无历史记录
- **Short**: 包含简短交流 2-5轮
- **Extended**: 基于较长对话的评估 6+轮
- **Longitudinal**: 跨越多个会话/较长时间的评估

### 提示词披露度（单选）

- **Full**: 清晰提供了所有必要提示词（论文正文、附录或GitHub中给出）
- **Partial**: 展示了部分提示词，不足以复现
- **No**: 没有可用的提示词信息

### 理论支撑度（单选）

- **Strong**: 明确使用公认理论来定义或测量（如CBT概念、MI编码、经过验证的临床量表）
- **Weak**: 提及了概念但未在评估中实际操作化（如提到共情但只用1-5 helpfulness打分）
- **None**: 没有真正的理论支撑（仅评估流畅度、偏好、真实性）

### 信度报告（单选）

判断是否报告了**标准化的评估者间信度系数**。
- **Yes**: 明确报告了公认的统计系数（如 Cohen's kappa, Krippendorff's alpha, ICC, Fleiss' kappa, Pearson/Spearman 相关系数用于评估者一致性）。仅报告平均差异、标准差、百分比一致性**不算** Yes。
- **No**: 使用了人类评估，但仅报告了非标准化的粗略指标（如平均差异、标准差、百分比一致），或完全未报告任何一致性指标。
- **N/A**: 没有使用人类评估（纯自动指标或纯 LLM 评估）。

### 评估缺陷（从以下列表中选择1-2个）

人类评估问题：lacks evaluation rubric, limited sample size, participant expertise unclear, relies on subjective ratings only
LLM裁判问题：LLM judge not validated, evaluation prompt not specified, assumes LLM evaluation is reliable
指标问题：uses custom metric without benchmark, metric lacks interpretability, evaluation not comparable across studies
缺失评估维度：no real-world human outcomes evaluated, lacks long-term interaction evaluation, no evaluation under diverse conditions, lacks analysis of failure cases
生态效度问题：evaluated only in simulated settings, simulated behavior not realistic, not tested in real-world scenarios
透明度/复现：prompts not disclosed, dataset not available, evaluation procedure not clearly described

## 输出格式

严格返回以下 JSON 对象，不要包含其他内容。每个字段必须包含 value、evidence（原文引用或说明）、page（页码整数或null）、confidence（0-100整数）。

{
  "title": "论文标题",
  "eval_human_experts": {"value": "YES", "evidence": "Our evaluation team consists of two experts.", "page": 8, "confidence": 85},
  "eval_lay_users": {"value": "NO", "evidence": "No evidence of non-expert user evaluation found in the paper.", "page": null, "confidence": 90},
  "eval_user_study": {"value": "YES", "evidence": "We invite six volunteers to interact as clients with the AI psychotherapy models.", "page": 7, "confidence": 80},
  "eval_llm_judge": {"value": "NO", "evidence": "No evidence of LLM-as-judge evaluation found in the paper.", "page": null, "confidence": 95},
  "eval_automatic": {"value": "YES", "evidence": "We evaluate the model using BLEU and ROUGE scores.", "page": 6, "confidence": 88},
  "dim_realism": {"value": "NO", "evidence": "No evidence of evaluating whether outputs appear human-like or natural found in the paper.", "page": null, "confidence": 85},
  "dim_consistency": {"value": "YES", "evidence": "the model maintains consistent persona across multiple turns of dialogue", "page": 7, "confidence": 75},
  "dim_fidelity": {"value": "NO", "evidence": "No evidence of evaluating adherence to a preset persona or role found in the paper.", "page": null, "confidence": 90},
  "dim_utility": {"value": "YES", "evidence": "participants reported the system was helpful for their daily tasks", "page": 8, "confidence": 80},
  "dim_human_learning": {"value": "NO", "evidence": "No evidence of measuring changes in human knowledge, skills, or behavior found in the paper.", "page": null, "confidence": 88},
  "dim_emotional_plausibility": {"value": "YES", "evidence": "empathy plays a pivotal therapeutic role in fostering patients' psychological recovery", "page": 7, "confidence": 70},
  "dim_safety": {"value": "NO", "evidence": "No evidence of systematic safety or harmfulness evaluation found in the paper.", "page": null, "confidence": 82},
  "interaction_level": {"value": "Extended", "evidence": "The dialogue process lasts for three rounds", "page": 7, "confidence": 75},
  "prompt_disclosure": {"value": "Partial", "evidence": "The prompts used in our experiments are shown in Figure 2.", "page": 4, "confidence": 80},
  "theoretical_grounding": {"value": "Weak", "evidence": "we use a 5-point Likert scale to measure helpfulness", "page": 2, "confidence": 65},
  "inter_rater_reliability": {"value": "No", "evidence": "No evidence of standardized inter-rater reliability coefficients (e.g., Cohen's kappa, Krippendorff's alpha) found in the paper.", "page": null, "confidence": 70},
  "defects": {"value": ["lacks evaluation rubric", "metric lacks interpretability"], "evidence": "the evaluation criteria are not clearly defined in the paper", "page": 8, "confidence": 60}
}

重要：
- 每个字段都必须有值，不允许留空或null（value不能为空）
- 如果某个评估方法或维度没有被使用，value 应为 "NO"，evidence 使用模板："No evidence of [method/dimension] found in the paper."
- confidence 反映你对判断的确定程度（0-100）
- **evidence 必须是论文原文的逐字引用（verbatim quote），一字不改，一句不编。**
- 禁止改写、概括、总结、释义或用自己的话重新表述。
- 如果 value 为 NO，evidence 中写 "No evidence of [具体方法/维度] found in the paper." 即可，不要编造原文。
- 引用可以省略开头或结尾的片段（用"..."表示），但中间部分必须逐字一致。
- 页码标记 "--- Page N ---" 会帮助你定位原文，请据此给出准确的 page 值。
"""


# --- Response Parsing ---

def strip_code_fences(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```\w*\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return content.strip()


def parse_llm_response(content: str) -> dict:
    content = strip_code_fences(content)
    data = json.loads(content)

    result = {}
    result["title"] = data.get("title", "")

    # Validate bool fields
    for field in BOOL_FIELDS:
        field_data = data.get(field, {})
        value = str(field_data.get("value", "NO")).upper()
        result[field] = {
            "value": value if value in ("YES", "NO") else "NO",
            "evidence": str(field_data.get("evidence", "")),
            "page": field_data.get("page"),
            "confidence": _clamp_confidence(field_data.get("confidence", 50)),
        }

    # Validate single-choice fields
    for field, valid_options in SINGLE_CHOICE_FIELDS.items():
        field_data = data.get(field, {})
        value = str(field_data.get("value", valid_options[-1]))
        result[field] = {
            "value": value if value in valid_options else valid_options[-1],
            "evidence": str(field_data.get("evidence", "")),
            "page": field_data.get("page"),
            "confidence": _clamp_confidence(field_data.get("confidence", 50)),
        }

    # Validate defects
    defects_data = data.get("defects", {})
    raw_defects = defects_data.get("value", [])
    if isinstance(raw_defects, str):
        raw_defects = [raw_defects]
    valid_defects = [d for d in raw_defects if d in DEFECT_OPTIONS]
    if not valid_defects:
        valid_defects = [DEFECT_OPTIONS[0]]
    result["defects"] = {
        "value": valid_defects[:2],
        "evidence": str(defects_data.get("evidence", "")),
        "page": defects_data.get("page"),
        "confidence": _clamp_confidence(defects_data.get("confidence", 50)),
    }

    return result


def _clamp_confidence(val) -> int:
    try:
        n = int(val)
    except (TypeError, ValueError):
        return 50
    return max(0, min(100, n))


# --- Output ---

def build_csv_row(paper_id: str, parsed: dict) -> dict:
    row = {"id": paper_id}
    for field in BOOL_FIELDS:
        row[field] = parsed[field]["value"]
    for field in SINGLE_CHOICE_FIELDS:
        row[field] = parsed[field]["value"]
    row["defects"] = "|".join(parsed["defects"]["value"])
    return row


def generate_markdown(paper_id: str, parsed: dict) -> str:
    title = parsed.get("title", f"Paper {paper_id}")
    lines = [f"# Paper {paper_id}: {title}\n"]

    lines.append("## 表1：评估方法\n")
    for field in EVAL_METHOD_FIELDS:
        _append_field(lines, field, parsed[field])

    lines.append("## 表2：评估核心维度\n")
    for field in DIMENSION_FIELDS:
        _append_field(lines, field, parsed[field])

    lines.append("## 表3-7：交互层级 / 提示词披露 / 理论支撑 / 信度报告 / 缺陷\n")
    for field in SINGLE_CHOICE_FIELDS:
        _append_field(lines, field, parsed[field])
    _append_field(lines, "defects", parsed["defects"])

    return "\n".join(lines)


def _append_field(lines: list, field_name: str, field_data: dict):
    value = field_data["value"]
    confidence = field_data["confidence"]
    evidence = field_data["evidence"]
    page = field_data["page"]

    if isinstance(value, list):
        value_str = ", ".join(value)
    else:
        value_str = value

    page_str = f"p.{page}" if page is not None else "N/A"
    lines.append(f"### {field_name}: {value_str} (confidence: {confidence})")
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
        return {row["id"] for row in reader if row.get("id")}


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
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            if write_header:
                writer.writeheader()
            writer.writerows(new_rows)

    print(f"\n完成！{len(new_rows)}/{len(new_pdfs)} 篇新增记录已写入 {OUTPUT_CSV}")
    print(f"验证文档已生成到 {REPORTS_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
