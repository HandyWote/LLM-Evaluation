"""Tests for pdf_index.py."""

import pytest
from pathlib import Path
from extract.pdf_index import PDFIndex, SearchResult


PAPER_DIR = Path(__file__).parent / "paper"


@pytest.fixture
def index():
    pdf_path = PAPER_DIR / "1.pdf"
    if not pdf_path.exists():
        pytest.skip("1.pdf not found in paper/")
    return PDFIndex(pdf_path)


class TestPDFIndexBasics:
    def test_page_count(self, index):
        assert index.page_count > 0

    def test_get_full_text_contains_page_markers(self, index):
        text = index.get_full_text()
        assert "--- Page 1 ---" in text

    def test_get_page_returns_string(self, index):
        page = index.get_page(1)
        assert isinstance(page, str)
        assert len(page) > 0

    def test_get_page_out_of_range(self, index):
        result = index.get_page(999)
        assert "Error" in result

    def test_get_page_one_indexed(self, index):
        page1 = index.get_page(1)
        page2 = index.get_page(2)
        assert page1 != page2


class TestSearch:
    def test_search_returns_results(self, index):
        results = index.search("evaluation", top_k=3)
        assert len(results) > 0
        for r in results:
            assert isinstance(r, SearchResult)
            assert isinstance(r.page, int)
            assert 1 <= r.page <= index.page_count
            assert isinstance(r.text, str)
            assert isinstance(r.context, str)

    def test_search_empty_query(self, index):
        results = index.search("", top_k=5)
        assert results == []

    def test_search_no_match(self, index):
        results = index.search("xyznonexistentterm12345", top_k=5)
        assert results == []

    def test_search_respects_top_k(self, index):
        results = index.search("the", top_k=2)
        assert len(results) <= 2


class TestVerifyQuote:
    def test_verify_exact_match(self, index):
        page_text = index.get_page(1)
        # Take first 50 chars as a known quote
        quote = page_text[:50].strip()
        result = index.verify_quote(quote, 1)
        assert result["matched"] is True
        assert result["detail"] == "EXACT"

    def test_verify_no_match(self, index):
        result = index.verify_quote("this text definitely does not exist in any paper", 1)
        assert result["matched"] is False

    def test_verify_wrong_page(self, index):
        page1_text = index.get_page(1)
        if index.page_count < 2:
            pytest.skip("Need at least 2 pages")
        page2_text = index.get_page(2)
        # Find text unique to page 1 and search on page 2
        quote = page1_text[:80].strip()
        result = index.verify_quote(quote, 2)
        assert result["matched"] is False

    def test_verify_page_out_of_range(self, index):
        result = index.verify_quote("some text", 999)
        assert result["matched"] is False
        assert "out of range" in result["detail"]

    def test_verify_whitespace_normalization(self, index):
        page_text = index.get_page(1)
        quote = page_text[:80].strip()
        # Find a space to split at so we don't break a word
        split_pos = quote.find(" ", 20)
        if split_pos == -1:
            pytest.skip("No space found for splitting")
        modified = quote[:split_pos] + "  \n  " + quote[split_pos:]
        result = index.verify_quote(modified, 1)
        assert result["matched"] is True
