# DATA SOURCES — 哪个文件是哪个数据的真源（权威留档）

> **本文档是一份"留档"**：用来回答"论文里某个数字到底来自哪个文件"。
> 规则很简单：**下表中列出的源文件都是归档记录，禁止修改**；网页/表格里需要做的任何转换（拼写修正、字段覆盖、丢弃多余列）都在**构建脚本内**完成，不改源文件。
> 最后更新：2026-10（网站 `web/` 建立时）。

---

## 0. 一句话

**没有任何单一文件能独立复现论文的全部数字；三个文件按分组各管一块，合起来 100% 复现最终版论文（ARR Oct 2026）。**

---

## 1. 分组的真源（写代码、做网页时照这张表取数）

| 分组 | 字段 | **真源文件** |
|---|---|---|
| **G1** System & Simulation | Focus_Type, Simulation_Target, Persona_Model_Depth, Uses_Dynamic_State, Temporal_Modeling_Details | `compare/final-table.csv` |
| **G2** Evaluation Methods | Eval_Human_Experts, Eval_Lay_Users, Eval_User_Study, Eval_LLM_Judge, Eval_Automatic | `compare/final-table.csv` |
| **G3** Evaluation Dimensions | Safety, Realism, Consistency, Fidelity, Human Learning / Outcomes, Utility, Emotional Plausibility, Raw Eval Metrics | `compare/final-table.csv` |
| **G4** Interaction & Behavior | Interaction_Level, Behavior_Eval_Depth, Intervention_Sensitivity | `compare/final-table.csv`（列名拼写 `Interention_Sensitivity`，缺 v） |
| **G5** Theory & Reliability | **Theory_Grounding, Theory_Operationalized, Theory_Eval_Type** | **`table/theory_eval_refined_coding_refined.csv`** |
| | Prompt_Disclosure, Clinical_Theory, Reliability_Reported, Agreement Method | `compare/final-table.csv` |
| **G6** Additional Characteristics | Has_Rubric, LLM_Judge_Validated, Uses_Standard_Metrics, Metric_Interpretable, Comparable_To_Prior_Work, Has_Longitudinal_Eval, Has_Robustness_Testing, Has_Failure_Analysis, Sim_Behavior_Realistic, Dataset_Available | `compare/final-table.csv` |
| **G7** Claim–Evidence Alignment | Claim (C1/C2), Claim_Evidence_Alignment | `compare/claim_level_FINAL_analysis_ready.csv` |
| 字段定义（名称/取值/判断规则） | 全部 40 字段 | `docs/09_appendices.tex` 的 `\section{Coding Scheme}` |
| 最终版论文（裁判） | 所有报告数字 | `docs/Rethiniking_Evaluation___ARR_October_2026.pdf` |

> 注：`compare/final-table.csv` 里**也有** `Theory_Grounding` / `Theory_Operationalized` 两列，但那是**旧值**（Grounding 36/Weak 15、Op 35/10/5），与论文不符——**这两列作废，一律以 `table/theory_eval_refined_coding_refined.csv` 为准**。

---

## 2. 三个源文件分别是什么（来历）

| 文件 | 粒度 | 是什么 | 与论文的关系 |
|---|---|---|---|
| `compare/final-table.csv` | 论文级 52×46 | 人类**双人**编码（cxt + hyh）**逐格裁决**后的最终编码表；骨架取自 cxt 的表，220 处分歧逐格裁定（163→hyh、55→cxt）。元数据/自由文本列是 cxt 单人。 | G1–G6（除理论 3 字段）与论文一致 |
| `table/theory_eval_refined_coding_refined.csv` | 论文级 52 | 理论字段的**AI 辅助 PDF 复核**版（含 Theory_Eval_Type） | 论文 Table 18 的理论值（40/10/2、30/16/6）来自这里 |
| `compare/claim_level_FINAL_analysis_ready.csv` | claim 级 72 | 论文主张与支撑证据的配对 + 对齐裁决（C1 52 / C2 20） | 论文 §4.3 与附录 Table 13 来自这里 |

> 关于 `final-table.csv` 的 git 史：它的前身是 `extract/eval_results.csv`（**自始至终理论列都是旧值**，从未与论文理论表一致过）。论文理论表用的是 `theory_eval_refined_coding_refined.csv`（2026-05-20 加入后未再改）。两条编码线并行，谁也没并到谁。

---

## 3. 数字复现对照（论文 ← 文件）

