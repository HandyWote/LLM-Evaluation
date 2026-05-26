# PDF 正文与附表数据不一致对照表

> 论文：*From Surface Realism to Behavioral Validity: Rethinking Evaluation for Repurposed Interactive LLM Systems*
> 检查日期：2026-05-26
> 检查范围：PDF §4.1–§4.5 正文叙述 vs Table 5–9 附表数据 vs LaTeX `eval_tables.tex`

---

## 总览

| # | 所在位置 | 正文数据 | 附表数据 | 差值 |
|---|---|---|---|---|
| 1 | §4.1 p.4 | Auto Metrics = 40 | Table 5: 35 | +5 |
| 2 | §4.1 p.4 | Human Experts = 39 | Table 5: 34 | +5 |
| 3 | §4.1 p.4 | All Three = 21 | LaTeX: 15 | +6 |
| 4 | §4.1 p.4 | Reliability reported = 23 | Table 6: 15 | +8 |
| 5 | §4.2 p.5 | Utility = 46 | Table 7: 44 | +2 |
| 6 | §4.2 p.5 | Fidelity = 35 | Table 7: 33 | +2 |
| 7 | §4.2 p.5 | Realism = 30 | Table 7: 29 | +1 |
| 8 | §4.2 p.5 | Emotional Plausibility = 30 | Table 7: 28 | +2 |
| 9 | §4.2 p.5 | Consistency = 22 | Table 7: 20 | +2 |
| 10 | §4.2 p.5 | Safety = 22 | Table 7: 14 | +8 |
| 11 | §4.4 p.5 | Extended Dialogue = 27 | Table 8: 31 | -4 |
| 12 | §4.4 p.5 | Longitudinal = 7 | Table 8: 2 | +5 |
| 13 | §4.5 p.5 | User studies = 19 | Table 9: 17 | +2 |
| 14 | §4.5 p.5 | Lay users = 16 | Table 9: 13 | +3 |

**规律**：正文数字几乎全部大于附表数字（仅 Extended Dialogue 反向），暗示论文经历了一次数据修正——附表更新了但正文未同步。

---

## 逐条对照

### 矛盾 1：评估者数量（§4.1, p.4）

**原文**：

> "Automatic metrics appeared in 40 of 52 papers, human experts in 39, and LLM judges in 30; 21 papers combined all three."

**附表 Table 5（PDF p.14）**：

| 评估者类型 | 正文 | Table 5 | 差值 |
|---|---|---|---|
| Automatic Metrics | 40 | 35 | +5 |
| Human Experts | 39 | 34 | +5 |
| LLM Judges | 30 | 30 | 0 |
| All Three | 21 | 15（LaTeX Tab 1） | +6 |

---

### 矛盾 2：LLM Judge 验证数量（§4.1, p.4）

**原文**：

> "LLM-as-judge evaluation was common: 30 papers used LLM judges, and 26 reported some form of validation."

此字段无对应附表列，无法交叉验证。若正文正确，则 30 篇中有 26 篇做了验证（87%）。

---

### 矛盾 3：Rubric 可靠性报告数量（§4.1, p.4）

**原文**：

> "Forty-four papers used rubrics, but only 23 reported reliability or agreement (e.g., Cohen's kappa) for rubric-based judgments"

**附表 Table 6（PDF p.14）**：

| 指标 | 正文 | Table 6 | 差值 |
|---|---|---|---|
| Has Rubric = Yes | 44 | 13+31 = 44 | 0 ✓ |
| Reliability = Yes | 23 | 13+2 = 15 | **+8** |

---

### 矛盾 4：评估维度数量（§4.2, p.5）

**原文**：

> "Utility was the most common target (46 papers), followed by fidelity (35), realism (30), emotional plausibility (30), consistency (22), and safety (22)."

**附表 Table 7（PDF p.15）**：

