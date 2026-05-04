"""Core agentic loop for the multi-phase extraction pipeline."""

import asyncio
import json
import logging

from openai import AsyncOpenAI

from schemas import PHASES, METADATA_FIELDS
from pdf_index import PDFIndex
from tools import TOOL_DEFINITIONS, execute_tool
from prompts import build_system_prompt, build_phase_user_message, build_correction_message

MAX_TURNS_PER_PHASE = 10
MAX_PHASE_RETRIES = 3

logger = logging.getLogger(__name__)


def _parse_phase_response(phase_idx: int, content: str) -> dict | None:
    """Parse JSON response for a phase. Returns None on parse failure."""
    try:
        text = content.strip()
        if text.startswith("```"):
            import re
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
            text = text.strip()
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def _validate_phase_fields(phase_idx: int, data: dict) -> list[str]:
    """Return list of missing fields for this phase."""
    phase = PHASES[phase_idx]
    missing = []
    for field in phase["fields"]:
        if field not in data:
            missing.append(field)
    return missing


def _verify_all_evidence(extracted: dict, index: PDFIndex) -> dict[str, dict]:
    """Verify evidence quotes against PDF. Returns {field: {"current": data, "error": detail}}.
    Only flags FABRICATED quotes (no similar text found); skips PARAPHRASED (partial match)."""
    failures = {}
    for field, data in extracted.items():
        if not isinstance(data, dict):
            continue
        value = data.get("value", "")
        evidence = data.get("evidence", "")
        page = data.get("page")
        if value.upper() in ("NO", "N/A") or not evidence.strip() or evidence.startswith("No evidence"):
            continue
        if page is None:
            continue
        result = index.verify_quote(evidence, page)
        if result["matched"]:
            continue
        # Only flag FABRICATED (no similar text); skip PARAPHRASED (partial match)
        detail = result.get("detail", "")
        if "No similar text found" in detail:
            failures[field] = {"current": data, "error": detail}
    return failures


def _parse_correction_response(content: str) -> dict | None:
    text = content.strip()
    if text.startswith("```"):
        import re
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


async def _run_correction(
    client: AsyncOpenAI,
    model: str,
    semaphore: asyncio.Semaphore,
    paper_id: str,
    messages: list[dict],
    failures: dict[str, dict],
) -> dict | None:
    """Send correction request for failing fields. Returns corrected fields or None."""
    correction_msg = build_correction_message(failures)
    messages.append({"role": "user", "content": correction_msg})
    try:
        async with semaphore:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=0,
            )
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg.model_dump())
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps({"status": "received"}),
                })
                if tc.function.name == "submit_result":
                    data = args.get("result", {})
                    if isinstance(data, str):
                        try:
                            data = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                    if isinstance(data, dict):
                        return data
            return None

        if msg.content:
            messages.append({"role": "assistant", "content": msg.content})
            return _parse_correction_response(msg.content)
    except Exception as e:
        logger.error("[%s] Correction request failed: %s", paper_id, e)
    return None


async def agent_loop(
    client: AsyncOpenAI,
    model: str,
    semaphore: asyncio.Semaphore,
    paper_id: str,
    index: PDFIndex,
) -> dict | None:
    """Run 6-phase extraction with tool-use agent loop."""
    all_extracted: dict = {}
    messages: list[dict] = [{"role": "system", "content": build_system_prompt()}]
    full_text = index.get_full_text()

    for phase_idx, phase in enumerate(PHASES):
        phase_result = await _run_phase(
            client, model, semaphore, paper_id, index,
            phase_idx, messages, full_text, all_extracted,
        )
        if phase_result is None:
            logger.error("[%s] Phase %d/%d (%s) FAILED after all retries",
                         paper_id, phase_idx, len(PHASES) - 1, phase["name"])
            return None
        if not isinstance(phase_result, dict):
            logger.error("[%s] Phase %d invalid result type: %s",
                         paper_id, phase_idx, type(phase_result).__name__)
            return None
        all_extracted.update(phase_result)
        logger.info("[%s] Phase %d/%d (%s) complete: %d fields",
                    paper_id, phase_idx, len(PHASES) - 1, phase["name"],
                    len(phase_result))

    # Post-extraction evidence verification
    failures = _verify_all_evidence(all_extracted, index)
    if failures:
        total_structured = sum(1 for v in all_extracted.values() if isinstance(v, dict))
        logger.info("[%s] Evidence verification: %d/%d fields failed",
                    paper_id, len(failures), total_structured)
        corrected = await _run_correction(
            client, model, semaphore, paper_id, messages, failures,
        )
        if corrected and isinstance(corrected, dict):
            fixed = 0
            for field in failures:
                if field in corrected and isinstance(corrected[field], dict):
                    all_extracted[field] = corrected[field]
                    fixed += 1
            logger.info("[%s] Correction: %d/%d fields fixed",
                        paper_id, fixed, len(failures))
            still_failing = _verify_all_evidence(
                {f: all_extracted[f] for f in failures if f in all_extracted},
                index,
            )
            if still_failing:
                logger.warning("[%s] %d fields still failing after correction: %s",
                               paper_id, len(still_failing), ", ".join(still_failing))
        else:
            logger.warning("[%s] Correction failed, keeping original values", paper_id)
    else:
        logger.info("[%s] Evidence verification: all quotes passed", paper_id)

    return all_extracted