| 论文中的数字 | 论文值 | 来自 |
|---|---|---|
| 评估者 Human/LLM/Auto/三者 | 34 / 30 / 35 / 15 | `final-table.csv` |
| 维度 Utility/Fidelity/Realism/Emo/Cons/Safety | 44/33/29/28/20/14 | `final-table.csv` |
| ≥1 / ≥3 维度（6 维口径） | 50 / 40 | `final-table.csv` |
| 长对话 / 动态状态 / 纵向 | 31 / 13 / 3 | `final-table.csv` |
| 长对话内行为深度 Static/Pattern/Dynamic | 16 / 7 / 7 | `final-table.csv` |
| LLM judge 验证（∩ 用 LLM judge） | 23 | `final-table.csv`（交集） |
| 用 rubric / 其中报信度 | 45 / 13 | `final-table.csv`（交集） |
| **理论 Grounding** | **40 / 10 / 2** | **`theory_eval_refined_coding_refined.csv`** |
| **理论 Operationalization** | **30 / 16 / 6** | **`theory_eval_refined_coding_refined.csv`** |
| 理论评估类型 scale/编码系统/rubric/benchmark | 9 / 7 / 35 / 26 | `theory_eval_refined_coding_refined.csv`（Theory_Eval_Type） |
| Claim–Evidence C1（n=52） | 41 / 7 / 4 | `claim_level_FINAL_analysis_ready.csv` |
| Claim–Evidence C2（n=20） | 12 / 8 / 0 | `claim_level_FINAL_analysis_ready.csv` |
| 编码信度 平均 raw / Cohen κ | 82.5% / 0.61 | 论文 §Coding Reliability |

---

## 4. 数据管线

```
compare/final-table.csv ─────────────────┐
table/theory_eval_refined_coding_refined.csv ─┼─► web/build/build_data.py ─► web/data/{papers,claims,codebook,stats}.json + data.js
compare/claim_level_FINAL_analysis_ready.csv ─┤        （只读源文件；不修改任何 CSV/tex）
docs/09_appendices.tex ───────────────────┘
```

- 网页所有数字**由脚本从源文件重算**，不手工写入 HTML。
- 重新生成：`python3 web/build/build_data.py`（见 `web/README.md`）。
- 部署：`.github/workflows/pages.yml`（push main 时 CI 里跑上面命令，再把 `web/` 发布到 GitHub Pages）。

---

## 5. 已知坑（构建时必须处理）

| 坑 | 处理 |
|---|---|
| `final-table.csv` 理论 2 列为旧值 | 构建时用 `theory_eval_refined_coding_refined.csv` **覆盖**（不改源文件） |
| `final-table.csv` 列名 `Interention_Sensitivity`（缺 v） | 映射为 codebook 的 `Intervention_Sensitivity` |
| `final-table.csv` 有重复列 `Coding Options`（≈ Reliability_Reported）与空列 `Unnamed: 45` | 丢弃 |
| G7 的 `Claim_Section`/`Evidence_Section` 命名不统一（如 `Abstract`、`7 Conclusion`、`VI Deployment`） | 展示前归一化 |
| `eval_reports/` 有 6 篇不在 52 篇语料内 | 做证据 join 时按 `Citation_Key` 过滤 |

---

## 6. 归档：原先散落在仓库根目录的文件去哪儿了

这些文件原来在仓库根目录，2026-10 网站建设时归位（**内容字节未变，仅移动**）：

| 原路径（根目录） | 现路径 |
|---|---|
| `09_appendices.tex` | `docs/09_appendices.tex` |
| `claim_level_FINAL_analysis_ready.csv` | `compare/claim_level_FINAL_analysis_ready.csv` |
| `Rethiniking_Evaluation___ARR_October_2026.pdf` | `docs/Rethiniking_Evaluation___ARR_October_2026.pdf` |
| `site_draft.html` | `docs/drafts/site_draft.html`（早期可视化草稿，仅留档） |

> 更早的论文版本 `docs/Rethiniking_Evaluation.pdf` 一并保留在 `docs/`。

---

## 7. 相关文档

- 网页需求与数据裁定：`docs/2026-10-08-codebook-webpage-requirements.md`
- 正文数字 vs CSV 的勘误：`docs/pdf_body_vs_csv.md`、`docs/pdf_table_discrepancies.md`
- 编码者间信度方法：`docs/Inter-rater_reliability_instructions_updated.md`、`compare/irr_method_summary.md`
- 字段定义草稿：`docs/codebook.csv`、`docs/评估维度表.md`
