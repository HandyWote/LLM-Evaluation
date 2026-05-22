"""Tests for notes.py."""

import tempfile
from pathlib import Path

from note.notes import (
    append_notes,
    build_notes_section,
    build_system_prompt,
    build_user_message,
    has_notes_section,
    load_existing_note_ids,
    parse_id,
    strip_response,
)


def test_has_notes_section__no_section():
    content = "# Paper 1\n## 基础元数据\nsome content"
    assert has_notes_section(content) is False


def test_has_notes_section__has_section():
    content = "# Paper 1\n## 基础元数据\nsome content\n## 研究笔记\nnotes here"
    assert has_notes_section(content) is True


def test_has_notes_section__partial_match():
    """## 研究笔记总结 should NOT match"""
    content = "# Paper 1\n## 研究笔记总结\nnotes here"
    assert has_notes_section(content) is False


def test_parse_id__numeric():
    assert parse_id("1.pdf") == "1"
    assert parse_id("83.pdf") == "83"


def test_parse_id__non_numeric():
    assert parse_id("abc.pdf") == "abc"


def test_append_notes__new_content():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# Paper 1\n## 基础元数据\nsome content\n")
        path = Path(f.name)
    try:
        notes_text = "## 研究笔记\n\n### 概括\ncontent here"
        append_notes(path, notes_text)
        result = path.read_text(encoding="utf-8")
        assert result.endswith("## 研究笔记\n\n### 概括\ncontent here\n")
        assert "## 研究笔记" in result
    finally:
        path.unlink()


def test_build_notes_section__format():
    notes = "这里是一段笔记内容"
    result = build_notes_section(notes)
    assert result.startswith("\n## 研究笔记\n\n")
    assert "这里是一段笔记内容" in result
    assert result.endswith("\n")


def test_build_system_prompt__content():
    prompt = build_system_prompt()
    assert "元评测" in prompt
    assert "研究笔记" in prompt
    assert "评估方法" in prompt


def test_build_user_message__sections():
    coding_table = "这是评估维度表"
    eval_report = "## 基础元数据\n- Year: 2024"
    pdf_text = "论文全文内容..."
    msg = build_user_message(coding_table, eval_report, pdf_text)
    assert "评估维度表" in msg
    assert "## 基础元数据" in msg
    assert "论文全文内容..." in msg
    assert "概括" in msg
    assert "评价" in msg


def test_build_user_message__chinese():
    """User message should be in Chinese."""
    msg = build_user_message("", "", "")
    assert "研究目标" in msg
    assert "方法概述" in msg
    assert "主要结果" in msg


def test_load_existing_note_ids__no_files(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    assert load_existing_note_ids(reports_dir) == set()


def test_load_existing_note_ids__with_notes(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    # Paper 1 has notes section
    (reports_dir / "1.md").write_text("# Paper 1\n## 研究笔记\nnotes", encoding="utf-8")
    # Paper 2 has no notes section
    (reports_dir / "2.md").write_text("# Paper 2\n## 基础元数据", encoding="utf-8")
    assert load_existing_note_ids(reports_dir) == {"1"}


def test_load_existing_note_ids__empty_file(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "1.md").write_text("", encoding="utf-8")
    assert load_existing_note_ids(reports_dir) == set()


def test_strip_response__no_fences():
    assert strip_response("hello") == "hello"


def test_strip_response__with_fences():
    assert strip_response("```markdown\nhello\n```") == "hello"


def test_strip_response__with_language_tag():
    assert strip_response("```md\nhello\n```") == "hello"
