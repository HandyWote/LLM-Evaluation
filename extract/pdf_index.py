"""PDF indexing and text search for the agentic extraction pipeline."""

import re
from dataclasses import dataclass, field
from pathlib import Path

import fitz


@dataclass
class SearchResult:
    page: int
    text: str
    context: str


def _clean_footnote_breaks(text: str) -> str:
    """修复被脚注编号打断的单词：pro-\\n1 Footnote text\\nfessional → professional。"""
    lines = text.split('\n')
    cleaned = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # 检测：当前行以数字开头（脚注），前一行以连字符结尾，后一行以小写字母开头
        if (re.match(r'^\d{1,2}\s', line.strip())
                and cleaned
                and cleaned[-1].rstrip().endswith('-')
                and i + 1 < len(lines)
                and lines[i + 1] and lines[i + 1][0].islower()):
            # 移除脚注行，拼接被打断的单词
            prev = cleaned.pop().rstrip()
            cleaned.append(prev[:-1] + lines[i + 1].lstrip())
            i += 2
            continue
        cleaned.append(line)
        i += 1
    return '\n'.join(cleaned)


def _normalize_whitespace(s: str) -> str:
    s = s.replace('’', "'").replace('‘', "'")  # 弯引号 → 直引号
    s = s.replace("“", '"').replace("”", '"')    # 弯双引号 → 直双引号
    s = re.sub(r'-\s+', '', s)  # 移除 PDF 行尾连字符（如 psychother-\napist → psychologist）
    s = s.replace('-', '')       # 移除所有剩余连字符（统一处理复合词，如 co-authors ↔ co- authors）
    return re.sub(r'\s+', ' ', s.strip().lower())


def _verify_single_quote(quote: str, normalized_page: str) -> dict:
    """Verify a single (non-segmented) quote against normalized page text."""
    normalized_quote = _normalize_whitespace(quote)
    if not normalized_quote:
        return {"matched": False, "detail": "Empty quote segment"}
    if normalized_quote in normalized_page:
        return {"matched": True, "detail": "EXACT"}
    return {"matched": False, "detail": "No similar text found"}


class PDFIndex:
    def __init__(self, pdf_path: Path):
        self._pages: list[str] = []
        self._full_text: str = ""
        doc = fitz.open(str(pdf_path))
        parts = []
        for page in doc:
            text = page.get_text()
            self._pages.append(text)
            parts.append(f"--- Page {len(self._pages)} ---\n{text}")
        doc.close()
        self._full_text = "\n\n".join(parts)

    @property
    def page_count(self) -> int:
        return len(self._pages)

    def get_full_text(self) -> str:
        return self._full_text

    def get_page(self, page_num: int) -> str:
        if 1 <= page_num <= len(self._pages):
            return self._pages[page_num - 1]
        return f"Error: Page {page_num} out of range (1-{len(self._pages)})"

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        query = query.strip()
        if not query:
            return []
        terms = query.split()
        pattern = r'\s+'.join(re.escape(t) for t in terms)
        regex = re.compile(pattern, re.IGNORECASE)
        results: list[SearchResult] = []
        for i, page_text in enumerate(self._pages):
            for match in regex.finditer(page_text):
                matched_text = match.group()
                start, end = match.span()
                ctx_start = max(0, start - 100)
                ctx_end = min(len(page_text), end + 100)
                context = page_text[ctx_start:ctx_end]
                results.append(SearchResult(
                    page=i + 1,
                    text=matched_text,
                    context=context,
                ))
        return results[:top_k]

    def verify_quote(self, quote: str, page_num: int) -> dict:
        if page_num < 1 or page_num > len(self._pages):
            return {"matched": False, "detail": f"Page {page_num} out of range (1-{len(self._pages)})"}
        page_text = self._pages[page_num - 1]
        cleaned_page = _clean_footnote_breaks(page_text)
        normalized_page = _normalize_whitespace(cleaned_page)

        # 支持 `...` 分段证据：按 `...` 拆分，每段独立验证
        segments = [s.strip() for s in quote.split("...") if s.strip()]
        if len(segments) > 1:
            return self._verify_segments(segments, normalized_page, page_text)
        return _verify_single_quote(quote, normalized_page)

    def _verify_segments(self, segments: list[str], normalized_page: str, page_text: str) -> dict:
        results = []
        all_matched = True
        for i, seg in enumerate(segments):
            r = _verify_single_quote(seg, normalized_page)
            results.append((seg, r))
            if not r["matched"]:
                all_matched = False

        if all_matched:
            return {"matched": True, "detail": f"EXACT (all {len(segments)} segments matched)"}

        failed = [f"seg[{i+1}]: {r['detail']}" for i, (_, r) in enumerate(results) if not r["matched"]]
        return {"matched": False, "detail": f"segmented evidence, {len(failed)}/{len(segments)} failed: " + "; ".join(failed)}
