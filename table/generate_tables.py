#!/usr/bin/env python3
"""
Generate LaTeX tables from CSV data.

Usage:
    cd table
    uv run python generate_tables.py

Output:
    table/acl_latex_for_overleaf.tex  - Theory tables (1-4)
    table/eval_tables.tex             - Eval methodology tables (5-9)
"""

import pandas as pd
from pathlib import Path


def read_data(csv_path: str) -> pd.DataFrame:
    """Read CSV file and return DataFrame, preserving 'N/A' strings."""
    df = pd.read_csv(csv_path, keep_default_na=False)
    return df


# ─── Theory Tables (1-4) ─────────────────────────────────────────


def generate_table1(df: pd.DataFrame) -> str:
    """Generate statistics table for Theory Grounding and Theory Operationalization."""
    df_clean = df.copy()
    df_clean['Theory_Grounding'] = df_clean['Theory_Grounding'].replace('', 'Not Specified')
    df_clean['Theory_Operationalized_In_Evaluation'] = df_clean['Theory_Operationalized_In_Evaluation'].replace('', 'Not Specified')

    grounding_counts = df_clean["Theory_Grounding"].value_counts()
    grounding_total = len(df_clean)
    operational_counts = df_clean["Theory_Operationalized_In_Evaluation"].value_counts()
    operational_total = len(df_clean)

    all_categories = ["Strong", "Partial", "Mentioned", "Not Specified"]
    active_categories = [cat for cat in all_categories
                        if grounding_counts.get(cat, 0) > 0 or operational_counts.get(cat, 0) > 0]

    latex = r"""\begin{table*}[tbp]
\centering
\begin{tabular}{l""" + "c" * (len(active_categories) + 1) + r"""}
\toprule
\textbf{Category}"""
    for cat in active_categories:
        latex += f" & \\textbf{{{cat}}}"
    latex += " & \\textbf{Total} \\\\\n\\midrule\n"

    grounding_row = "Theory Grounding"
    for cat in active_categories:
        count = grounding_counts.get(cat, 0)
        if count > 0:
            pct = count / grounding_total * 100
            grounding_row += f" & {count} ({pct:.1f}\\%)"
        else:
            grounding_row += " & ---"
    grounding_row += f" & {grounding_total} \\\\\n"
    latex += grounding_row + "\\midrule\n"

    operational_row = "Theory Operationalization"
    for cat in active_categories:
        count = operational_counts.get(cat, 0)
        if count > 0:
            pct = count / operational_total * 100
            operational_row += f" & {count} ({pct:.1f}\\%)"
        else:
            operational_row += " & ---"
    operational_row += f" & {operational_total} \\\\\n"
    latex += operational_row

    latex += r"""
\bottomrule
\end{tabular}
\caption{Statistics of Theory Grounding and Theory Operationalization in Evaluation}
\label{tab:theory-stats}
\end{table*}
"""
    return latex


def _generate_classification_table(df: pd.DataFrame, col: str, caption: str, label: str) -> str:
    """Generate a classification table for a given column."""
    categories = ["Strong", "Partial", "Mentioned", "None", "Not Specified"]
    grouped = df.groupby(col)["Citation_Key"].apply(list)

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{2.5cm}p{12.4cm}}
\toprule
\textbf{Category} & \textbf{Papers} \\
\midrule
"""
    first = True
    for cat in categories:
        papers = grouped.get(cat, [])
        if papers:
            if not first:
                latex += "\\midrule\n"
            papers_str = ", ".join([f"\\cite{{{p}}}" for p in papers])
            latex += f"{cat} & {papers_str} \\\\\n"
            first = False

    latex += r"""\bottomrule
