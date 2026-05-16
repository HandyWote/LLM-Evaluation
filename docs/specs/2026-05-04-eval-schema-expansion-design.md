# 评估维度扩充设计

日期: 2026-05-04

## 背景

theme_track.csv 的 schema 包含 43 列，其中 ~22 列超出现有 7 表文档和 evaluate.py 的覆盖范围。需要：
1. 扩充 docs/ 下的评估维度表文档
2. 重写 evaluate.py 使输出严格对齐 theme_track.csv

## 设计原则

- 字段名称、顺序、选项严格对照 `docs/theme_track.csv`
- 字段定义严格按用户提供的标准
- 文档先定标准，代码对齐文档

## 第一部分：新增表格

在现有 7 表文档后追加以下 4 张表。

### 表 8：模拟/角色建模

| 字段 | 类型 | 定义 | 选项 |
|------|------|------|------|
| Focus_Type | 开放分类 | 论文的主要研究焦点类型 | SimulationFramework / EvaluationFramework / Dataset / Training System / Tool 等 |
| Simulation_Target | 单选 | 论文模拟的对象 | Client Agent: 模拟来访者 / Therapist Agent: 模拟咨询师 / Dual-Agent: 双方都模拟 / Human Trainee: 人类受训者 |
| Persona_Model_Depth | 单选 | 模拟用户画像的建模深度 | Surface Persona: 表层描述(如用文字profile) / Behavioral State Model: 行为状态模型 / Cognitive Model: 认知模型(含信念/动机等) / Dynamic Traits: 动态特质(随对话变化) / Expert Principles: 专家定义的原则 |
| Uses_Dynamic_State | YES/NO | 是否使用动态状态建模 | YES=有明确的动态状态追踪机制 |
| Temporal_Modeling_Details | 自由文本 | 动态状态建模的具体方式描述 | 如 State transitions / Session memory / Dynamic openness / Conversation principles update / Limited |

### 表 9：评估深度与理论操作化

| 字段 | 类型 | 定义 | 选项 |
|------|------|------|------|
| Raw_Eval_Metrics | 自由文本 | 论文实际使用的评估指标名称 | 如 "BLEU, ROUGE-L, BERTScore, human Likert 1-5" |
| Theory_Operationalized | 单选 | 理论是否被用于定义评估标准或指标，不仅仅是提及 | Strong: 评估标准明确源于理论 / Partial: 理论被提及并部分操作化 / None: 理论仅被提及或完全未使用 |
| Behavior_Eval_Depth | 单选 | 论文对交互过程中行为变化的评估深度 | Dynamic: 考虑行为如何随对话轮次演变 / Static: 仅评估单轮或静态输出 / None: 未评估行为 |
| Intervention_Sensitivity | YES/NO | 系统行为是否根据输入/干预发生适当变化 | 仅当论文明确测试了不同输入下行为的变化时标 YES |
| Clinical_Theory | 自由文本 | 具体使用的临床理论或框架名称 | 如 "CBT-inspired", "Motivational Interviewing", "Person-Centered Therapy" |

### 表 10：信度与方法论细节（补充表 6）

| 字段 | 类型 | 定义 | 选项 |
|------|------|------|------|
| Agreement_Method | 自由文本 | 具体使用的一致性评测方法 | 如 Cohen's kappa, Krippendorff's alpha。若无则留空 |
| Coding_Options | Yes / No / N/A | 论文是否明确报告了评估者之间的一致性 | Yes: 明确报告了评估者间的 agreement / No: 使用了人类评估但未报告 agreement 或 consistency / N/A: 没有使用人类评估 |

### 表 11：评估质量标记

| 字段 | 类型 | 定义 |
|------|------|------|
| Has_Rubric | YES/NO | 是否提供了明确的评分标准/评分指引 |
| LLM_Judge_Validated | YES/NO | LLM裁判是否经过验证（与人类评估对比等）。若未使用 LLM judge 则标 NO |
| Uses_Standard_Metrics | YES/NO | 是否使用了标准/公认的评估指标（非自创） |
| Metric_Interpretable | YES/NO | 评估指标的含义是否清晰可解释 |
| Comparable_To_Prior_Work | YES/NO | 评估是否可与先前研究进行对比 |
| Has_Longitudinal_Eval | YES/NO | 是否包含纵向/长期评估 |
| Has_Robustness_Testing | YES/NO | 是否在不同条件下进行了鲁棒性测试 |
| Has_Failure_Analysis | YES/NO | 是否分析了失败案例 |
| Sim_Behavior_Realistic | YES/NO | 模拟行为是否真实（非过于顺从或简化）。若未使用模拟则标 NO |
| Dataset_Available | YES/NO | 数据集是否公开可用 |

## 第二部分：evaluate.py 改动

### 移除

- `DEFECT_OPTIONS` 列表
- `defects` 字段
- 旧的 `CSV_FIELDS`、`ALL_EXTRACTION_FIELDS`

### 新增字段组

- `FREE_TEXT_FIELDS`: focus_type, temporal_modeling_details, raw_eval_metrics, clinical_theory, agreement_method
- 扩展 `BOOL_FIELDS`: 追加 uses_dynamic_state, intervention_sensitivity, has_rubric, llm_judge_validated, uses_standard_metrics, metric_interpretable, comparable_to_prior_work, has_longitudinal_eval, has_robustness_testing, has_failure_analysis, sim_behavior_realistic, dataset_available
- 扩展 `SINGLE_CHOICE_FIELDS`: 追加 simulation_target, persona_model_depth, theory_operationalized, behavior_eval_depth, coding_options

### CSV 列对齐

43 列严格匹配 theme_track.csv header，包括：
- `Human Learning / Outcomes`（含空格和斜杠）
- `Intervention_Sensitivity`（已修正拼写）
- `Agreement Method`、`Coding Options`（含空格）

使用 `CSV_COLUMNS` 元组列表维护 (internal_name → csv_header) 映射，确保顺序一致。

### 输出值格式

| 字段类型 | 输出格式 |
|----------|----------|
| 布尔 | YES / NO |
| 单选 | 选项文本（如 "Client Agent"、"Partial"） |
| 自由文本 | 原始文本 |
| 元数据 | 直接值（数字/字符串） |

### SYSTEM_PROMPT 重组

按 9 个 section 组织，字段定义严格对齐文档表格：
1. 基础元数据
2. 模拟/角色建模
3. 评估方法分类
4. 评估核心维度
5. 评估深度与理论操作化
6. 干预敏感性
7. 单选字段
8. 信度与方法论
9. 评估质量标记

### 幂等性

`load_existing_ids` 读取 CSV 的 `Paper_ID` 列判断已处理论文。若旧 `eval_results.csv` 存在但 schema 不同，需用户手动删除后重新运行。
