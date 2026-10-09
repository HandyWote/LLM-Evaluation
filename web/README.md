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

## Regenerating the data

```bash
python3 web/build/build_data.py
```

This writes / overwrites `web/data/`:

| Output | Contents |
| --- | --- |
| `codebook.json` | 7 groups × 40 fields: name, allowed values, type, definition |
| `papers.json` | 52 papers × 40 fields (per-paper coded values) |
| `claims.json` | 72 claim–evidence rows (52 papers) with final alignment |
| `stats.json` | Overview counts / funnel / distributions for the charts |
| `data.js` | All of the above as one `window.SURVEY_DATA` bundle |

The script is read-only with respect to its inputs: it never modifies the CSV
or TeX files below, it only reads them and writes JSON under `web/data/`.
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

## Do not modify the source files

`compare/final-table.csv`, `table/theory_eval_refined_coding_refined.csv`,
`compare/claim_level_FINAL_analysis_ready.csv` and `docs/09_appendices.tex` are **archival
records** of the coding / adjudication work and the submitted appendix. They are
kept exactly as they are; any transformation (spelling normalisation, G5
override, metadata stripping) happens at build time inside
`web/build/build_data.py`.

If a value looks wrong, change the script or add a new file — do not edit these
four files in place.