async def _run_phase(
    client: AsyncOpenAI,
    model: str,
    semaphore: asyncio.Semaphore,
    paper_id: str,
    index: PDFIndex,
    phase_idx: int,
    messages: list[dict],
    full_text: str,
    extracted_so_far: dict,
) -> dict | None:
    for retry in range(MAX_PHASE_RETRIES):
        msg_count_before = len(messages)
        result = await _attempt_phase(
            client, model, semaphore, paper_id, index,
            phase_idx, messages, full_text, extracted_so_far,
        )
        if result is not None:
            return result
        if retry < MAX_PHASE_RETRIES - 1:
            logger.warning("[%s] Phase %d retry %d/%d",
                           paper_id, phase_idx, retry + 1, MAX_PHASE_RETRIES - 1)
            while len(messages) > msg_count_before:
                messages.pop()
    return None


async def _attempt_phase(
    client: AsyncOpenAI,
    model: str,
    semaphore: asyncio.Semaphore,
    paper_id: str,
    index: PDFIndex,
    phase_idx: int,
    messages: list[dict],
    full_text: str,
    extracted_so_far: dict,
) -> dict | None:
    user_msg = build_phase_user_message(phase_idx, full_text, extracted_so_far)
    messages.append({"role": "user", "content": user_msg})
    turn = 0

    while turn < MAX_TURNS_PER_PHASE:
        turn += 1
        async with semaphore:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=0,
            )

        choice = response.choices[0] if response.choices else None
        if choice is None:
            logger.warning("[%s] Phase %d turn %d: empty API response", paper_id, phase_idx, turn)
            messages.append({"role": "assistant", "content": ""})
            messages.append({"role": "user", "content": "Error: empty response. Please return JSON with all fields."})
            continue
        assistant_msg = choice.message

        if assistant_msg.tool_calls:
            messages.append(assistant_msg.model_dump())
            submit_data = None
            for tc in assistant_msg.tool_calls:
                args = json.loads(tc.function.arguments)
                if tc.function.name == "submit_result":
                    submit_data = args.get("result", {})
                    logger.info("[%s] Phase %d turn %d: submit_result called", paper_id, phase_idx, turn)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps({"status": "received"}),
                    })
                else:
                    logger.warning("[%s] Phase %d turn %d: unknown tool %s, sending error response",
                                   paper_id, phase_idx, turn, tc.function.name)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps({"error": f"Unknown tool: {tc.function.name}"}),
                    })

            if submit_data is not None:
                # Handle case where LLM passes JSON string instead of dict
                if isinstance(submit_data, str):
                    try:
                        submit_data = json.loads(submit_data)
                    except json.JSONDecodeError:
                        logger.warning("[%s] Phase %d submit_result: invalid JSON string", paper_id, phase_idx)
                        messages.append({"role": "user", "content": "Error: result must be a JSON object, not a string."})
                        continue
                logger.info("[%s] Phase %d submit_result data: %s",
                            paper_id, phase_idx, str(submit_data)[:300])
                missing = _validate_phase_fields(phase_idx, submit_data)
                if not missing:
                    logger.info("[%s] Phase %d done via submit_result: %d turns",
                                paper_id, phase_idx, turn)
                    return submit_data
                logger.warning("[%s] Phase %d submit_result missing fields: %s",
                               paper_id, phase_idx, ", ".join(missing))
                messages.append({
                    "role": "user",
                    "content": f"Error: missing fields: {', '.join(missing)}. Please return JSON with ALL fields.",
                })
                continue

            logger.info("[%s] Phase %d turn %d: %s", paper_id, phase_idx, turn,
                        ", ".join(tc.function.name for tc in assistant_msg.tool_calls))
            continue

        # No tool calls — LLM returned text (should be JSON)
        if assistant_msg.content is None:
            logger.warning("[%s] Phase %d turn %d: empty response", paper_id, phase_idx, turn)
            messages.append({"role": "assistant", "content": ""})
            messages.append({"role": "user", "content": "Error: empty response. Please return JSON with all fields."})
            continue

        messages.append({"role": "assistant", "content": assistant_msg.content})
        parsed = _parse_phase_response(phase_idx, assistant_msg.content)

        if parsed is None:
            logger.warning("[%s] Phase %d turn %d: invalid JSON", paper_id, phase_idx, turn)
            messages.append({"role": "user", "content": "Error: invalid JSON. Please return valid JSON."})
            continue

        missing = _validate_phase_fields(phase_idx, parsed)
        if missing:
            logger.warning("[%s] Phase %d turn %d: missing fields: %s",
                           paper_id, phase_idx, turn, ", ".join(missing))
            messages.append({
                "role": "user",
                "content": f"Error: missing fields: {', '.join(missing)}. Please return JSON with ALL fields for this phase.",
            })
            continue

        logger.info("[%s] Phase %d done: %d turns", paper_id, phase_idx, turn)
        return parsed

    logger.error("[%s] Phase %d exhausted after %d turns",
                 paper_id, phase_idx, turn)
    return None
