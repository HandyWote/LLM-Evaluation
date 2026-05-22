"""Tool definitions (OpenAI function calling) and execution for the agentic extraction pipeline."""

import json
from extract.pdf_index import PDFIndex, SearchResult

TOOL_DEFINITIONS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "submit_result",
            "description": "提交当前阶段的提取结果。完成所有字段提取后调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "result": {
                        "type": "object",
                        "description": "JSON object with extracted field values for this phase",
                    },
                },
                "required": ["result"],
            },
        },
    },
]


def execute_tool(index: PDFIndex, tool_name: str, args: dict) -> str:
    """Execute a tool call and return a JSON string result for the LLM."""
    if tool_name == "submit_result":
        return json.dumps({"status": "received"})
    return json.dumps({"error": f"Unknown tool: {tool_name}"})
