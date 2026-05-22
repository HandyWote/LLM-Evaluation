import json
import pytest
from evaluate.evaluate import parse_llm_response, build_csv_row, generate_markdown


def _make_field(value, evidence="test evidence", page=1, confidence=80):
    return {"value": value, "evidence": evidence, "page": page, "confidence": confidence}


def _make_full_response(**overrides):
    base = {
        "title": "Test Paper",
        "eval_human_experts": _make_field("YES"),
        "eval_lay_users": _make_field("NO"),
        "eval_user_study": _make_field("YES"),
        "eval_llm_judge": _make_field("NO"),
        "eval_automatic": _make_field("YES"),
        "dim_realism": _make_field("NO"),
        "dim_consistency": _make_field("YES"),
        "dim_fidelity": _make_field("NO"),
        "dim_utility": _make_field("YES"),
        "dim_human_learning": _make_field("NO"),
        "dim_emotional_plausibility": _make_field("YES"),
        "dim_safety": _make_field("NO"),
        "interaction_level": _make_field("Extended Dialogue"),
        "prompt_disclosure": _make_field("Partial"),
        "theory_grounding": _make_field("Weak"),
        "reliability_reported": _make_field("No"),
        "coding_options": _make_field("No"),
    }
    base.update(overrides)
    return json.dumps(base)


def test_parse_valid_response():
    raw = _make_full_response()
    result = parse_llm_response(raw)
    assert result["title"] == "Test Paper"
    assert result["eval_human_experts"]["value"] == "YES"
    assert result["eval_lay_users"]["value"] == "NO"
    assert result["interaction_level"]["value"] == "Extended Dialogue"


def test_parse_strips_code_fences():
    raw_json = _make_full_response()
    raw = f"```json\n{raw_json}\n```"
    result = parse_llm_response(raw)
    assert result["title"] == "Test Paper"


def test_parse_clamps_confidence():
    raw = _make_full_response(eval_human_experts=_make_field("YES", confidence=150))
    result = parse_llm_response(raw)
    assert result["eval_human_experts"]["confidence"] == 100


def test_parse_invalid_bool_defaults_to_no():
    raw = _make_full_response(eval_human_experts=_make_field("MAYBE"))
    result = parse_llm_response(raw)
    assert result["eval_human_experts"]["value"] == "NO"


def test_parse_invalid_single_choice_uses_last_default():
    raw = _make_full_response(interaction_level=_make_field("Invalid"))
    result = parse_llm_response(raw)
    assert result["interaction_level"]["value"] == "Longitudinal"


def test_build_csv_row():
    parsed = parse_llm_response(_make_full_response())
    row = build_csv_row("28", parsed)
    assert row["Paper_ID"] == "28"
    assert row["Eval_Human_Experts"] == "YES"
    assert row["Eval_Lay_Users"] == "NO"
    assert row["Interaction_Level"] == "Extended Dialogue"


def test_generate_markdown_contains_title():
    parsed = parse_llm_response(_make_full_response())
    md = generate_markdown("28", parsed)
    assert "Test Paper" in md
    assert "eval_human_experts" in md
    assert "confidence" in md
    assert "Evidence" in md


def test_generate_markdown_shows_page():
    parsed = parse_llm_response(_make_full_response())
    md = generate_markdown("28", parsed)
    assert "p.1" in md
