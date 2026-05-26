# 论文正文数据修正报告（最终版）

> 论文：*From Surface Realism to Behavioral Validity: Rethinking Evaluation for Repurposed Interactive LLM Systems*
> 数据源：`compare/final-table.csv`（52 篇论文，NaN 已全部修复）
> Theory 数据源：`table/theory_eval_refined_coding_refined.csv`（三级分类，与正文一致）
> 检查日期：2026-05-26
> LaTeX 表格：已从 `final-table.csv` 重新生成（`table/eval_tables.tex`）

---

## 需修改的正文数字

### §4.1 Evaluation authority is broad but unevenly grounded (p.4)

**修改 1** — 评估者数量

> "Automatic metrics appeared in **40** of 52 papers, human experts in **39**, and LLM judges in 30; **21** papers combined all three."

| 原数字 | 正确值 | 字段 | 差值 |
|--------|--------|------|------|
| 40 | **35** | Eval_Automatic | -5 |
| 39 | **34** | Eval_Human_Experts | -5 |
| 21 | **15** | 三者交集 (Expert∩LLM∩Auto) | -6 |

建议改为：*"Automatic metrics appeared in **35** of 52 papers, human experts in **34**, and LLM judges in 30; **15** papers combined all three."*

---

**修改 2** — LLM Judge 验证数量

> "30 papers used LLM judges, and **26** reported some form of validation."

| 原数字 | 正确值 | 字段 | 差值 |
|--------|--------|------|------|
| 26 | **24** | LLM_Judge_Validated | -2 |

建议改为：*"30 papers used LLM judges, and **24** reported some form of validation."*

---

**修改 3** — Rubric 与信度

> "Forty-four papers used rubrics, but only **23** reported reliability or agreement"

| 原数字 | 正确值 | 字段 | 差值 |
|--------|--------|------|------|
| 44 | **45** | Has_Rubric | +1 |
| 23 | **16** | Reliability_Reported | -7 |

建议改为：*"Forty-five papers used rubrics, but only **16** reported reliability or agreement"*

注：Reliability_Reported 从之前报告的 15 修正为 16（Tanana2019Development 的 NaN 已修复为 "Yes"）。

---

### §4.2 Output quality is overused as a proxy for behavioral validity (p.4–5)

**修改 4** — 覆盖广度

> "**All 52** papers evaluated at least one local quality dimension, and **39** evaluated three or more."

| 原数字 | 正确值 | 字段 | 差值 |
|--------|--------|------|------|
| All 52 | **50** | 7 维度列 ≥1 Yes | -2 |
| 39 | **41** | 7 维度列 ≥3 Yes | +2 |

建议改为：*"**50** of 52 papers evaluated at least one local quality dimension, and **41** evaluated three or more."*

---

**修改 5** — 各维度数量

> "Utility was the most common target (**46** papers), followed by fidelity (**35**), realism (**30**), emotional plausibility (**30**), consistency (**22**), and safety (**22**)."

| 维度 | 原数字 | 正确值 | 差值 |
|------|--------|--------|------|
| Utility | 46 | **44** | -2 |
| Fidelity | 35 | **33** | -2 |
| Realism | 30 | **29** | -1 |
| Emotional Plausibility | 30 | **28** | -2 |
| Consistency | 22 | **20** | -2 |
| Safety | 22 | **14** | **-8** |

建议改为：*"Utility was the most common target (**44** papers), followed by fidelity (**33**), realism (**29**), emotional plausibility (**28**), consistency (**20**), and safety (**14**)."*

---



### §4.4 Dynamic design outpaces trajectory evaluation (p.5)

**修改 7** — 交互与动态

> "Twenty-**seven** of 52 papers studied extended dialogues, and **19** used some form of dynamic state"

| 原数字 | 正确值 | 字段 | 差值 |
|--------|--------|------|------|
| 27 | **31** | Interaction_Level = Extended Dialogue | +4 |
| 19 | **13** | Uses_Dynamic_State = Yes | -6 |

建议改为：*"Thirty-one of 52 papers studied extended dialogues, and **13** used some form of dynamic state"*

---

**修改 8** — 纵向评估

