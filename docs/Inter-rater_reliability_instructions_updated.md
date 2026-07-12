**Goal.** Assess the reliability of the literature coding by comparing
the two original independent coding sheets before discussion or
adjudication. The analysis will be used in the revised paper, so all
calculations must be reproducible and all scripts and intermediate files
must be retained.

**Important:** Use the two original independent coding sheets only. Do
not use the final merged or consensus coding sheet to compute agreement
or kappa.

# 1. Variables and statistics to compute

| **Coding dimension** | **Categories** | **Statistic** |
|----|----|----|
| Theory grounding | Strong / Partial / None | Linearly weighted Cohen’s kappa |
| Theory operationalization | Strong / Partial / None | Linearly weighted Cohen’s kappa |
| Dynamic state | Yes / No | Cohen’s kappa |
| Longitudinal evaluation | Yes / No | Cohen’s kappa |
| Intervention-sensitive evaluation | Yes / No | Cohen’s kappa |
| Human learning / outcomes | Yes / No | Cohen’s kappa |
| LLM-judge validation | Yes / No | Cohen’s kappa |

**Also compute raw agreement (%) for every variable.** Raw agreement is
the percentage of papers for which the two coders assigned exactly the
same label. Report it together with kappa because it is easy to
interpret and complements chance-corrected agreement.

# 2. Required workflow

**1. Align the two sheets.** Verify that both sheets contain the same 52
papers, in the same order, with matching paper identifiers and variable
names.

**2. Standardize labels.** Ensure labels are coded consistently, for
example Strong/Partial/None and Yes/No. Remove differences caused only
by spelling, capitalization, spaces, or abbreviations.

**3. Check missing data.** Identify blank or missing values. Do not
silently convert missing values to No or None. Report how missing
entries are handled for each variable.

**4. Compute raw agreement.** For each variable, calculate the number
and percentage of exact coder matches.

**5. Compute kappa.** Use standard Cohen’s kappa for binary variables
and weighted Cohen’s kappa for ordered three-level variables. State the
weighting scheme used; linear weights are recommended unless there is a
clear reason to use another scheme.

**6. Inspect disagreements.** Create a confusion matrix for each
variable and identify the most common disagreement types, such as Strong
versus Partial.

**7. Retain pre-adjudication results.** All agreement statistics must be
based on the original independent labels, before disagreements were
discussed or resolved.

**8. Document adjudication separately.** After reliability is computed,
describe how remaining disagreements were resolved to create the final
consensus coding used in the paper.

# 3. Final results table

| **Coding dimension** | **Categories** | **Statistic** | **Raw agreement (%)** | Kappa |
|----|----|----|----|----|
| Theory grounding | Strong / Partial / None | Linearly weighted Cohen’s kappa |  |  |
| Theory operationalization | Strong / Partial / None | Linearly weighted Cohen’s kappa |  |  |
| Dynamic state | Yes / No | Cohen’s kappa |  |  |
| Longitudinal evaluation | Yes / No | Cohen’s kappa |  |  |
| Intervention-sensitive evaluation | Yes / No | Cohen’s kappa |  |  |
| Human learning / outcomes | Yes / No | Cohen’s kappa |  |  |
| LLM-judge validation | Yes / No | Cohen’s kappa |  |  |

**Table note.** Agreement and kappa must be calculated from the original
independent coding before adjudication. Linearly weighted Cohen’s kappa
is used for ordinal variables; standard Cohen’s kappa is used for binary
variables.

# 4. Disagreement analysis

- For each variable, report the number of disagreements and the most
  frequent disagreement pair.

- For the two ordinal variables, distinguish adjacent disagreements
  (Strong vs. Partial; Partial vs. None) from extreme disagreements
  (Strong vs. None).

- Write a short interpretation of why the difficult cases were
  ambiguous. Do not change the original labels before computing
  reliability.

# 5. Deliverables

1.  Two cleaned and aligned pre-adjudication coding files.

2.  A reproducible Python or R script used to compute raw agreement,
    kappa, and confusion matrices.

3.  The completed reliability table shown above.

4.  Confusion matrices and a list of disagreement cases for the seven
    key variables.

5.  A short 1–2 paragraph methodological summary suitable for inclusion
    in the paper.

6.  A short note describing any missing data, label cleaning, or coding
    irregularities discovered.

# 6. Suggested reporting language for the revised paper

**Template:** “Two researchers independently coded all 52 papers using a
predefined 38-field codebook. Inter-rater agreement was assessed on the
original pre-adjudication labels. We report both raw agreement and
Cohen’s kappa, using weighted kappa for ordinal variables and standard
kappa for binary variables. Across the principal coding dimensions, raw
agreement ranged from XX% to XX%, and kappa ranged from XX to XX.
Remaining disagreements were resolved through discussion with the
faculty lead to produce the final consensus coding.”
