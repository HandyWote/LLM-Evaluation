# Codebook Website (`web/`)

A static, dependency-free single-page site that browses the paper's codebook
(7 groups / 40 coding fields) and the coded corpus. Everything is computed from
the repository's authoritative files by `web/build/build_data.py`; nothing is
hard-coded into the HTML.

## Local preview

The page reads a single generated bundle (`web/data/data.js`) that assigns
`window.SURVEY_DATA`, so it also works from `file://` (no `fetch()` needed).

- **Double-click** `web/index.html` (open it directly in a browser), or
- Serve it over HTTP from the `web/` directory:

  ```bash
  cd web
  python3 -m http.server 8000
  # then open http://localhost:8000/
  ```

## Page structure and presentation

**Single page.** `web/index.html` is the only page of the site. There is no
second page: the former companion page has been retired and is no longer
published. The page carries no search box, no filter bar and no download UI.

The page is one linear document: seven stacked tables (G1–G6 = 52 paper rows
each, G7 = 52 claim rows) under a sticky jump bar, with column-header definition
popovers and a tally footer row per table.

- **Numbering.** The `#` column is a positional index (1…52), not a source
  identifier; internal `Paper_ID` values are never displayed.
- **Tables G1–G6.** One row per paper, one column per coded field. Long free-text
  cells expand on click; the `Tally · all 52 papers` footer row is computed over
  all 52 papers.
- **Table G7 (claim–evidence alignment).** One row per *paper* with four data
  columns: `C1`, `C1 value`, `C2`, `C2 value` — the claim sentence as coded plus
  its final alignment verdict (`ALIGNED` / `PARTIAL` / `EXCEEDS` / `UNCLEAR`).
  C2 is shown only where the paper makes an explicit extension beyond C1, so 20
  of the 52 rows carry a C2. The footer row tallies the 72 claim slots
  (C1 = 52 slots, C2 = 20 slots). Review-flag, evidence-quote and page-link
  columns are not rendered.
- **No exploration UI.** No search box, no filter selects and no download links:
  the page is meant to be read top to bottom.