> "Only **7** papers reported longitudinal evaluation"

| 原数字 | 正确值 | 字段 | 差值 |
|--------|--------|------|------|
| 7 | **3** | Has_Longitudinal_Eval = Yes | -4 |

建议改为：*"Only **3** papers reported longitudinal evaluation"*

证据：Qiu2025EmoAgent, Li2024Understanding, Wang2025Psychological

---

**修改 9** — 动态状态与纵向评估

> "among the **19** papers with dynamic state, **13** did not evaluate behavior longitudinally."

| 原数字 | 正确值 | 逻辑 | 差值 |
|--------|--------|------|------|
| 19 | **13** | Uses_Dynamic_State=Yes 总数 | -6 |
| 13 | **11** | Dynamic=Yes 且 Longitudinal=No | -2 |

建议改为：*"among the **13** papers with dynamic state, **11** did not evaluate behavior longitudinally."*

---

**修改 10** — 干预敏感与纵向

> "**39** papers involved intervention-sensitive evaluation or design, but only **7** of these included longitudinal evaluation."

| 原数字 | 正确值 | 字段 | 差值 |
|--------|--------|------|------|
| 39 | **39** | Interention_Sensitivity = Yes | ✓ |
| 7 | **3** | Intervention=Yes ∩ Longitudinal=Yes | -4 |

建议改为：*"39 papers involved intervention-sensitive evaluation or design, but only **3** of these included longitudinal evaluation."*

---

### §4.5 Human-facing motivations often outpace human-facing evidence (p.5–6)

**修改 11** — 用户研究

> "User studies appeared in **19** of 52 papers, lay-user evaluation in **16**, and explicit human learning or outcome measures in only 10."

| 原数字 | 正确值 | 字段 | 差值 |
|--------|--------|------|------|
| 19 | **17** | Eval_User_Study = Yes | -2 |
| 16 | **13** | Eval_Lay_Users = Yes | -3 |
| 10 | **10** | Human Learning / Outcomes = Yes | ✓ |

建议改为：*"User studies appeared in **17** of 52 papers, lay-user evaluation in **13**, and explicit human learning or outcome measures in only 10."*

---

**修改 12** — 无超越模型输出的评估

> "Across the corpus, **36** papers showed no clear evaluation beyond model outputs"

| 原数字 | 正确值 | 逻辑 | 差值 |
|--------|--------|------|------|
| 36 | **34** | UserStudy=No 且 Human Learning=No | -2 |

建议改为：*"Across the corpus, **34** papers showed no clear evaluation beyond model outputs"*

---

**修改 13** — Utility 与 Human Learning（§4.5 重复 §4.2 数据）

> "Utility was evaluated in **46** papers, but human learning or outcome evidence appeared in only 10."

| 原数字 | 正确值 | 字段 | 差值 |
|--------|--------|------|------|
| 46 | **44** | Utility = Yes | -2 |
| 10 | **10** | Human Learning = Yes | ✓ |

建议改为：*"Utility was evaluated in **44** papers, but human learning or outcome evidence appeared in only 10."*

---

**修改 14** — Safety（§4.5 重复 §4.2 数据）

> "Safety was evaluated in **22** papers, but only a small number examined safety or deployment consequences."

| 原数字 | 正确值 | 字段 | 差值 |
|--------|--------|------|------|
| 22 | **14** | Safety = Yes | -8 |

建议改为：*"Safety was evaluated in **14** papers, but only a small number examined safety or deployment consequences."*

---

**保留** — 模拟被试（无法从 CSV 验证）

> "8 papers measured outcomes only in simulated clients or patients"

CSV 中无对应列，需人工核对。

---

## 汇总表

