"""Constants and field definitions for the agentic extraction pipeline."""

# --- CSV Column Mapping (internal_name -> theme_track.csv header, order matters) ---
CSV_COLUMNS = [
    ("paper_id", "Paper_ID"),
    ("title", "Title"),
    ("year", "Year"),
    ("venue", "Venue"),
    ("domain", "Domain"),
    ("focus_type", "Focus_Type"),
    ("simulation_target", "Simulation_Target"),
    ("persona_model_depth", "Persona_Model_Depth"),
    ("uses_dynamic_state", "Uses_Dynamic_State"),
    ("temporal_modeling_details", "Temporal_Modeling_Details"),
    ("eval_human_experts", "Eval_Human_Experts"),
    ("eval_lay_users", "Eval_Lay_Users"),
    ("eval_user_study", "Eval_User_Study"),
    ("eval_llm_judge", "Eval_LLM_Judge"),
    ("eval_automatic", "Eval_Automatic"),
    ("dim_safety", "Safety"),
    ("dim_realism", "Realism"),
    ("dim_consistency", "Consistency"),
    ("dim_fidelity", "Fidelity"),
    ("dim_human_learning", "Human Learning / Outcomes"),
    ("dim_utility", "Utility"),
    ("dim_emotional_plausibility", "Emotional Plausibility"),
    ("raw_eval_metrics", "Raw Eval Metrics"),
    ("theory_operationalized", "Theory_Operationalized"),
    ("behavior_eval_depth", "Behavior_Eval_Depth"),
    ("intervention_sensitivity", "Interention_Sensitivity"),
    ("interaction_level", "Interaction_Level"),
    ("prompt_disclosure", "Prompt_Disclosure"),
    ("theory_grounding", "Theory_Grounding"),
    ("clinical_theory", "Clinical_Theory"),
    ("reliability_reported", "Reliability_Reported"),
    ("agreement_method", "Agreement Method"),
    ("coding_options", "Coding Options"),
    ("has_rubric", "Has_Rubric"),
    ("llm_judge_validated", "LLM_Judge_Validated"),
    ("uses_standard_metrics", "Uses_Standard_Metrics"),
    ("metric_interpretable", "Metric_Interpretable"),
    ("comparable_to_prior_work", "Comparable_To_Prior_Work"),
    ("has_longitudinal_eval", "Has_Longitudinal_Eval"),
    ("has_robustness_testing", "Has_Robustness_Testing"),
    ("has_failure_analysis", "Has_Failure_Analysis"),
    ("sim_behavior_realistic", "Sim_Behavior_Realistic"),
    ("dataset_available", "Dataset_Available"),
]

CSV_HEADER = [csv_name for _, csv_name in CSV_COLUMNS]
INTERNAL_TO_CSV = dict(CSV_COLUMNS)

# --- Field Groups ---

METADATA_FIELDS = ["title", "year", "venue", "domain"]

BOOL_FIELDS = [
    "eval_human_experts", "eval_lay_users", "eval_user_study",
    "eval_llm_judge", "eval_automatic",
    "dim_realism", "dim_consistency", "dim_fidelity",
    "dim_utility", "dim_human_learning", "dim_emotional_plausibility", "dim_safety",
    "uses_dynamic_state", "intervention_sensitivity",
    "has_rubric", "llm_judge_validated", "uses_standard_metrics",
    "metric_interpretable", "comparable_to_prior_work",
    "has_longitudinal_eval", "has_robustness_testing",
    "has_failure_analysis", "sim_behavior_realistic", "dataset_available",
]

SINGLE_CHOICE_FIELDS = {
    "simulation_target": ["Client Agent", "Therapist Agent", "Dual-Agent", "Human Trainee"],
    "persona_model_depth": [
        "Surface Persona", "Behavioral State Model",
        "Cognitive Model", "Dynamic Traits", "Expert Principles",
    ],
    "theory_operationalized": ["None", "Partial", "Strong"],
    "behavior_eval_depth": ["Dynamic", "Static", "None"],
    "interaction_level": ["None", "Short", "Extended", "Longitudinal"],
    "prompt_disclosure": ["Full", "Partial", "No"],
    "theory_grounding": ["Strong", "Weak", "None"],
    "reliability_reported": ["Yes", "No", "N/A"],
    "coding_options": ["Yes", "No", "N/A"],
}

FREE_TEXT_FIELDS = [
    "focus_type", "temporal_modeling_details", "raw_eval_metrics",
    "clinical_theory", "agreement_method",
]

STRUCTURED_FIELDS = BOOL_FIELDS + list(SINGLE_CHOICE_FIELDS.keys()) + FREE_TEXT_FIELDS

# --- Phase Definitions ---

