# IRR Data Notes

## Label Cleaning

1. **Case normalization**: All labels were uppercased and whitespace-stripped.
   cxt used mixed case (Yes/No), hyh used uppercase (YES/NO).
2. **Column name typo**: cxt's `Interention_Sensitivity` (missing 'v') was
   renamed to `Intervention_Sensitivity` to match hyh's column.
3. **Prompt_Disclosure normalization**: cxt's `FULL DISCLOSURE`/`PARTIAL DISCLOSURE`
   /`NO DISCLOSURE` were normalized to `FULL`/`PARTIAL`/`NO`.

## Ordinal Variables (Weighted Kappa)

- **Persona_Model_Depth**: categories = Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles
  Kappa = 0.564, Agreement = 63.5%
- **Theory_Operationalized**: categories = Strong / Partial / Mentioned / None
  Kappa = 0.421, Agreement = 75.0%
- **Behavior_Eval_Depth**: categories = Dynamic / Pattern-level / Static / None
  Kappa = 0.178, Agreement = 50.0%
- **Interaction_Level**: categories = Single-turn / Short Multi-turn / Extended Dialogue / Longitudinal
  Kappa = 0.696, Agreement = 74.0%
- **Prompt_Disclosure**: categories = Full / Partial / No
  Kappa = 0.427, Agreement = 76.9%
- **Theory_Grounding**: categories = Strong / Weak / None
  Kappa = 0.526, Agreement = 81.2%

## Data Quality Issues in cxt CSV

The cxt CSV file contained corrupted rows beyond the 52 valid papers.
Rows with non-numeric Paper_ID were filtered out during loading.

## Missing Data Summary

Missing values are treated as NA and excluded pairwise from kappa computation.
No imputation was performed.

| Variable | Total | Valid | Missing cxt | Missing hyh | Missing both |
|----------|-------|-------|-------------|-------------|--------------|
| Eval_Human_Experts | 52 | 52 | 0 | 0 | 0 |
| Eval_Lay_Users | 52 | 52 | 0 | 0 | 0 |
| Eval_User_Study | 52 | 52 | 0 | 0 | 0 |
| Eval_LLM_Judge | 52 | 52 | 0 | 0 | 0 |
| Eval_Automatic | 52 | 52 | 0 | 0 | 0 |
| Realism | 52 | 52 | 0 | 0 | 0 |
| Consistency | 52 | 52 | 0 | 0 | 0 |
| Fidelity | 52 | 52 | 0 | 0 | 0 |
| Utility | 52 | 52 | 0 | 0 | 0 |
| Human Learning / Outcomes | 52 | 52 | 0 | 0 | 0 |
| Emotional Plausibility | 52 | 52 | 0 | 0 | 0 |
| Safety | 52 | 52 | 0 | 0 | 0 |
| Uses_Dynamic_State | 52 | 52 | 0 | 0 | 0 |
| Intervention_Sensitivity | 52 | 52 | 0 | 0 | 0 |
| Has_Rubric | 52 | 52 | 0 | 0 | 0 |
| LLM_Judge_Validated | 52 | 52 | 0 | 0 | 0 |
| Uses_Standard_Metrics | 52 | 52 | 0 | 0 | 0 |
| Metric_Interpretable | 52 | 52 | 0 | 0 | 0 |
| Comparable_To_Prior_Work | 52 | 52 | 0 | 0 | 0 |
| Has_Longitudinal_Eval | 52 | 52 | 0 | 0 | 0 |
| Has_Robustness_Testing | 52 | 52 | 0 | 0 | 0 |
| Has_Failure_Analysis | 52 | 52 | 0 | 0 | 0 |
| Sim_Behavior_Realistic | 52 | 52 | 0 | 0 | 0 |
| Dataset_Available | 52 | 52 | 0 | 0 | 0 |
| Simulation_Target | 52 | 52 | 0 | 0 | 0 |
| Persona_Model_Depth | 52 | 52 | 0 | 0 | 0 |
| Theory_Operationalized | 52 | 48 | 2 | 3 | 1 |
| Behavior_Eval_Depth | 52 | 36 | 10 | 12 | 6 |
| Interaction_Level | 52 | 50 | 2 | 0 | 0 |
| Prompt_Disclosure | 52 | 52 | 0 | 0 | 0 |
| Theory_Grounding | 52 | 48 | 1 | 4 | 1 |
| Reliability_Reported | 52 | 43 | 3 | 8 | 2 |
| Coding Options | 52 | 44 | 2 | 8 | 2 |