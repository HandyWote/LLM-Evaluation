# LaTeX表格生成器实施计划

> **致智能体工作者：** 必须使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 技能来逐任务实施此计划。步骤使用复选框（`- [ ]`）语法进行跟踪。

**目标：** 从Excel数据源生成4个LaTeX表格，分析AI心理健康研究论文的理论扎根和评估方法。

**架构：** 单一脚本读取Excel文件，解析数据，生成4个独立的.tex文件。使用pandas处理数据，字符串模板生成LaTeX代码。

**技术栈：** Python 3.12+, pandas, openpyxl, uv

---

## 文件结构

```
table/
├── theory_eval_refined_coding_refined.xlsx  # 数据源（已复制）
├── pyproject.toml                           # uv项目配置
├── generate_tables.py                       # 主脚本
├── table1.tex                               # 统计表（生成）
├── table2.tex                               # 理论扎根分类表（生成）
├── table3.tex                               # 理论操作化评估分类表（生成）
└── table4.tex                               # 评估类型分析表（生成）
```

---

## Task 1: 初始化uv项目

**文件：**
- 创建：`table/pyproject.toml`

- [ ] **Step 1: 创建pyproject.toml**

```toml
[project]
name = "latex-table-generator"
version = "0.1.0"
description = "Generate LaTeX tables from Excel data"
requires-python = ">=3.12"
dependencies = [
    "pandas>=2.0.0",
    "openpyxl>=3.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 2: 安装依赖**

```bash
cd table
uv sync
```

预期输出：依赖安装成功

- [ ] **Step 3: 提交**

```bash
git add table/pyproject.toml table/uv.lock
git commit -m "feat: initialize uv project for table generator"
```

---

## Task 2: 创建主脚本框架

**文件：**
- 创建：`table/generate_tables.py`

- [ ] **Step 1: 创建脚本框架**

```python
#!/usr/bin/env python3
"""Generate LaTeX tables from Excel data."""

import pandas as pd
from pathlib import Path


def read_data(excel_path: str) -> pd.DataFrame:
    """Read Excel file and return DataFrame."""
    df = pd.read_excel(excel_path, sheet_name="theory_eval_refined_coding")
    return df