- **Palette.** Every colour comes from the four CSS variables declared in
  `:root` of `assets/styles.css` (the site's only stylesheet): `--brand-base
  #EFECE3`, `--brand-mid #8FABD4`, `--brand-accent #4A70A9`, `--brand-ink
  #000000`. The Yes/No marks keep their semantic colours
  (`#16a34a` / `#dc2626`) independently of the palette.

## Regenerating the data

```bash
python3 web/build/build_data.py
```

This writes / overwrites `web/data/` and `web/downloads/`:

| Output | Contents |
| --- | --- |
| `data/codebook.json` | 7 groups × 40 fields: name, verbatim allowed-values string, type, definition, and `gate` metadata where the field is conditional |
| `data/papers.json` | 52 papers × 38 paper-level values plus `Author_Year` (display citation, e.g. "Chandra et al., 2025") — see below |
| `data/claims.json` | 72 claim–evidence rows (52 papers) with final alignment plus `Author_Year`, `Paper_URL` / `Claim_URL` / `Evidence_URL` deep links and top-level URL counts |
| `data/stats.json` | Overview counts / legacy `funnel` / **non-nested `behavioral_validity`** / **`gated`** / **`reliability_reporting`** / **`clinical_theory`** / distributions |
| `data/data.js` | All of the above as one `window.SURVEY_DATA` bundle |
| `downloads/final-table.csv` | Byte-for-byte copy of `compare/final-table.csv` (G1–G6 coded corpus) |
| `downloads/theory_eval_refined_coding_refined.csv` | Byte-for-byte copy of `table/theory_eval_refined_coding_refined.csv` (G5 theory fields) |
| `downloads/claim_level_FINAL_analysis_ready.csv` | Byte-for-byte copy of `compare/claim_level_FINAL_analysis_ready.csv` (G7 claim–evidence) |
| `downloads/09_appendices.tex` | Byte-for-byte copy of `docs/09_appendices.tex` (codebook definitions) |

The script is read-only with respect to its inputs: it never modifies the CSV
or TeX files below. It only reads them and writes JSON under `web/data/` plus
byte-for-byte copies under `web/downloads/` (no header is injected, so the
bundled files are identical to the released archival files). The copies under
`web/downloads/` are kept for release purposes but are **no longer linked from
the page** (the page carries no download UI).
**Run it again whenever a source file changes**, and make sure
`web/data/data.js` exists before deploying — the deployment workflow
(`.github/workflows/pages.yml`) runs the script in CI and uploads `web/` as the
Pages artifact.

## Data sources

| Part of the site | Source file |
| --- | --- |
| G1–G6 paper-level coding | `compare/final-table.csv` |
| G5 theory fields (`Theory_Grounding`, `Theory_Operationalized_In_Evaluation`, `Theory_Eval_Type`) | `table/theory_eval_refined_coding_refined.csv` |
| G7 claim–evidence alignment (72 rows / 52 papers) | `compare/claim_level_FINAL_analysis_ready.csv` |
| Field names, allowed values, definitions, group structure | `docs/09_appendices.tex` (`\section{Coding Scheme}`) |

Two notes on the mapping implemented in `build_data.py`:

- The G5 theory fields are taken from `table/theory_eval_refined_coding_refined.csv`
  because the theory columns in `compare/final-table.csv` hold outdated values
  and lack `Theory_Eval_Type`. This override makes the site match the paper's
  `tab:theory-stats`.
- `compare/final-table.csv` spells one column `Interention_Sensitivity` (missing
  a "v"); the script maps it to the codebook field `Intervention_Sensitivity`.
  The file itself is left untouched.

## Normalization, gating, and derived statistics

### Value normalization (`papers.json`)

- Fields whose codebook `type` is `boolean` or `single-choice` are rewritten to
the codebook's canonical spelling using a case- and whitespace-insensitive
match against the verbatim `values` string. The concrete effect is
`Uses_Dynamic_State` `NO` → `No`, giving `{No: 39, Yes: 13}`; interaction
levels, behaviour depth, prompt disclosure, theory grounding/operationalization,
etc. already match. The verbatim `values` string in `codebook.json` is never
changed.
- Values that are *not* a case/whitespace variant of a listed option are kept
exactly as reported (e.g. `Reliability_Reported = 'N/A'`, free-text
`Clinical_Theory`, `Prompt_Disclosure = 'Full Disclosure'`).
- `Reliability_Reported` (`Yes / No / N/A`) is inferred as `single-choice`, not
`boolean`, because it has three values.

### Gated fields (`codebook.json` + `stats.gated`)

- `LLM_Judge_Validated` is gated on `Eval_LLM_Judge = Yes` and
`Reliability_Reported` is gated on `Has_Rubric = Yes`. Each carries a `gate`
object (`gate_field`, `gate_value`, `gate_note`) in `codebook.json`.
- `stats.gated` reports the conditional counts the paper uses — LLM-judge
validation `23/30`, rubric reliability `13/45` — and exposes the unconditional
counts (`24`, `16`) separately as `unconditional_n`. The notes state that an
unconditional count must never be shown without its denominator.
- `stats.reliability_reporting` gives both views:
`value_counts = {Yes: 16, No: 34, N/A: 2}` and
`with_rubric = {denominator: 45, Yes: 13, No: 31, N/A: 1}`.

### Behavioral validity (`stats.behavioral_validity`)

The three criteria are **not nested**. The script emits one object with:

- `criteria` — `extended_dialogue` (`Interaction_Level = 'Extended Dialogue'`, n=31),
  `dynamic_state` (`Uses_Dynamic_State = 'Yes'`, n=13),
  `longitudinal` (`Has_Longitudinal_Eval = 'Yes'`, n=3), each with its codebook
  definition;
- `combinations` — all 8 Yes/No triples with `n` and `paper_ids`
  (`FFF=18, FFT=1[34], FTF=1[65], FTT=1[111], TFF=20, TFT=0, TTF=10, TTT=1[13]`);
- `pairwise` — the three pairwise intersections (`both` / `only_a` / `only_b` / `neither`);
- `caveats` — explicit statements that the criteria are independent, naming the
  counterexamples (65 and 111 have a dynamic state but are not extended
dialogues; 34 and 111 are longitudinal but not extended dialogues) and the paper
  Sec. 4.2 point that a longer dialogue does not itself provide trajectory-level
  evidence.

The legacy nested `stats.funnel` array is kept only for compatibility; the site
renders `behavioral_validity` instead.

### Clinical theory (`stats.clinical_theory`)

The free-text `Clinical_Theory` strings are split on `;`, `,`, `+`, `/`, `、`
and ` and `, de-duplicated per paper, and matched (case-insensitively) against a
documented alias table in `build_data.py`. Output:

- `denominator: 52`, `multi_label: true` — families may sum above 52;
- `families: [{name, n, paper_ids}]` (CBT, motivational interviewing, DBT,
  problem-solving therapy, working alliance, person-centered/Rogers, narrative
  therapy/IMCS, diagnostic manuals & symptom scales, crisis & suicide-risk
  approaches, Big Five, emotion/empathy constructs, clinical guidelines & exams);
- `unclassified: {n, paper_ids}` for fragments that match no family and
  `not_specified: {n: 1, paper_ids: ['29']}`;
- `raw: [{value, n, paper_ids}]` — the unmodified reported strings, kept so the
  site can show them next to the canonical families;
- `mapping_note` — the grouping rule, shown in the UI caption.

### Claim page-level links (`claims.json`)

Each claim slot gains `Paper_URL` (from the paper's Bibtex: `eprint` →
`https://arxiv.org/abs/<eprint>`, else `url`, else `doi` →
`https://doi.org/<doi>`), plus `Claim_URL` / `Evidence_URL`. Deep links add
`#page=N` using `Claim_Page` / `Evidence_Page`: arXiv →
`https://arxiv.org/pdf/<id>#page=N`, `aclanthology.org` URLs ending in `/` →
`<url>.pdf#page=N`, URLs already ending in `.pdf` → append `#page=N`, and all
other hosts (DOI landing pages, journal HTML) fall back to the plain URL. An
`eprint` is only used when it is a syntactically valid arXiv id, so malformed
placeholder values (e.g. Paper 77) never produce a fabricated arXiv link. No URL
is fabricated: top-level `papers_with_url` / `papers_without_url`
(`papers_without_url_ids`) report the one paper (Paper_ID 45) whose Bibtex has
neither `eprint`, `url` nor `doi`, and its slot keeps empty URL fields.

## Do not modify the source files

`compare/final-table.csv`, `table/theory_eval_refined_coding_refined.csv`,
`compare/claim_level_FINAL_analysis_ready.csv` and `docs/09_appendices.tex` are **archival
records** of the coding / adjudication work and the submitted appendix. They are
kept exactly as they are; any transformation (spelling normalisation, G5
override, metadata stripping) happens at build time inside
`web/build/build_data.py`.

If a value looks wrong, change the script or add a new file — do not edit these
four files in place.