PHASES = [
    {
        "name": "元数据",
        "fields": ["title", "year", "venue", "domain"],
        "type": "metadata",
    },
    {
        "name": "模拟/角色建模",
        "fields": [
            "focus_type", "simulation_target", "persona_model_depth",
            "uses_dynamic_state", "temporal_modeling_details",
        ],
    },
    {
        "name": "评估方法",
        "fields": ["eval_human_experts", "eval_lay_users", "eval_user_study",
                    "eval_llm_judge", "eval_automatic"],
    },
    {
        "name": "评估核心维度",
        "fields": ["dim_safety", "dim_realism", "dim_consistency", "dim_fidelity",
                    "dim_utility", "dim_human_learning", "dim_emotional_plausibility"],
    },
    {
        "name": "评估深度与理论",
        "fields": ["raw_eval_metrics", "theory_operationalized", "behavior_eval_depth",
                    "intervention_sensitivity", "interaction_level", "prompt_disclosure",
                    "theory_grounding", "clinical_theory"],
    },
    {
        "name": "信度与质量标记",
        "fields": ["reliability_reported", "agreement_method", "coding_options",
                    "has_rubric", "llm_judge_validated", "uses_standard_metrics",
                    "metric_interpretable", "comparable_to_prior_work",
                    "has_longitudinal_eval", "has_robustness_testing",
                    "has_failure_analysis", "sim_behavior_realistic", "dataset_available"],
    },
]

# --- Field Definitions (for prompts) ---
# Maps field name -> short definition string used in per-phase user messages.

FIELD_DEFINITIONS = {
    "title": "论文标题（原文）",
    "year": "发表年份（数字）",
    "venue": "发表场所（会议名/期刊名）",
    "domain": "研究领域（如 Counseling, Therapy, Mental Health 等）",
    "focus_type": "论文的主要研究焦点类型（开放分类）。如 SimulationFramework, EvaluationFramework, Dataset 等",
    "simulation_target": "模拟的对象: Client Agent / Therapist Agent / Dual-Agent / Human Trainee",
    "persona_model_depth": "模拟用户画像的建模深度: Surface Persona / Behavioral State Model / Cognitive Model / Dynamic Traits / Expert Principles",
    "uses_dynamic_state": "是否使用动态状态建模（YES/NO）",
    "temporal_modeling_details": "动态状态建模的具体方式描述",
    "eval_human_experts": "领域专家（治疗师、临床医生、受过训练的标注员）进行评估（YES/NO）",
    "eval_lay_users": "非专家/普通用户进行评估（YES/NO）",
    "eval_user_study": "结构化实验，用户与系统发生交互（YES/NO）",
    "eval_llm_judge": "使用大模型进行打分、比较、排序（YES/NO）",
    "eval_automatic": "算法/数学公式自动计算的指标（YES/NO）",
    "dim_safety": "是否避免有害/偏见输出（YES/NO）",
    "dim_realism": "输出是否像人类或自然（YES/NO）",
    "dim_consistency": "跨轮次行为是否稳定（YES/NO）",
    "dim_fidelity": "是否符合预设角色/目标（YES/NO）",
    "dim_utility": "对任务是否有用/有效（YES/NO）",
    "dim_human_learning": "是否带来人类进步/改变（YES/NO）",
    "dim_emotional_plausibility": "情绪反应是否真实/恰当（YES/NO）",
    "raw_eval_metrics": "实际使用的评估指标名称（自由文本）",
    "theory_operationalized": "理论操作化程度: None / Partial / Strong",
    "behavior_eval_depth": "行为变化评估深度: Dynamic / Static / None",
    "intervention_sensitivity": "系统行为是否根据输入发生适当变化（YES/NO）",
    "interaction_level": "对话上下文深度: None / Short / Extended / Longitudinal",
    "prompt_disclosure": "提示词披露程度: Full / Partial / No",
    "theory_grounding": "评估标准与理论挂钩程度: Strong / Weak / None",
    "clinical_theory": "具体使用的临床理论或框架名称（自由文本）。必须是论文原文明确引用的理论，若未明确引用则写 'Not specified'，禁止猜测或推断",
    "reliability_reported": "是否报告了标准化评估者间信度系数（如 Cohen's kappa, Krippendorff's alpha, ICC）: Yes / No / N/A。注意：仅报告平均差异(Avg.Diff)、标准差(Std.Dev)、百分比一致不算，必须有统计信度系数",
    "agreement_method": "具体使用的一致性评测方法（自由文本，若无则空字符串）",
    "coding_options": "是否明确报告了评估者之间的一致性: Yes / No / N/A",
    "has_rubric": "是否提供了明确的评分标准/评分指引（YES/NO）",
    "llm_judge_validated": "LLM裁判是否经过验证（YES/NO）",
    "uses_standard_metrics": "是否使用了标准/公认的评估指标（YES/NO）",
    "metric_interpretable": "评估指标的含义是否清晰可解释（YES/NO）",
    "comparable_to_prior_work": "评估是否可与先前研究进行对比（YES/NO）",
    "has_longitudinal_eval": "是否包含纵向/长期评估（YES/NO）",
    "has_robustness_testing": "是否在不同条件下进行了鲁棒性测试（YES/NO）",
    "has_failure_analysis": "是否分析了失败案例（YES/NO）",
    "sim_behavior_realistic": "模拟行为是否真实（YES/NO）",
    "dataset_available": "数据集是否公开可用（YES/NO）",
}