def main():
    """Main entry point."""
    excel_path = Path(__file__).parent / "theory_eval_refined_coding_refined.xlsx"
    df = read_data(excel_path)
    print(f"Loaded {len(df)} papers")
    print(f"Columns: {list(df.columns)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 测试脚本运行**

```bash
cd table
uv run python generate_tables.py
```

预期输出：
```
Loaded 52 papers
Columns: ['Paper_ID', 'Citation_Key', 'Title', ...]
```

- [ ] **Step 3: 提交**

```bash
git add table/generate_tables.py
git commit -m "feat: create main script framework"
```

---

## Task 3: 实现Table 1统计表生成

**文件：**
- 修改：`table/generate_tables.py`
- 创建：`table/table1.tex`

- [ ] **Step 1: 添加统计函数**

在 `generate_tables.py` 中添加：

```python
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
```

- [ ] **Step 2: 更新main函数**

```python
def main():
    """Main entry point."""
    excel_path = Path(__file__).parent / "theory_eval_refined_coding_refined.xlsx"
    df = read_data(excel_path)

    # 生成Table 1
    table1 = generate_table1(df)
    output_path = Path(__file__).parent / "table1.tex"
    output_path.write_text(table1)
    print(f"Generated {output_path}")
```

- [ ] **Step 3: 测试生成**

```bash
cd table
uv run python generate_tables.py
cat table1.tex
```

预期输出：LaTeX表格代码，包含统计数据

- [ ] **Step 4: 提交**

```bash
git add table/generate_tables.py table/table1.tex
git commit -m "feat: implement Table 1 statistics generation"
```

---

## Task 4: 实现Table 2理论扎根分类表

**文件：**
- 修改：`table/generate_tables.py`
- 创建：`table/table2.tex`

- [ ] **Step 1: 添加分类函数**

在 `generate_tables.py` 中添加：

```python
def generate_table2(df: pd.DataFrame) -> str:
    """Generate classification table for Theory Grounding."""
    categories = ["Strong", "Partial", "Mentioned", "None"]

    # 按Theory_Grounding分组
    grouped = df.groupby("Theory_Grounding")["Citation_Key"].apply(list)

    # 生成LaTeX表格
    latex = r"""\begin{table}[htbp]
\centering
\caption{Papers Classified by Theory Grounding Level}
\label{tab:theory-grounding}
\begin{tabular}{lp{12cm}}
\toprule
\textbf{Category} & \textbf{Papers (Citation Keys)} \\
\midrule
"""

    for cat in categories:
        papers = grouped.get(cat, [])
        if papers:
            papers_str = ", ".join(papers)
        else:
            papers_str = "---"
        latex += f"{cat} & {papers_str} \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""
    return latex
```

- [ ] **Step 2: 更新main函数**

```python
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
```

- [ ] **Step 3: 测试生成**

```bash
cd table
uv run python generate_tables.py
cat table2.tex
```

预期输出：LaTeX表格代码，按程度分类列出论文

- [ ] **Step 4: 提交**

```bash
git add table/generate_tables.py table/table2.tex
git commit -m "feat: implement Table 2 theory grounding classification"
```

---

## Task 5: 实现Table 3理论操作化评估分类表

**文件：**
- 修改：`table/generate_tables.py`
- 创建：`table/table3.tex`

- [ ] **Step 1: 添加分类函数**

在 `generate_tables.py` 中添加：

```python
def generate_table3(df: pd.DataFrame) -> str:
    """Generate classification table for Theory Operationalization in Evaluation."""
    categories = ["Strong", "Partial", "Mentioned", "None"]

    # 按Theory_Operationalized_In_Evaluation分组
    grouped = df.groupby("Theory_Operationalized_In_Evaluation")["Citation_Key"].apply(list)

    # 生成LaTeX表格
    latex = r"""\begin{table}[htbp]
\centering
\caption{Papers Classified by Theory Operationalization in Evaluation}
\label{tab:theory-operationalization}
\begin{tabular}{lp{12cm}}
\toprule
\textbf{Category} & \textbf{Papers (Citation Keys)} \\
\midrule
"""

    for cat in categories:
        papers = grouped.get(cat, [])
        if papers:
            papers_str = ", ".join(papers)
        else:
            papers_str = "---"
        latex += f"{cat} & {papers_str} \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""
    return latex
```

- [ ] **Step 2: 更新main函数**

```python
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
```

- [ ] **Step 3: 测试生成**

```bash
cd table
uv run python generate_tables.py
cat table3.tex
```

预期输出：LaTeX表格代码，按程度分类列出论文

- [ ] **Step 4: 提交**

```bash
git add table/generate_tables.py table/table3.tex
git commit -m "feat: implement Table 3 theory operationalization classification"
```

---

## Task 6: 实现Table 4评估类型分析表

**文件：**
- 修改：`table/generate_tables.py`
- 创建：`table/table4.tex`

- [ ] **Step 1: 添加评估类型分析函数**

在 `generate_tables.py` 中添加：

```python
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

    # 生成LaTeX表格
    latex = r"""\begin{table}[htbp]
\centering
\caption{Evaluation Types Used in Included Studies}
\label{tab:eval-types}
\begin{tabular}{lp{8cm}p{4cm}}
\toprule
\textbf{Evaluation Type} & \textbf{What It Evaluates} & \textbf{Example Papers} \\
\midrule
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
        examples = ", ".join(papers[:3])  # 最多显示3个例子
        if len(papers) > 3:
            examples += f", ... ({len(papers)} total)"
        latex += f"{eval_type} & {desc} & {examples} \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""
    return latex
```

- [ ] **Step 2: 更新main函数**

```python
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
```

- [ ] **Step 3: 测试生成**

```bash
cd table
uv run python generate_tables.py
cat table4.tex
```

预期输出：LaTeX表格代码，包含评估类型分析

- [ ] **Step 4: 提交**

```bash
git add table/generate_tables.py table/table4.tex
git commit -m "feat: implement Table 4 evaluation type analysis"
```

---

## Task 7: 最终测试和文档

**文件：**
- 修改：`table/generate_tables.py`（添加使用说明注释）

- [ ] **Step 1: 添加脚本头部注释**

在 `generate_tables.py` 顶部添加：

```python
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
```

- [ ] **Step 2: 完整测试**

```bash
cd table
uv run python generate_tables.py
ls -la *.tex
```

预期输出：4个.tex文件生成成功

- [ ] **Step 3: 验证LaTeX语法**

```bash
cd table
for f in table*.tex; do echo "=== $f ==="; head -20 "$f"; done
```

预期输出：每个文件都以 `\begin{table}` 开头，格式正确

- [ ] **Step 4: 最终提交**

```bash
git add table/generate_tables.py
git commit -m "feat: complete LaTeX table generator with documentation"
```

---

## 自查清单

- [x] 所有表格都从Excel数据源读取
- [x] 4个表格独立生成，格式正确
- [x] 使用uv管理依赖
- [x] 脚本可直接运行
- [x] 代码简洁，无过度设计
