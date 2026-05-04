"""Tests for agent_loop.py — uses mocked AsyncOpenAI client."""

import json
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from schemas import PHASES
from agent_loop import agent_loop


def _make_json_message(content: str):
    msg = MagicMock()
    msg.content = content
    msg.tool_calls = None
    return msg


def _make_tool_call_message(tool_calls: list[dict]):
    msg = MagicMock()
    msg.content = None
    msg.tool_calls = []
    for tc in tool_calls:
        mock_tc = MagicMock()
        mock_tc.id = tc["id"]
        mock_tc.type = "function"
        mock_tc.function.name = tc["name"]
        mock_tc.function.arguments = tc["args"]
        msg.tool_calls.append(mock_tc)
    return msg


def _make_response(message):
    resp = MagicMock()
    resp.choices = [MagicMock(message=message)]
    resp.usage = MagicMock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    return resp


def _make_structured(value="NO", evidence="No evidence found in the paper.", page=None, confidence=80):
    return {"value": value, "evidence": evidence, "page": page, "confidence": confidence}


def _phase_json(phase_idx: int) -> str:
    """Generate a valid JSON response for any phase."""
    phase = PHASES[phase_idx]
    data = {}
    if phase.get("type") == "metadata":
        data = {"title": "Test Paper", "year": 2024, "venue": "ACL", "domain": "Counseling"}
    else:
        for field in phase["fields"]:
            if field in ("raw_eval_metrics", "clinical_theory", "agreement_method",
                         "temporal_modeling_details", "focus_type"):
                data[field] = _make_structured(value="", evidence="No evidence found in the paper.")
            elif field == "simulation_target":
                data[field] = _make_structured(value="Client Agent")
            elif field == "persona_model_depth":
                data[field] = _make_structured(value="Surface Persona")
            elif field == "theory_operationalized":
                data[field] = _make_structured(value="None")
            elif field == "behavior_eval_depth":
                data[field] = _make_structured(value="None")
            elif field == "interaction_level":
                data[field] = _make_structured(value="Short")
            elif field == "prompt_disclosure":
                data[field] = _make_structured(value="No")
            elif field == "theory_grounding":
                data[field] = _make_structured(value="None")
            elif field in ("reliability_reported", "coding_options"):
                data[field] = _make_structured(value="N/A")
            else:
                data[field] = _make_structured()
    return json.dumps(data)


def _all_phases_responses(overrides: dict[int, list] | None = None) -> list:
    """Build response list for all 6 phases, with optional per-phase overrides.

    overrides: {phase_idx: [extra_responses_to_insert_after_user_msg]}
    For example, {1: [tool_call_response]} means phase 1 will have
    metadata response + tool_call + final_response instead of just final_response.
    """
    overrides = overrides or {}
    responses = []
    for phase_idx in range(6):
        phase_overrides = overrides.get(phase_idx, [])
        if phase_overrides:
            responses.extend(phase_overrides)
        responses.append(_make_response(_make_json_message(_phase_json(phase_idx))))
    return responses


class MockIndex:
    def __init__(self):
        from pdf_index import SearchResult
        self._pages = ["Page 1 text about evaluation.\nIt uses BLEU.", "Page 2 text about safety."]

    @property
    def page_count(self):
        return len(self._pages)

    def get_full_text(self):
        return "--- Page 1 ---\nPage 1 text about evaluation.\nIt uses BLEU.\n\n--- Page 2 ---\nPage 2 text about safety."

    def get_page(self, page_num):
        return self._pages[page_num - 1] if 1 <= page_num <= len(self._pages) else "Error"

    def search(self, query, top_k=5):
        from pdf_index import SearchResult
        results = []
        if "evaluation" in query.lower():
            results.append(SearchResult(page=1, text=query, context=self._pages[0][:100]))
        return results

    def verify_quote(self, quote, page_num):
        if 1 <= page_num <= len(self._pages) and quote in self._pages[page_num - 1]:
            return {"matched": True, "detail": "EXACT"}
        return {"matched": False, "detail": "No match"}


@pytest.fixture
def mock_client():
    client = MagicMock()
    return client


@pytest.fixture
def semaphore():
    return asyncio.Semaphore(3)


@pytest.mark.asyncio
async def test_phase0_metadata_no_tools(mock_client, semaphore):
    mock_client.chat.completions.create = AsyncMock(
        side_effect=_all_phases_responses()
    )
    index = MockIndex()
    result = await agent_loop(mock_client, "gpt-test", semaphore, "test-1", index)
    assert result is not None
    assert result["title"] == "Test Paper"
    assert result["year"] == 2024


@pytest.mark.asyncio
async def test_phase1_with_tool_calls(mock_client, semaphore):
    idx = MockIndex()
    custom_phase1 = [
        _make_response(_make_tool_call_message([
            {"id": "call_1", "name": "search_text", "args": '{"query": "evaluation"}'},
        ])),
    ]
    responses = _all_phases_responses(overrides={1: custom_phase1})
    mock_client.chat.completions.create = AsyncMock(side_effect=responses)

    result = await agent_loop(mock_client, "gpt-test", semaphore, "test-1", idx)
    assert result is not None
    assert result["focus_type"]["value"] == ""
    assert mock_client.chat.completions.create.call_count == 7  # 6 phases + 1 tool call


@pytest.mark.asyncio
async def test_phase_retry_on_missing_fields(mock_client, semaphore):
    idx = MockIndex()
    incomplete_json = json.dumps({"focus_type": _make_structured(value="EvaluationFramework")})

    custom_phase1 = [
        _make_response(_make_json_message(incomplete_json)),
    ]
    responses = _all_phases_responses(overrides={1: custom_phase1})
    mock_client.chat.completions.create = AsyncMock(side_effect=responses)

    result = await agent_loop(mock_client, "gpt-test", semaphore, "test-1", idx)
    assert result is not None
    assert "simulation_target" in result


@pytest.mark.asyncio
async def test_returns_none_on_phase_exhaustion(mock_client, semaphore):
    idx = MockIndex()
    incomplete_json = json.dumps({"focus_type": _make_structured(value="X")})

    # Provide only phase 0 response, then infinite incomplete responses for phase 1
    responses = [
        _make_response(_make_json_message(_phase_json(0))),
    ]
    # 10 turns per attempt * 3 retries = 30 incomplete responses for phase 1
    for _ in range(30):
        responses.append(_make_response(_make_json_message(incomplete_json)))

    mock_client.chat.completions.create = AsyncMock(side_effect=responses)

    result = await agent_loop(mock_client, "gpt-test", semaphore, "test-1", idx)
    assert result is None


@pytest.mark.asyncio
async def test_verify_quote_tool_execution(mock_client, semaphore):
    idx = MockIndex()

    custom_phase1 = [
        _make_response(_make_tool_call_message([
            {"id": "call_1", "name": "verify_quote", "args": '{"quote": "evaluation", "page_num": 1}'},
        ])),
    ]
    responses = _all_phases_responses(overrides={1: custom_phase1})
    mock_client.chat.completions.create = AsyncMock(side_effect=responses)

    result = await agent_loop(mock_client, "gpt-test", semaphore, "test-1", idx)
    assert result is not None
    assert mock_client.chat.completions.create.call_count == 7  # 6 phases + 1 tool call
