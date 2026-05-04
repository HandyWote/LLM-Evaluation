---
name: verify-eval-extraction
description: Verify LLM-extracted evaluation methodology results against original PDFs. Use when the user asks to verify, validate, or check the quality of extraction results from evaluate.py — specifically whether evidence quotes are verbatim from the source papers and whether judgment values are correct. Also use when the user says "验证", "核对", "检查提取结果", "verify extraction", or references eval_reports/*.md quality.
---

# Verify Eval Extraction Results

You are verifying the output of `extract/evaluate.py` against the original PDFs. The goal is to check two things:

1. **Verbatim accuracy**: Every evidence quote in the Markdown reports must be an exact word-for-word quote from the PDF — no paraphrasing, summarizing, or fabrication.
2. **Judgment correctness**: The YES/NO/single-choice values should be reasonable given the paper content.

## Workflow

### Step 1: Determine scope and run verification script

Run the verification script from the project root. The script extracts PDF text, parses the Markdown reports, and checks every evidence claim against the original paper.

```bash
# Single paper
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py 1

# Multiple papers
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py 1 28 35

# All papers in eval_reports/
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py --all
```

The script outputs JSON. Save it to a variable or file for Step 2.

### Step 2: Present evidence verification results

For each paper, format the JSON results into a table:

```
## Verification: Paper {id} — {title}

### Evidence Accuracy

| Field | Value | Quality | Page Match | Issue |
|-------|-------|---------|------------|-------|
| eval_human_experts | YES | EXACT | ✅ p.5 | |
| eval_lay_users | NO | TEMPLATE | N/A | |
| dim_consistency | YES | PARAPHRASED | — | partial: "consistent and logical" but changed subject |
| dim_utility | YES | FABRICATED | — | NOT FOUND in PDF |
| ... | | | | |
```

Quality labels:
- **EXACT** — verbatim match found
- **TEMPLATE** — NO field using standard template text
- **PARAPHRASED** — partial match found, but full quote not verbatim (detail shows what matched and what didn't)
- **FABRICATED** — quote not found in PDF at all

Page Match column:
- ✅ — evidence found on the claimed page
- ❌ p.X→p.Y — evidence found but on a different page
- — — not applicable (TEMPLATE/PARAPHRASED/FABRICATED)

### Step 3: Review judgment correctness

The script outputs `judgment_hints` — extracted snippets from the PDF containing keywords relevant to tricky fields. Use these snippets to assess:

- **`reliability_reported`**: Does the paper report a *standardized statistical coefficient* (Cohen's kappa, Krippendorff's alpha, ICC), or just average differences / standard deviations / percentage agreement? Yes = coefficient reported, No = human eval exists but no coefficient, N/A = no human eval at all.
- **`coding_options`**: Is there explicit inter-annotator agreement data reported? Yes = agreement explicitly reported, No = human eval but no agreement data, N/A = no human eval.
- **`eval_llm_judge`**: Is the LLM actually *scoring/comparing* outputs, or just being used for feature extraction / data generation?
- **`llm_judge_validated`**: Is there evidence of *validating* the LLM judge against human ratings (e.g. correlation, agreement scores)?
- **`theory_grounding`**: Is the evaluation grounded in validated instruments/theories with proper operationalization, or just mentioning concepts? Strong = evaluation criteria derived from theory, Weak = theory mentioned but not operationalized, None = no theory reference.
- **`prompt_disclosure`**: Are the actual prompts included in the paper or appendix? Full = complete prompts visible, Partial = fragments or description only, No = no prompts shared.

If `judgment_hints` is empty for a field, that means no relevant keywords were found — the field's judgment is likely correct but you should note low confidence.

Format the review:

```
### Judgment Review

| Field | Extracted | Verified | Note |
|-------|-----------|----------|------|
| reliability_reported | No | No | Reports Avg.Diff/Std.Dev, not kappa/alpha |
| coding_options | No | No | Uses human eval but no agreement data |
| eval_llm_judge | YES | YES | GPT-4 scores empathy on 1-5 Likert scale |
| llm_judge_validated | NO | — | No LLM judge validation found |
| theory_grounding | Weak | Weak | Mentions CBT but not operationalized in eval |
| prompt_disclosure | Partial | Partial | Prompts described but not fully shown |
```

### Step 4: Summary

For each paper:
```
Paper {id}: {exact_count} EXACT, {para_count} PARAPHRASED, {fab_count} FABRICATED, {tpl_count} TEMPLATE
Judgment corrections needed: {count}
```

For batch verification, also output:
```
## Batch Summary

| Paper | EXACT | PARAPHRASED | FABRICATED | TEMPLATE | Page Wrong | Judgment Fix |
|-------|-------|-------------|------------|----------|------------|--------------|
| 1     | 14    | 3           | 0          | 0        | 1          | 1            |
| 28    | 16    | 1           | 0          | 0        | 0          | 0            |
```

## Tips

- The script handles PDF hyphenation artifacts (e.g., `psy-\nchological` → `psychological`) via whitespace normalization.
- Evidence with `...` is split into parts and each part is verified independently.
- The current schema has 39 structured fields across 5 categories: simulation modeling, eval methods, eval dimensions, eval depth, reliability, and quality markers.
- Focus judgment review on the six tricky fields — the script provides hints so you don't need to read the full PDF.
- If a paper's PDF or report is missing, the script reports an error — skip it and note it in the summary.