\end{tabular}
\caption{""" + caption + r"""}
\label{""" + label + r"""}
\end{table*}
"""
    return latex


def generate_table2(df: pd.DataFrame) -> str:
    return _generate_classification_table(df, "Theory_Grounding",
        "Papers Classified by Theory Grounding Level", "tab:theory-grounding")


def generate_table3(df: pd.DataFrame) -> str:
    return _generate_classification_table(df, "Theory_Operationalized_In_Evaluation",
        "Papers Classified by Theory Operationalization in Evaluation", "tab:theory-operationalization")


def generate_table4(df: pd.DataFrame) -> str:
    """Generate evaluation type analysis table."""
    eval_types = [
        "Validated scale",
        "Established therapy/counseling coding system",
        "Theory-specific rubric",
        "Custom expert rating",
        "Affective/emotional dynamics metric",
        "Clinical diagnostic benchmark",
        "Theory-specific benchmark/task",
        "LLM-based evaluation",
    ]

    type_papers = {}
    for eval_type in eval_types:
        mask = df["Theory_Eval_Type"].str.contains(eval_type, na=False, case=False)
        papers = df.loc[mask, "Citation_Key"].tolist()
        if papers:
            type_papers[eval_type] = papers

    descriptions = {
        "Validated scale": "Standardized psychological or clinical scales",
        "Established therapy/counseling coding system": "Therapy process or outcome coding",
        "Theory-specific rubric": "Custom rubrics based on theoretical constructs",
        "Custom expert rating": "Expert judgments on custom dimensions",
        "Affective/emotional dynamics metric": "Emotion recognition or affective computing metrics",
        "Clinical diagnostic benchmark": "Clinical diagnosis or screening benchmarks",
        "Theory-specific benchmark/task": "Task-specific performance benchmarks",
        "LLM-based evaluation": "LLM-generated ratings or judgments",
    }

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{6cm}p{8cm}}
\toprule
\textbf{Evaluation Type} & \textbf{Example Papers} \\
\midrule
"""
    items = list(type_papers.items())
    for i, (eval_type, papers) in enumerate(items):
        desc = descriptions.get(eval_type, "Other evaluation methods")
        papers_str = ", ".join([f"\\cite{{{p}}}" for p in papers])
        latex += f"{eval_type}\\newline\\textcolor{{gray}}{{\\footnotesize{{\\textit{{{desc}}}}}}} & {papers_str} \\\\\n"
        if i < len(items) - 1:
            latex += "\\midrule\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Evaluation Types Used in Included Studies}
\label{tab:eval-types}
\end{table*}
"""
    return latex


# ─── Eval Tables (5-9) ───────────────────────────────────────────


def _cite_list(papers: list[str]) -> str:
    return ", ".join([f"\\cite{{{p}}}" for p in sorted(papers)])


def generate_evaluator_summary(df: pd.DataFrame) -> str:
    """Table 5: Distribution of Evaluator Types."""
    rows = [
        ("Human Experts", "Eval_Human_Experts"),
        ("LLM Judges", "Eval_LLM_Judge"),
        ("Automatic Metrics", "Eval_Automatic"),
    ]
    total = len(df)
    all3_mask = (df["Eval_Human_Experts"]=="Yes") & (df["Eval_LLM_Judge"]=="Yes") & (df["Eval_Automatic"]=="Yes")
    all3_count = all3_mask.sum()

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{lc}
\toprule
\textbf{Evaluator Type} & \textbf{Count (\%)} \\
\midrule
"""
    for label, col in rows:
        count = (df[col] == "Yes").sum()
        pct = count / total * 100
        latex += f"{label} & {count} ({pct:.1f}\\%) \\\\\n"
    latex += f"All Three (Expert + LLM + Auto) & {all3_count} ({all3_count/total*100:.1f}\\%) \\\\\n"
    latex += r"""\bottomrule
\end{tabular}
\caption{Distribution of Evaluator Types Across Studies ($N=52$)}
\label{tab:evaluator-types}
\end{table*}
"""
    return latex


def generate_evaluator_papers(df: pd.DataFrame) -> str:
    """Table 5 cite: Papers by Evaluator Type."""
    rows = [
        ("Human Experts", "Eval_Human_Experts"),
        ("LLM Judges", "Eval_LLM_Judge"),
        ("Automatic Metrics", "Eval_Automatic"),
    ]
    all3_mask = (df["Eval_Human_Experts"]=="Yes") & (df["Eval_LLM_Judge"]=="Yes") & (df["Eval_Automatic"]=="Yes")

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{5cm}p{10cm}}
\toprule
\textbf{Evaluator Type} & \textbf{Papers} \\
\midrule
"""
    for i, (label, col) in enumerate(rows):
        papers = df.loc[df[col]=="Yes", "Citation_Key"].tolist()
        latex += f"{label} & {_cite_list(papers)} \\\\\n"
        latex += "\\midrule\n"

    papers = df.loc[all3_mask, "Citation_Key"].tolist()
    latex += f"All Three (Expert + LLM + Auto) & {_cite_list(papers)} \\\\\n"
    latex += r"""\bottomrule
