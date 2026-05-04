"""Tests for prompts.py."""

import pytest
from prompts import build_system_prompt, build_phase_user_message


class TestBuildSystemPrompt:
    def test_contains_role_description(self):
        prompt = build_system_prompt()
        assert "学术论文评价方法论提取助手" in prompt

    def test_contains_tool_instructions(self):
        prompt = build_system_prompt()
        assert "submit_result" in prompt
        assert "逐字" in prompt

    def test_contains_evidence_rules(self):
        prompt = build_system_prompt()
        assert "verbatim" in prompt.lower() or "逐字" in prompt

    def test_contains_all_field_definitions(self):
        from schemas import METADATA_FIELDS, STRUCTURED_FIELDS
        prompt = build_system_prompt()
        for field in METADATA_FIELDS + STRUCTURED_FIELDS:
            assert field in prompt, f"Field {field} not in system prompt"

    def test_contains_json_format(self):
        prompt = build_system_prompt()
        assert "JSON" in prompt


class TestBuildPhaseUserMessage:
    def test_phase_0_contains_full_text(self):
        full_text = "--- Page 1 ---\nSample content"
        msg = build_phase_user_message(0, full_text=full_text, extracted_so_far={})
        assert "--- Page 1 ---" in msg

    def test_phase_0_contains_metadata_instruction(self):
        msg = build_phase_user_message(0, full_text="text", extracted_so_far={})
        assert "元数据" in msg

    def test_phase_1_contains_field_names(self):
        from schemas import PHASES
        msg = build_phase_user_message(1, full_text="text", extracted_so_far={})
        for field in PHASES[1]["fields"]:
            assert field in msg

    def test_phase_1_contains_tool_instruction(self):
        msg = build_phase_user_message(1, full_text="text", extracted_so_far={})
        assert "工具" in msg or "tool" in msg.lower()

    def test_later_phase_contains_extracted_so_far(self):
        extracted = {"title": "Test Paper", "year": 2024}
        msg = build_phase_user_message(2, full_text="text", extracted_so_far=extracted)
        assert "Test Paper" in msg

    def test_all_phases_produce_non_empty_messages(self):
        for phase_idx in range(6):
            msg = build_phase_user_message(phase_idx, full_text="text", extracted_so_far={})
            assert len(msg) > 50, f"Phase {phase_idx} message too short"
