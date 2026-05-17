# LaTeX表格生成器设计文档

## 概述

为学术研究项目创建一个表格生成器，从Excel数据源生成4个LaTeX表格，用于分析AI心理健康研究论文的理论扎根和评估方法。

## 目录结构

```
table/
├── theory_eval_refined_coding_refined.xlsx  # 数据源（从项目根目录复制）
├── generate_tables.py                       # 主脚本
├── table1.tex                               # 统计表
├── table2.tex                               # 理论扎根分类表
├── table3.tex                               # 理论操作化评估分类表
└── table4.tex                               # 评估类型分析表
```

## 数据源

- **文件**: `theory_eval_refined_coding_refined.xlsx`
- **工作表**: `theory_eval_refined_coding`
- **论文数量**: 52篇
- **关键列**:
  - `Citation_Key`: 论文引用标识
  - `Theory_Grounding`: 理论扎根程度（Strong/Partial/Mentioned/None）
  - `Theory_Operationalized_In_Evaluation`: 理论操作化评估程度（Strong/Partial/Mentioned/None）
  - `Theory_Eval_Type`: 评估类型（分号分隔的多值）

## 表格设计

### Table 1: 统计表
**目的**: 统计每篇论文的"理论扎根"和"理论操作化评估"程度

**格式**:
```
| Category                    | Strong | Partial | Mentioned | None | Total |
|-----------------------------|--------|---------|-----------|------|-------|
| Theory Grounding            |   N    |    N    |     N     |  N   |   N   |
| Theory Operationalization   |   N    |    N    |     N     |  N   |   N   |
```

**内容**:
- 每个程度类别的论文数量
- 每个程度类别的百分比
- 总计

### Table 2: 理论扎根分类表
**目的**: 按理论扎根程度分类列出论文

**格式**:
```
| Category   | Papers (Citation Keys)                                    |
|------------|-------------------------------------------------------------|
| Strong     | Xiao2024HealMe, Gabriel2024Can, ...                       |
| Partial    | Haydarov2025Towards, ...                                  |
| Mentioned  | ...                                                       |
| None       | ...                                                       |
```

### Table 3: 理论操作化评估分类表
**目的**: 按理论操作化评估程度分类列出论文

**格式**:
```
| Category   | Papers (Citation Keys)                                    |
|------------|-------------------------------------------------------------|
| Strong     | Xiao2024HealMe, Gabriel2024Can, ...                       |
| Partial    | Haydarov2025Towards, ...                                  |
| Mentioned  | ...                                                       |
| None       | ...                                                       |
```

### Table 4: 评估类型分析表
**目的**: 分析每篇论文使用的评估方法类型

**格式**:
```
| Evaluation Type                | What It Evaluates           | Example Papers                |
|--------------------------------|-----------------------------|--------------------------------|
| Validated scale                | ...                         | Xiao2024HealMe, ...           |
| Established therapy/counseling | ...                         | ...                            |
| coding system                  |                             |                                |
| Theory-specific rubric         | ...                         | ...                            |
| Custom expert rating           | ...                         | ...                            |
| ...                            | ...                         | ...                            |
```

**评估类型分类**（从`Theory_Eval_Type`列解析）:
- Validated scale
- Established therapy/counseling coding system
- Theory-specific rubric
- Custom expert rating
- Affective/emotional dynamics metric
- Clinical diagnostic benchmark
- Theory-specific benchmark/task
- LLM-based evaluation
- Other

## 脚本功能

**generate_tables.py**:
1. 读取Excel文件
2. 解析数据，处理分号分隔的多值
3. 统计各程度类别的数量和百分比
4. 按程度分类整理论文列表
5. 归类评估类型，提取示例论文
6. 生成4个独立的LaTeX表格文件

## 技术要求

- Python 3.12+
- 依赖: pandas, openpyxl
- 使用uv管理依赖

## 使用方式

```bash
cd table
uv run generate_tables.py
```

生成的.tex文件可直接在LaTeX文档中使用：
```latex
\input{table/table1.tex}
```