\end{tabular}
\caption{Papers by Evaluator Type}
\label{tab:evaluator-types-cite}
\end{table*}
"""
    return latex


def generate_rubric_summary(df: pd.DataFrame) -> str:
    """Table 6: Scoring Rubric and Inter-Rater Reliability."""
    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{llc}
\toprule
\textbf{Has Rubric} & \textbf{Reliability Reported} & \textbf{Count} \\
\midrule
"""
    rubric_vals = ["Yes", "No"]
    rel_vals = ["Yes", "No", "N/A"]
    for r in rubric_vals:
        for rel in rel_vals:
            n = ((df["Has_Rubric"]==r) & (df["Reliability_Reported"]==rel)).sum()
            if n > 0:
                display_rel = rel if rel != "N/A" else "N/A"
                latex += f"{r} & {display_rel} & {n} \\\\\n"
    latex += r"""\bottomrule
\end{tabular}
\caption{Scoring Rubric and Inter-Rater Reliability Reporting}
\label{tab:rubric-reliability}
\end{table*}
"""
    return latex


def generate_rubric_papers(df: pd.DataFrame) -> str:
    """Table 6 cite: Papers by Rubric and Reliability."""
    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{5cm}p{10cm}}
\toprule
\textbf{Category} & \textbf{Papers} \\
\midrule
"""
    categories = [
        ("Rubric=Yes, Reliability=Yes", ("Yes", "Yes")),
        ("Rubric=Yes, Reliability=No", ("Yes", "No")),
        ("Rubric=Yes, Reliability=N/A", ("Yes", "N/A")),
        ("Rubric=No, Reliability=Yes", ("No", "Yes")),
        ("Rubric=No, Reliability=No", ("No", "No")),
        ("Rubric=No, Reliability=N/A", ("No", "N/A")),
    ]
    first = True
    for label, (r, rel) in categories:
        mask = (df["Has_Rubric"]==r) & (df["Reliability_Reported"]==rel)
        papers = df.loc[mask, "Citation_Key"].tolist()
        if papers:
            if not first:
                latex += "\\midrule\n"
            latex += f"{label} & {_cite_list(papers)} \\\\\n"
            first = False

    latex += r"""\bottomrule
\end{tabular}
\caption{Papers by Rubric Use and Reliability Reporting}
\label{tab:rubric-reliability-cite}
\end{table*}
"""
    return latex


def generate_dimensions_summary(df: pd.DataFrame) -> str:
    """Table 7: Evaluation Dimension Coverage."""
    dims = [
        ("Utility", "Utility"),
        ("Fidelity", "Fidelity"),
        ("Realism", "Realism"),
        ("Emotional Plausibility", "Emotional Plausibility"),
        ("Consistency", "Consistency"),
        ("Safety", "Safety"),
        ("Human Learning / Outcomes", "Human Learning / Outcomes"),
    ]
    total = len(df)

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{lc}
\toprule
\textbf{Evaluation Dimension} & \textbf{Count (\%)} \\
\midrule
"""
    for label, col in dims:
        count = (df[col] == "Yes").sum()
        pct = count / total * 100
        latex += f"{label} & {count} ({pct:.1f}\\%) \\\\\n"
    latex += r"""\bottomrule
\end{tabular}
\caption{Evaluation Dimension Coverage Across Studies ($N=52$)}
\label{tab:eval-dimensions}
\end{table*}
"""
    return latex


