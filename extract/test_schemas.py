"""Tests for schemas.py constants."""

import pytest
from schemas import (
    CSV_COLUMNS, CSV_HEADER, INTERNAL_TO_CSV,
    METADATA_FIELDS, BOOL_FIELDS, SINGLE_CHOICE_FIELDS,
    FREE_TEXT_FIELDS, STRUCTURED_FIELDS,
    PHASES, FIELD_DEFINITIONS,
)


def test_csv_columns_count():
    assert len(CSV_COLUMNS) == 43


def test_csv_header_matches_columns():
    assert CSV_HEADER == [csv_name for _, csv_name in CSV_COLUMNS]


def test_internal_to_csv_round_trip():
    for internal, csv_name in CSV_COLUMNS:
        assert INTERNAL_TO_CSV[internal] == csv_name


def test_metadata_fields_in_columns():
    for f in METADATA_FIELDS:
        assert f in INTERNAL_TO_CSV


def test_bool_fields_all_yes_no():
    assert "eval_human_experts" in BOOL_FIELDS
    assert len(BOOL_FIELDS) == 24


def test_single_choice_fields_have_options():
    for field, options in SINGLE_CHOICE_FIELDS.items():
        assert len(options) >= 2
        assert field in INTERNAL_TO_CSV


def test_structured_fields_covers_all_non_metadata():
    all_schema_fields = set(BOOL_FIELDS) | set(SINGLE_CHOICE_FIELDS.keys()) | set(FREE_TEXT_FIELDS)
    assert set(STRUCTURED_FIELDS) == all_schema_fields
    assert "title" not in STRUCTURED_FIELDS
    assert "year" not in STRUCTURED_FIELDS


def test_phases_count():
    assert len(PHASES) == 6


def test_phases_cover_all_fields():
    phase_fields = []
    for phase in PHASES:
        phase_fields.extend(phase["fields"])
    assert len(phase_fields) == len(set(phase_fields)), "Duplicate field across phases"
    all_fields = set(METADATA_FIELDS) | set(STRUCTURED_FIELDS)
    assert set(phase_fields) == all_fields, f"Missing: {all_fields - set(phase_fields)}"


def test_phase_0_is_metadata():
    assert PHASES[0]["type"] == "metadata"
    assert set(PHASES[0]["fields"]) == set(METADATA_FIELDS)


def test_field_definitions_cover_all_fields():
    all_fields = set(METADATA_FIELDS) | set(STRUCTURED_FIELDS)
    assert set(FIELD_DEFINITIONS.keys()) == all_fields


def test_field_definitions_no_empty_strings():
    for field, defn in FIELD_DEFINITIONS.items():
        assert defn, f"Empty definition for {field}"
