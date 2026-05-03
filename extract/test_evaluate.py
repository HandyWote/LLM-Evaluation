import json
import pytest
from evaluate import parse_llm_response, build_csv_row, generate_markdown


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
        "interaction_level": _make_field("Extended"),
        "prompt_disclosure": _make_field("Partial"),
        "theoretical_grounding": _make_field("Weak"),
        "inter_rater_reliability": _make_field("No"),
        "defects": {"value": ["lacks evaluation rubric"], "evidence": "test", "page": 5, "confidence": 70},
    }
    base.update(overrides)
    return json.dumps(base)


def test_parse_valid_response():
    raw = _make_full_response()
    result = parse_llm_response(raw)
    assert result["title"] == "Test Paper"
    assert result["eval_human_experts"]["value"] == "YES"
    assert result["eval_lay_users"]["value"] == "NO"
    assert result["interaction_level"]["value"] == "Extended"
    assert result["defects"]["value"] == ["lacks evaluation rubric"]


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


def test_parse_defects_caps_at_two():
    three_defects = ["lacks evaluation rubric", "limited sample size", "participant expertise unclear"]
    raw = _make_full_response(defects={"value": three_defects, "evidence": "t", "page": 1, "confidence": 70})
    result = parse_llm_response(raw)
    assert len(result["defects"]["value"]) == 2


def test_parse_defects_filters_invalid():
    raw = _make_full_response(defects={"value": ["not a real defect"], "evidence": "t", "page": 1, "confidence": 70})
    result = parse_llm_response(raw)
    assert result["defects"]["value"] == ["lacks evaluation rubric"]


def _make_parsed():
    return parse_llm_response(_make_full_response())


def test_build_csv_row():
    parsed = _make_parsed()
    row = build_csv_row("28", parsed)
    assert row["id"] == "28"
    assert row["eval_human_experts"] == "YES"
    assert row["eval_lay_users"] == "NO"
    assert row["interaction_level"] == "Extended"
    assert row["defects"] == "lacks evaluation rubric"


def test_generate_markdown_contains_title():
    parsed = _make_parsed()
    md = generate_markdown("28", parsed)
    assert "Test Paper" in md
    assert "eval_human_experts" in md
    assert "confidence" in md
    assert "Evidence" in md


def test_generate_markdown_shows_page():
    parsed = _make_parsed()
    md = generate_markdown("28", parsed)
    assert "p.1" in md
