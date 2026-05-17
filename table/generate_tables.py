#!/usr/bin/env python3
"""
Generate LaTeX tables from Excel data.

Usage:
    cd table
    uv run python generate_tables.py

Output:
    table1.tex - Statistics of Theory Grounding and Theory Operationalization
    table2.tex - Papers Classified by Theory Grounding Level
    table3.tex - Papers Classified by Theory Operationalization in Evaluation
    table4.tex - Evaluation Types Used in Included Studies
"""

import pandas as pd
from pathlib import Path


def read_data(excel_path: str) -> pd.DataFrame:
    """Read Excel file and return DataFrame."""
    df = pd.read_excel(excel_path, sheet_name="theory_eval_refined_coding")
    return df


def generate_table1(df: pd.DataFrame) -> str:
    """Generate statistics table for Theory Grounding and Theory Operationalization."""
    # 统计Theory_Grounding
    grounding_counts = df["Theory_Grounding"].value_counts()
    grounding_total = len(df)

    # 统计Theory_Operationalized_In_Evaluation
    operational_counts = df["Theory_Operationalized_In_Evaluation"].value_counts()
    operational_total = len(df)

    # 定义程度类别
    categories = ["Strong", "Partial", "Mentioned", "None"]

    # 生成LaTeX表格
    latex = r"""\begin{table}[htbp]
\centering
\caption{Statistics of Theory Grounding and Theory Operationalization in Evaluation}
\label{tab:theory-stats}
\begin{tabular}{lcccccc}
\toprule
\textbf{Category} & \textbf{Strong} & \textbf{Partial} & \textbf{Mentioned} & \textbf{None} & \textbf{Total} \\
\midrule
"""

    # Theory Grounding行
    grounding_row = "Theory Grounding"
    for cat in categories:
        count = grounding_counts.get(cat, 0)
        pct = count / grounding_total * 100
        grounding_row += f" & {count} ({pct:.1f}\\%)"
    grounding_row += f" & {grounding_total} \\\\"
    latex += grounding_row + "\n"

    # Theory Operationalization行
    operational_row = "Theory Operationalization"
    for cat in categories:
        count = operational_counts.get(cat, 0)
        pct = count / operational_total * 100
        operational_row += f" & {count} ({pct:.1f}\\%)"
    operational_row += f" & {operational_total} \\\\"
    latex += operational_row + "\n"

    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""
    return latex


def generate_table2(df: pd.DataFrame) -> str:
    """Generate classification table for Theory Grounding."""
    categories = ["Strong", "Partial", "Mentioned", "None"]

    # 按Theory_Grounding分组
    grouped = df.groupby("Theory_Grounding")["Citation_Key"].apply(list)

    # 生成LaTeX表格 - 使用longtable支持跨页，p{}列自动换行
    latex = r"""\begin{longtable}{p{2.5cm}p{13cm}}
\caption{Papers Classified by Theory Grounding Level}
\label{tab:theory-grounding} \\
\toprule
\textbf{Category} & \textbf{Papers (Citation Keys)} \\
\midrule
\endfirsthead

\toprule
\textbf{Category} & \textbf{Papers (Citation Keys)} \\
\midrule
\endhead

\bottomrule
\endfoot
\hyphenpenalty=10000\exhyphenpenalty=10000\tolerance=10000\raggedright
"""

    for cat in categories:
        papers = grouped.get(cat, [])
        if papers:
            papers_str = ", ".join(papers)
        else:
            papers_str = "---"
        latex += f"{cat} & {papers_str} \\\\\n"

    latex += r"""\end{longtable}
"""
    return latex


def generate_table3(df: pd.DataFrame) -> str:
    """Generate classification table for Theory Operationalization in Evaluation."""
    categories = ["Strong", "Partial", "Mentioned", "None"]

    # 按Theory_Operationalized_In_Evaluation分组
    grouped = df.groupby("Theory_Operationalized_In_Evaluation")["Citation_Key"].apply(list)

    # 生成LaTeX表格 - 使用longtable支持跨页，p{}列自动换行
    latex = r"""\begin{longtable}{p{2.5cm}p{13cm}}
\caption{Papers Classified by Theory Operationalization in Evaluation}
\label{tab:theory-operationalization} \\
\toprule
\textbf{Category} & \textbf{Papers (Citation Keys)} \\
\midrule
\endfirsthead

\toprule
\textbf{Category} & \textbf{Papers (Citation Keys)} \\
\midrule
\endhead

\bottomrule
\endfoot
\hyphenpenalty=10000\exhyphenpenalty=10000\tolerance=10000\raggedright
"""

    for cat in categories:
        papers = grouped.get(cat, [])
        if papers:
            papers_str = ", ".join(papers)
        else:
            papers_str = "---"
        latex += f"{cat} & {papers_str} \\\\\n"

    latex += r"""\end{longtable}
"""
    return latex


def generate_table4(df: pd.DataFrame) -> str:
    """Generate evaluation type analysis table."""
    # 定义评估类型分类
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

    # 统计每种评估类型
    type_papers = {}
    for eval_type in eval_types:
        # 查找包含该评估类型的论文
        mask = df["Theory_Eval_Type"].str.contains(eval_type, na=False, case=False)
        papers = df.loc[mask, "Citation_Key"].tolist()
        if papers:
            type_papers[eval_type] = papers

    # 生成LaTeX表格 - 使用longtable支持跨页，p{}列自动换行
    latex = r"""\begin{longtable}{p{4cm}p{5cm}p{6cm}}
\caption{Evaluation Types Used in Included Studies}
\label{tab:eval-types} \\
\toprule
\textbf{Evaluation Type} & \textbf{What It Evaluates} & \textbf{Example Papers} \\
\midrule
\endfirsthead

\toprule
\textbf{Evaluation Type} & \textbf{What It Evaluates} & \textbf{Example Papers} \\
\midrule
\endhead

\bottomrule
\endfoot
\hyphenpenalty=10000\exhyphenpenalty=10000\tolerance=10000\raggedright
"""

    # 评估类型描述
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

    for eval_type, papers in type_papers.items():
        desc = descriptions.get(eval_type, "Other evaluation methods")
        papers_str = ", ".join(papers)
        latex += f"{eval_type} & {desc} & {papers_str} \\\\\n"

    latex += r"""\end{longtable}
"""
    return latex


def main():
    """Main entry point."""
    excel_path = Path(__file__).parent / "theory_eval_refined_coding_refined.xlsx"
    df = read_data(excel_path)

    # 生成Table 1
    table1 = generate_table1(df)
    output_path = Path(__file__).parent / "table1.tex"
    output_path.write_text(table1)
    print(f"Generated {output_path}")

    # 生成Table 2
    table2 = generate_table2(df)
    output_path = Path(__file__).parent / "table2.tex"
    output_path.write_text(table2)
    print(f"Generated {output_path}")

    # 生成Table 3
    table3 = generate_table3(df)
    output_path = Path(__file__).parent / "table3.tex"
    output_path.write_text(table3)
    print(f"Generated {output_path}")

    # 生成Table 4
    table4 = generate_table4(df)
    output_path = Path(__file__).parent / "table4.tex"
    output_path.write_text(table4)
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
