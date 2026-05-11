---
name: summarize-research-notes
description: Summarize and cross-compare research notes from eval_reports. Use when the user asks to summarize research notes, do cross-paper comparison, find commonalities/differences, or says "总结研究笔记", "跨论文对比", "求同求异", "总结评估方法论问题". Triggers on eval_reports/*.md analysis requests.
---

# Summarize Research Notes

综合多篇 eval_reports 的评估方法论批判。目标不是压缩信息，而是通过交叉对比揭示单篇论文看不到的结构性问题和研究机会。

## 核心理念

好的总结应该让读者读完后自然产生判断——"这个领域最大的结构性问题是 X"、"如果做 Y 就能填补空白"、"这个反常现象值得追问"。

为达到这个目标，本 skill 采用**维度×论文交叉矩阵**结构，每个维度下三层展开：
- **共性发现**：这批论文在该维度上普遍存在什么（求同）
- **逐篇差异**：每篇论文的具体表现，精确到一句话（不丢信息）
- **反常信号**：不符合预期的观察、跨论文矛盾、值得追问的蛛丝马迹（求异）

## 固定核心维度

以下 10 个维度跨批次固定出现，保证不同批次的 summary 可以直接横向对比：

| # | 维度名称 | 对应 CSV 字段 | 关注点 |
|---|---------|-------------|--------|
| 1 | 评估方法组合 | Eval_Human_Experts, Eval_Lay_Users, Eval_LLM_Judge, Eval_Automatic, Eval_User_Study | 用了哪些评估方法，如何组合 |
| 2 | 理论操作化 | Theory_Operationalized, Theory_Grounding, Clinical_Theory | 评估标准是否有理论根基，还是凭直觉 |
| 3 | 信度报告 | Reliability_Reported, Agreement_Method, Coding_Options | 人类评估的一致性是否被测量和报告 |
| 4 | LLM 裁判验证 | Eval_LLM_Judge, LLM_Judge_Validated | LLM 打分是否与人类对比，如何对比 |
| 5 | 交互层级 | Interaction_Level | 单轮 vs 多轮 vs 纵向，对心理治疗评估的影响 |
| 6 | 行为评估深度 | Behavior_Eval_Depth, Intervention_Sensitivity | 静态输出评估 vs 动态行为变化追踪 |
| 7 | 失败分析 | Has_Failure_Analysis | 是否分析了失败案例，分析的深度 |
| 8 | 模拟保真度 | Sim_Behavior_Realistic, Simulation_Target, Persona_Model_Depth | 模拟用户/来访者是否接近真实行为 |
| 9 | 人类专家参与 | Eval_Human_Experts, Has_Rubric | 专家参与的方式、规模、是否有评分标准 |
| 10 | 指标与可复现性 | Uses_Standard_Metrics, Metric_Interpretable, Comparable_To_Prior_Work, Dataset_Available | 用的指标是否标准、可解释、可对比 |

## 涌现维度

除了固定维度外，每批论文可能有独特的观察角度，不强行归入固定维度。比如：
- "跨模型鲁棒性"（如果多篇做了不同模型的对比）
- "数据构建与评估的循环依赖"（如果多篇存在同源性问题）
- "文化/语言多样性"（如果涉及多语言或跨文化场景）
- "安全性评估"（如果多篇涉及 Safety 维度）

涌现维度同样使用三层结构（共性/差异/反常信号），但不要为了凑数硬造。

## 工作流

### Step 1: 检测未总结的论文

```bash
cd extract && uv run ../.claude/skills/summarize-research-notes/scripts/find_unsummarized.py eval_reports
```

脚本输出 JSON：
```json
{"unsummarized": ["1", "6", "10"], "total_with_notes": 10, "already_summarized": 7}
```

**如果 `unsummarized` 为空**：告诉用户"所有研究笔记都已总结"，结束。

### Step 2: 读取未总结论文

读取 `eval_reports/` 下 `unsummarized` 列表中的每篇 `.md` 文件。重点关注 `## 研究笔记` section。

同时读取 `eval_results.csv` 中对应论文的行，获取结构化字段值作为参考。

### Step 3: 逐篇提取评估事实

对每篇论文，从研究笔记中提取**具体事实**，不压缩、不改写、不评价。每篇论文需要提取：

1. **研究目标声称**：论文宣称要做什么（原文引用）
2. **实际评估做法**：论文实际怎么评的（具体方法、指标、参与者）
3. **评估方法细节**：用了什么指标、多少人评的、有没有报告信度、有没有评分标准
4. **关键发现/局限**：论文自己报告的重要发现或坦承的局限
5. **独特观察**：任何值得注意的细节（好的或坏的）

### Step 4: 维度×论文交叉分析

对每个固定核心维度 + 识别到的涌现维度，构建三层分析：

**共性发现**：
- 这批论文在该维度上的共同模式是什么？
- 用 1-2 句话概括，引用具体论文编号。

**逐篇差异**：
- 每篇论文在这个维度上的具体表现，用一句话精确描述。
- 格式：`- Paper {id}: {具体表现}`
- 不要概括，要具体。"Paper 10 做了 LLM 验证" 不够好；"Paper 10 发现 GPT-4o 与人类专家 Pearson r=0.11-0.19，但止步于'不能盲目用'的结论" 才够好。

**反常信号**：
- 有没有不符合预期的观察？
- 跨论文之间有没有矛盾？（比如一篇说 LLM 和人类不一致，另一篇说比众包更接近专家）
- 有没有"差一点就做好了"的案例？（方法对了但执行不到位）
- 有没有"歪打正着"的发现？（论文自己可能没意识到其发现的价值）
- 用 1-3 句话描述，指出为什么这个信号值得关注。

### Step 5: 识别研究机会

基于 Step 4 的交叉分析，识别具体的未来研究方向。每个机会对应一个明确的行动：

- **缺口型**："目前没有人做过 X，但 X 很重要"
- **矛盾型**："论文 A 和论文 B 的发现矛盾，说明 Y 的影响因素需要进一步研究"
- **改进型**："论文 C 差一点就做好了，如果把 D 和 E 结合起来就能解决"

格式：每个机会用 1-2 句话描述，句式为"如果做 X，就能解决/填补/验证 Y"。

### Step 6: 生成总结文档

文件名：`summary-{id1}-{id2}-...-{idN}.md`（ID 排序，`-` 连接）

输出到 `extract/eval_reports/summary-{ids}.md`，结构如下：

```markdown
# 研究笔记总结：Paper {id1}, {id2}, ..., {idN}

> 生成时间：{date}
> 论文列表：{id1} — {title1}，{id2} — {title2}，...

## 一、各论文评估概况

### Paper {id}: {title}
- **声称目标**：{一句话}
- **实际评估**：{评估方法概要}
- **核心方法**：{具体指标/参与者/规模}
- **关键发现**：{论文自身报告的最重要发现}
- **主要局限**：{最致命的 1-2 个问题}

（每篇论文一个小节，5-8 行，精炼但不丢关键信息）

## 二、维度交叉分析

### 固定维度 1：评估方法组合
**共性**：{1-2 句话}
**逐篇差异**：
- Paper {id}: {具体表现}
- Paper {id}: {具体表现}
...
**反常信号**：{1-3 句话，或"无明显反常"}

### 固定维度 2：理论操作化
（同上结构）

...（所有 10 个固定维度）

### 涌现维度：{名称}
（同上结构，仅在有明确模式时出现）

## 三、研究机会

1. {机会描述}（对应维度：{维度名}，支撑论文：{id列表}）
2. ...
3. ...

## 四、量化矩阵

| 维度 | Paper {id1} | Paper {id2} | ... |
|------|:-----------:|:-----------:|:---:|
| {维度1} | {简短标记} | {简短标记} | ... |
| {维度2} | ... | ... | ... |
| ... | ... | ... | ... |

> 矩阵中每个单元格用 2-5 个字标记该论文在该维度上的状态（如"有但浅"、"缺失"、"规范"、"N/A"），具体细节见上方逐篇差异。
```

如果 summary 文件已存在，提示用户是否覆盖。

### Step 7: 打标记

```bash
cd extract && uv run ../.claude/skills/summarize-research-notes/scripts/mark_summarized.py \
  --papers {id1},{id2},... --summary summary-{ids}.md --dir eval_reports
```

### Step 8: 告知用户

告诉用户：
1. 总结文件位置
2. 本轮最值得关注的 **2-3 个反常信号**（简短描述 + 为什么重要）
3. 最有潜力的 **2-3 个研究机会**（简短描述）
4. 哪篇论文在方法论上最值得学习、哪篇问题最大

## 写作风格

- 事实优先，评价其次。先说"Paper X 做了什么"，再说"这说明什么"。
- 引用具体数字和细节（Cohen's κ=0.02-0.09，Pearson r=0.11-0.19），不要概括为"信度很低"。
- 反常信号要尖锐——"这个矛盾暗示了什么"比"这是一个问题"有价值得多。
- 研究机会要具体——"如果做 X 就能解决 Y"比"需要进一步研究"有价值得多。
- 表格做量化，但量化矩阵是索引，细节在正文中。

## 注意事项

- 不要为了聚类而聚类。如果某篇论文在某个维度上有独特表现，就如实写，不要削足适履。
- 反常信号不必每维度都有，"无明显反常"是正常的。
- 研究机会不必每维度都有，有些维度可能已经做得很好了。
- 没有研究笔记的论文跳过，在开头注明。
- 读取 eval_results.csv 时注意字段拼写差异（如 `Interention_Sensitivity` 应为 `Intervention_Sensitivity`）。