def generate_dimensions_papers(df: pd.DataFrame) -> str:
    """Table 7 cite: Papers by Evaluation Dimension."""
    dims = [
        ("Utility", "Utility"),
        ("Fidelity", "Fidelity"),
        ("Realism", "Realism"),
        ("Emotional Plausibility", "Emotional Plausibility"),
        ("Consistency", "Consistency"),
        ("Safety", "Safety"),
        ("Human Learning / Outcomes", "Human Learning / Outcomes"),
    ]

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{4cm}p{10.5cm}}
\toprule
\textbf{Category} & \textbf{Papers} \\
\midrule
"""
    for i, (label, col) in enumerate(dims):
        papers = df.loc[df[col]=="Yes", "Citation_Key"].tolist()
        latex += f"{label} & {_cite_list(papers)} \\\\\n"
        if i < len(dims) - 1:
            latex += "\\midrule\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Papers by Evaluation Dimension}
\label{tab:eval-dimensions-cite}
\end{table*}
"""
    return latex


def generate_interaction_summary(df: pd.DataFrame) -> str:
    """Table 8: Interaction Level by Behavioral Evaluation Depth."""
    df = df.copy()
    df["BED_display"] = df["Behavior_Eval_Depth"].replace("None", "(unspecified)")

    il_order = ["Single-turn", "Short Multi-turn", "Extended Dialogue", "Longitudinal"]
    bed_order = ["Static", "Pattern-level", "Dynamic", "(unspecified)"]

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{l""" + "c" * len(bed_order) + r"""}
\toprule
\textbf{Interaction Level}"""
    for bed in bed_order:
        latex += f" & \\textbf{{{bed}}}"
    latex += r""" \\
\midrule
"""
    for il in il_order:
        latex += f"{il}"
        for bed in bed_order:
            n = ((df["Interaction_Level"]==il) & (df["BED_display"]==bed)).sum()
            latex += f" & {n}"
        latex += " \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Interaction Level by Behavioral Evaluation Depth ($N=52$)}
\label{tab:interaction-behavior}
\end{table*}
"""
    return latex


def generate_interaction_papers(df: pd.DataFrame) -> str:
    """Table 8 cite: Papers by Interaction and Behavior."""
    df = df.copy()
    df["BED_display"] = df["Behavior_Eval_Depth"].replace("None", "(unspecified)")

    il_order = ["Single-turn", "Short Multi-turn", "Extended Dialogue", "Longitudinal"]
    bed_order = ["Static", "Pattern-level", "Dynamic", "(unspecified)"]

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{5.5cm}p{9.5cm}}
\toprule
\textbf{Category} & \textbf{Papers} \\
\midrule
"""
    first = True
    for il in il_order:
        for bed in bed_order:
            mask = (df["Interaction_Level"]==il) & (df["BED_display"]==bed)
            papers = df.loc[mask, "Citation_Key"].tolist()
            if papers:
                if not first:
                    latex += "\\midrule\n"
                latex += f"{il} / {bed} & {_cite_list(papers)} \\\\\n"
                first = False

    latex += r"""\bottomrule
\end{tabular}
\caption{Papers by Interaction Level and Behavioral Evaluation Depth}
\label{tab:interaction-behavior-cite}
\end{table*}
"""
    return latex


def generate_human_learning_summary(df: pd.DataFrame) -> str:
    """Table 9: Human Learning by Lay Users and User Study."""
    df = df.copy()
    df["HL"] = (df["Human Learning / Outcomes"]=="Yes").map({True:"Yes", False:"No"})
    df["LU"] = (df["Eval_Lay_Users"]=="Yes").map({True:"Yes", False:"No"})
    df["US"] = (df["Eval_User_Study"]=="Yes").map({True:"Yes", False:"No"})

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{lllc}
\toprule
\textbf{Human Learning} & \textbf{Lay Users} & \textbf{User Study} & \textbf{Count} \\
\midrule
"""
    for hl in ["Yes", "No"]:
        for lu in ["Yes", "No"]:
            for us in ["Yes", "No"]:
                n = ((df["HL"]==hl) & (df["LU"]==lu) & (df["US"]==us)).sum()
                latex += f"{hl} & {lu} & {us} & {n} \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\caption{Human Learning Outcomes by Lay User Involvement and User Study Design ($N=52$)}
