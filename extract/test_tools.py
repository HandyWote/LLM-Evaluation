"""Tests for tools.py."""

import json
import pytest
from unittest.mock import MagicMock

from pdf_index import PDFIndex
from tools import TOOL_DEFINITIONS, execute_tool


class MockIndex:
    def __init__(self):
        self._pages = [
            "This is page one. It discusses evaluation methods.\nThe paper uses BLEU and ROUGE for evaluation.",
            "Page two covers safety and realism.\nThey found that the model produces harmful output 5% of the time.",
            "Page three is about conclusion.\nThe authors recommend further work on empathy.",
        ]


@pytest.fixture
def idx():
    return MockIndex()


def test_tool_definitions_exist():
    assert len(TOOL_DEFINITIONS) == 1
    names = {t["function"]["name"] for t in TOOL_DEFINITIONS}
    assert names == {"submit_result"}


def test_tool_definitions_have_parameters():
    for tool in TOOL_DEFINITIONS:
        func = tool["function"]
        assert "parameters" in func
        assert func["parameters"]["type"] == "object"


def test_execute_submit_result(idx):
    result = execute_tool(idx, "submit_result", {"result": {"field": "value"}})
    parsed = json.loads(result)
    assert parsed["status"] == "received"


def test_execute_unknown_tool(idx):
    result = execute_tool(idx, "unknown_tool", {})
    assert "Unknown tool" in result