| # | 位置 | 原文关键字 | 原数字 | 正确值 | 字段 | 差值 |
|---|------|-----------|--------|--------|------|------|
| 1a | §4.1 | Auto Metrics | 40 | **35** | Eval_Automatic | -5 |
| 1b | §4.1 | Human Experts | 39 | **34** | Eval_Human_Experts | -5 |
| 1c | §4.1 | All Three | 21 | **15** | 三者交集 | -6 |
| 2 | §4.1 | LLM Validated | 26 | **24** | LLM_Judge_Validated | -2 |
| 3a | §4.1 | Has Rubric | 44 | **45** | Has_Rubric | +1 |
| 3b | §4.1 | Reliability | 23 | **16** | Reliability_Reported | **-7** |
| 4a | §4.2 | ≥1 维度 | 52 | **50** | 7 维度列 | -2 |
| 4b | §4.2 | ≥3 维度 | 39 | **41** | 7 维度列 | +2 |
| 5a | §4.2 | Utility | 46 | **44** | Utility | -2 |
| 5b | §4.2 | Fidelity | 35 | **33** | Fidelity | -2 |
| 5c | §4.2 | Realism | 30 | **29** | Realism | -1 |
| 5d | §4.2 | Emo Plausibility | 30 | **28** | Emotional Plausibility | -2 |
| 5e | §4.2 | Consistency | 22 | **20** | Consistency | -2 |
| 5f | §4.2 | Safety | 22 | **14** | Safety | **-8** |
| 7a | §4.4 | Extended Dialogue | 27 | **31** | Interaction_Level | +4 |
| 7b | §4.4 | Dynamic State | 19 | **13** | Uses_Dynamic_State | -6 |
| 8 | §4.4 | Longitudinal | 7 | **3** | Has_Longitudinal_Eval | **-4** |
| 9a | §4.4 | Dynamic total | 19 | **13** | Uses_Dynamic_State | -6 |
| 9b | §4.4 | Dynamic no long | 13 | **11** | Dynamic∩~Longitudinal | -2 |
| 10b | §4.4 | Intervention+Long | 7 | **3** | Intervention∩Longitudinal | -4 |
| 11a | §4.5 | User Study | 19 | **17** | Eval_User_Study | -2 |
| 11b | §4.5 | Lay Users | 16 | **13** | Eval_Lay_Users | -3 |
| 12 | §4.5 | No beyond model | 36 | **34** | ~UserStudy∩~HL | -2 |
| 13 | §4.5 | Utility (重复) | 46 | **44** | Utility | -2 |
| 14 | §4.5 | Safety (重复) | 22 | **14** | Safety | **-8** |

**共 25 处需修改**（其中 §4.3 的 5 个 Theory 数字确认正确，无需修改）。

---

## 无需修改的数字

| 正文描述 | 数字 | 来源 | 状态 |
|----------|------|------|------|
| LLM Judges = 30 | 30 | Eval_LLM_Judge | ✓ |
| Human Learning = 10 | 10 | Human Learning / Outcomes | ✓ |
| Theory Strong = 40 | 40 | theory_eval file | ✓ |
| Theory Partial = 10 | 10 | theory_eval file | ✓ |
| Theory Op Strong = 30 | 30 | theory_eval file | ✓ |
| Theory Op Partial = 16 | 16 | theory_eval file | ✓ |
| Theory Op None = 6 | 6 | theory_eval file | ✓ |
| Intervention Sensitivity = 39 | 39 | Interention_Sensitivity | ✓ |

---

## 需人工核对的数字

| 正文描述 | 数字 | 说明 |
|----------|------|------|
| Table 4: Validated scales = 9 | 9 | CSV 无对应汇总列 |
| Table 4: Therapy coding = 7 | 7 | CSV 无对应汇总列 |
| Table 4: Theory rubrics = 35 | 35 | CSV 无对应汇总列 |
| Table 4: Theory benchmarks = 26 | 26 | CSV 无对应汇总列 |
| Simulated-only outcomes = 8 | 8 | CSV 无对应列 |

---

## 最大偏差（按严重程度排序）

1. **Safety（-8）**：正文 22 vs CSV 14 — 影响安全相关论证力度
2. **Reliability（-7）**：正文 23 vs CSV 16 — 影响 rubric 可靠性论证
3. **All Three（-6）**：正文 21 vs CSV 15 — 影响三角验证论述
4. **Dynamic State（-6）**：正文 19 vs CSV 13
5. **Longitudinal（-4）**：正文 7 vs CSV 3 — 影响轨迹评估论证

---