\label{tab:human-learning}
\end{table*}
"""
    return latex


def generate_human_learning_papers(df: pd.DataFrame) -> str:
    """Table 9 cite: Papers by Human Learning, Lay Users, User Study."""
    df = df.copy()
    df["HL"] = (df["Human Learning / Outcomes"]=="Yes").map({True:"Yes", False:"No"})
    df["LU"] = (df["Eval_Lay_Users"]=="Yes").map({True:"Yes", False:"No"})
    df["US"] = (df["Eval_User_Study"]=="Yes").map({True:"Yes", False:"No"})

    latex = r"""\begin{table*}[tbp]
\centering
\small
\begin{tabular}{p{5cm}p{10cm}}
\toprule
\textbf{Category} & \textbf{Papers} \\
\midrule
"""
    first = True
    for hl in ["Yes", "No"]:
        for lu in ["Yes", "No"]:
            for us in ["Yes", "No"]:
                mask = (df["HL"]==hl) & (df["LU"]==lu) & (df["US"]==us)
                papers = df.loc[mask, "Citation_Key"].tolist()
                if papers:
                    if not first:
                        latex += "\\midrule\n"
                    label = f"HL={hl}, LU={lu}, US={us}"
                    latex += f"{label} & {_cite_list(papers)} \\\\\n"
                    first = False

    latex += r"""\bottomrule
\end{tabular}
\caption{Papers by Human Learning, Lay Users, and User Study}
\label{tab:human-learning-cite}
\end{table*}
"""
    return latex


# ─── Main ─────────────────────────────────────────────────────────


def generate_theory_tables() -> str:
    """Generate Theory tables (1-4) from theory_eval CSV."""
    csv_path = Path(__file__).parent / "theory_eval_refined_coding_refined.csv"
    df = read_data(csv_path)

    content = "% === Theory Grounding & Operationalization Tables ===\n\n"
    content += generate_table1(df)
    content += "\n"
    content += generate_table2(df)
    content += "\n"
    content += generate_table3(df)
    content += "\n"
    content += generate_table4(df)
    return content


def generate_eval_tables() -> str:
    """Generate Eval tables (5-9) from final-table CSV."""
    csv_path = Path(__file__).parent.parent / "compare" / "final-table.csv"
    df = read_data(csv_path)

    content = "% === Evaluation Methodology Tables ===\n\n"
    content += generate_evaluator_summary(df)
    content += "\n"
    content += generate_evaluator_papers(df)
    content += "\n"
    content += generate_rubric_summary(df)
    content += "\n"
    content += generate_rubric_papers(df)
    content += "\n"
    content += generate_dimensions_summary(df)
    content += "\n"
    content += generate_dimensions_papers(df)
    content += "\n"
    content += generate_interaction_summary(df)
    content += "\n"
    content += generate_interaction_papers(df)
    content += "\n"
    content += generate_human_learning_summary(df)
    content += "\n"
    content += generate_human_learning_papers(df)
    return content


def main():
    """Main entry point."""
    # Theory tables
    theory_content = generate_theory_tables()
    theory_path = Path(__file__).parent / "acl_latex_for_overleaf.tex"
    theory_path.write_text(theory_content)
    print(f"Generated {theory_path}")

    # Eval tables
    eval_content = generate_eval_tables()
    eval_path = Path(__file__).parent / "eval_tables.tex"
    eval_path.write_text(eval_content)
    print(f"Generated {eval_path}")

    # Quick validation
    df = read_data(Path(__file__).parent.parent / "compare" / "final-table.csv")
    print(f"\nValidation (N={len(df)}):")
    print(f"  Human Experts: {(df['Eval_Human_Experts']=='Yes').sum()}")
    print(f"  LLM Judges: {(df['Eval_LLM_Judge']=='Yes').sum()}")
    print(f"  Automatic Metrics: {(df['Eval_Automatic']=='Yes').sum()}")
    print(f"  Has Rubric: {(df['Has_Rubric']=='Yes').sum()}")
    print(f"  Reliability Reported: {(df['Reliability_Reported']=='Yes').sum()}")
    print(f"  Utility: {(df['Utility']=='Yes').sum()}")
    print(f"  Safety: {(df['Safety']=='Yes').sum()}")
    print(f"  Human Learning: {(df['Human Learning / Outcomes']=='Yes').sum()}")


if __name__ == "__main__":
    main()
