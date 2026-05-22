"""Prompt construction for the agentic extraction pipeline."""

import json
from lib.schemas import PHASES, FIELD_DEFINITIONS, METADATA_FIELDS, BOOL_FIELDS


def build_system_prompt() -> str:
    return """\
你是一个学术论文评价方法论提取助手。从给定的论文全文中提取结构化信息。

## 工具使用规则

你有 submit_result 工具可用，用于提交当前阶段的提取结果。

**提取策略：**
- 论文全文已在对话历史中（Phase 0 消息），请直接从全文中提取信息
- 一次性生成 JSON，调用 submit_result 提交
- evidence 必须是论文原文的逐字引用，禁止编造、改写或概括

## 字段定义（完整参考）

以下是所有可提取的字段。每个阶段你只需提取当前阶段指定的字段，但可以参考其他字段的定义来理解上下文。

""" + _build_field_definitions_section() + "\n" + _build_output_format_section()


def _build_field_definitions_section() -> str:
    lines = []
    for phase in PHASES:
        lines.append(f"### {phase['name']}")
        for field in phase["fields"]:
            lines.append(f"- **{field}**: {FIELD_DEFINITIONS[field]}")
        lines.append("")
    return "\n".join(lines)


def _build_output_format_section() -> str:
    return """\
## 输出格式

严格返回 JSON 对象。

元数据字段（title, year, venue, domain）直接返回值。

其余字段格式：
```json
{
  "field_name": {"value": "...", "evidence": "...", "page": 1, "confidence": 80}
}
```

规则：
- 每个字段都必须有值（agreement_method 可以是空字符串 ""）
- 布尔字段 value 为 "YES" 或 "NO"
- confidence 为 0-100 整数
- evidence 必须是论文原文的逐字引用
- 允许用 " ... " 连接多个不连续的引用片段（如不同段落或不同句子的证据）
- 表格中的数据必须逐字引用，禁止重新格式化、添加标签或改写（如禁止将 "test 300 3" 改为 "Cases: 300; Rounds: 3"）
- 所有字段（包括 NO/N/A）的 evidence 都必须是论文原文的逐字引用。即使是判断为"不存在"的字段，也要引用论文中让你做出该判断的原文（如评估方法描述、参与者描述等）
- 仅当论文中确实完全没有相关内容时，才使用模板: "No evidence of [具体方法/维度] found in the paper."，page 设为 null
- page 为页码数字，若无则 null
"""


def build_phase_user_message(
    phase_idx: int,
    full_text: str,
    extracted_so_far: dict,
) -> str:
    phase = PHASES[phase_idx]

    if phase.get("type") == "metadata":
        return f"""论文全文:
{full_text}

请先提取元数据（{', '.join(phase['fields'])}），直接返回 JSON，无需工具调用。"""

    field_list = "\n".join(
        f"- **{f}**: {FIELD_DEFINITIONS[f]}" for f in phase["fields"]
    )

    extracted_summary = ""
    if extracted_so_far:
        lines = []
        for key, val in extracted_so_far.items():
            if isinstance(val, dict):
                page_info = f" (p.{val['page']})" if val.get("page") else ""
                lines.append(f"  - {key}: {val['value']}{page_info}")
            else:
                lines.append(f"  - {key}: {val}")
        extracted_summary = "\n已提取字段（可直接引用）:\n" + "\n".join(lines)

    return f"""现在请提取以下字段（阶段 {phase_idx}/{len(PHASES) - 1}: {phase['name']}）：

{field_list}
{extracted_summary}

论文全文已在对话历史中（Phase 0 消息）。请直接从全文中提取并返回 JSON。
evidence 必须是论文原文的逐字引用。

返回仅包含本阶段字段的 JSON，或使用 submit_result 工具提交。"""


def build_correction_message(failures: dict[str, dict]) -> str:
    parts = [
        "以下字段的 evidence 未通过逐字引用验证。请从论文原文（Phase 0 消息）中重新查找正确的逐字引用。\n",
        "## 验证失败的字段\n",
    ]
    for field, info in failures.items():
        current = info["current"]
        page = current.get("page")
        page_str = f"p.{page}" if page else "N/A"
        parts.append(f"### {field}")
        parts.append(f"- 当前 value: {current.get('value', '')}")
        parts.append(f"- 当前 evidence ({page_str}): \"{current.get('evidence', '')}\"")
        parts.append(f"- 错误原因: {info['error']}")
        parts.append("")
    parts.append(
        "请返回仅包含以上字段的 JSON，使用 submit_result 提交。\n"
        "要求：\n"
        "- evidence 必须是论文原文的逐字引用（直接从 Phase 0 全文中复制粘贴）\n"
        "- value 和 confidence 保持不变，仅修正 evidence 和 page\n"
        "- page 必须是引用内容实际所在的页码\n"
        "- 如果在原文中找不到合适的引用，请将 evidence 设为标准模板文本，page 设为 null\n"
        "  - NO/N/A 字段模板: \"No evidence of [具体方法/维度] found in the paper.\"\n"
        "  - 严禁为 NO/N/A 字段编造或改写 evidence\n"
        "- 但如果论文中确实有相关内容（如评估方法描述、参与者描述），必须引用那段原文作为 evidence"
    )
    return "\n".join(parts)