| 维度 | 正文 | Table 7 | 差值 |
|---|---|---|---|
| Utility | 46 | 44 | +2 |
| Fidelity | 35 | 33 | +2 |
| Realism | 30 | 29 | +1 |
| Emotional Plausibility | 30 | 28 | +2 |
| Consistency | 22 | 20 | +2 |
| Safety | 22 | 14 | **+8** |

Safety 差异最大（正文比表格多 8 篇）。

---

### 矛盾 5：Extended Dialogue 篇数（§4.4, p.5）

**原文**：

> "Twenty-seven of 52 papers studied extended dialogues, and 19 used some form of dynamic state"

**附表 Table 8（PDF p.15）**：

Extended Dialogue = 16+7+7+1 = **31**（正文说 27，差 4）。

---

### 矛盾 6：Longitudinal 评估篇数（§4.4, p.5）

**原文**：

> "Only 7 papers reported longitudinal evaluation; among the 19 papers with dynamic state, 13 did not evaluate behavior longitudinally."

**附表 Table 8（PDF p.15）**：

Longitudinal = **2**（正文说 7，差 5）。

---

### 矛盾 7：Intervention-sensitive 篇数（§4.4, p.5）

**原文**：

> "39 papers involved intervention-sensitive evaluation or design, but only 7 of these included longitudinal evaluation."

此字段不在附表中，无法交叉验证。结合矛盾 6，"only 7 of these included longitudinal evaluation" 也可能不准确。

---

### 矛盾 8：User Studies / Lay Users 数量（§4.5, p.5）

**原文**：

> "User studies appeared in 19 of 52 papers, lay-user evaluation in 16, and explicit human learning or outcome measures in only 10."

**附表 Table 9（PDF p.15）**：

| 指标 | 正文 | Table 9 | 差值 |
|---|---|---|---|
| User Study = Yes | 19 | 4+5+5+3 = 17 | +2 |
| Lay Users = Yes | 16 | 4+5+4 = 13 | +3 |
| Human Learning = Yes | 10 | 4+5+1 = 10 | 0 ✓ |

---

### 矛盾 9：§4.5 重复引用 Utility / Safety（§4.5, p.5）

**原文**：

> "Utility was evaluated in 46 papers, but human learning or outcome evidence appeared in only 10. Safety was evaluated in 22 papers, but only a small number examined safety or deployment consequences."

与 §4.2 中的数字相同（46/22），同样与 Table 7 不一致（44/14）。

---

## LaTeX 表格结构性差异

除正文与附表的数值矛盾外，LaTeX `eval_tables.tex` 与 PDF 附表之间还有以下结构差异：

| 问题 | 说明 |
|---|---|
| LaTeX 缺少 Lay Users 行 | PDF Table 5 有 "Lay Users: 13 (25%)"，LaTeX Tab 1 未生成 |
| LaTeX 多了 All Three 行 | PDF Table 5 无此行，LaTeX Tab 1 有 "All Three: 15 (28.8%)" |
| LaTeX 缺少 Rubric (unknown) 行 | PDF Table 6 有 "(unknown)/N/A: 3"，LaTeX Tab 3 缺失，总计 49 ≠ 52 |
| Interaction 表合计 50 ≠ 52 | PDF Table 8 和 LaTeX Tab 7 均合计 50，缺 2 篇未归类 |

---

## 建议优先修正

按偏差严重程度排序：

1. **Safety（+8）**：正文 22 vs 表格 14，差异最大，影响安全相关论证力度
2. **Reliability reported（+8）**：正文 23 vs 表格 15，影响 rubric 可靠性论证
3. **All Three（+6）**：正文 21 vs LaTeX 15，影响三角验证论述
4. **Longitudinal（+5）**：正文 7 vs 表格 2，影响轨迹评估论证
5. **Auto Metrics（+5）**：正文 40 vs 表格 35
6. **Human Experts（+5）**：正文 39 vs 表格 34
