---
name: verify-disagreement-judgment
description: Verify all Final_Judgment in disagreement_cn.csv against three evidence sources (CSV evidence, cxt evidence, eval_reports). Use when the user says "校验分歧判定", "验证disagreement", "check judgment", or wants to verify review decisions. Spawns one subagent per paper to check all fields at once.
---

# Verify Disagreement Judgments

校验 `compare/disagreement_cn.csv` 中「修正判定」列的正确性。

## 证据源（三合一）

对每个分歧，综合以下三个证据源判断：

| # | 来源 | 位置 |
|---|------|------|
| 1 | 原始证据 | CSV「原始证据」列（eval_report 提取的证据） |
| 2 | cxt 补充证据 | CSV「cxt补充证据」列 |
| 3 | eval_report | `eval_reports/{Paper_ID}.md` 中该字段的编码值和证据 |
| 4 | PDF 原文（仅在矛盾时） | `extract/paper/{Paper_ID}.pdf` |

## 执行流程

### Step 1: 读取 CSV，按论文分组

```bash
python3 -c "
import csv
from collections import defaultdict
with open('compare/disagreement_cn.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))
groups = defaultdict(list)
for i, r in enumerate(rows):
    groups[r['Paper_ID']].append((i, r))
for pid, items in sorted(groups.items(), key=lambda x: int(x[0])):
    fields = [it[1]['字段中文'] for it in items]
    print(f'Paper {pid}: {len(items)} 个分歧 — {', '.join(fields)}')
"
```

### Step 2: 对每篇论文启动一个 Agent

每篇论文一个 Agent，一次性校验该论文的所有分歧。

Agent prompt 模板：

```
你是学术评估校验专家。请校验 Paper {Paper_ID} 的所有分歧判定。

## 任务

对以下每个分歧，综合三个证据源判断「修正判定」是否正确：

1. CSV 原始证据（eval_report 提取）
2. CSV cxt 补充证据
3. eval_reports/{Paper_ID}.md 中的编码值和证据

如果三个证据源有矛盾，读取 extract/paper/{Paper_ID}.pdf 原文确认。

## 待校验分歧

{对该论文每个分歧的描述，包含：字段名、定义、cxt值、hyh值、修正判定、原始证据、cxt补充证据}

## 判定原则

{根据字段类型插入对应原则，见下方速查表}

## 输出格式

对每个分歧输出：
- 字段名
- 当前判定: xxx
- 是否正确: ✓ / ✗ / ⚠需确认
- 证据摘要: (简述三个证据源的关键信息)
- 建议修正: xxx（如果不需要修正写"无"）
- 理由: ...

最后输出 JSON 总结：
{"results": [{"row": 行号, "correct": true/false/"confirm", "new_judgment": "值或null", "reason": "理由"}, ...]}
```

### Step 3: 收集结果，更新 CSV

从每个 Agent 的 JSON 输出中提取结果，更新 CSV：

```bash
python3 -c "
import csv
with open('compare/disagreement_cn.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys())

# 应用修正
for result in results:
    idx = result['row']
    if not result['correct'] and result.get('new_judgment'):
        rows[idx]['修正判定'] = result['new_judgment']
        rows[idx]['理由'] = result['reason'] + ' (校验修正)'

with open('compare/disagreement_cn.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
"
```

### Step 4: 输出汇总报告

```
## 校验报告

- 总分歧: 220
- ✓ 正确: xxx
- ✗ 已修正: xxx
- ⚠ 需人工确认: xxx

### 已修正项
| Paper | 字段 | 原判定 | 新判定 | 理由 |
|-------|------|--------|--------|------|

### 需确认项
| Paper | 字段 | 当前判定 | 矛盾点 | 建议 |
|-------|------|----------|---------|------|
```

## 判定原则速查

### Boolean 字段

| 字段 | YES 条件 | NO 条件 | 易错点 |
|------|----------|---------|--------|
| Eval_Automatic | 算法/公式自动计算指标 | 人打分后算指标、LLM打分 | G-Eval≠自动，归入LLM_Judge |
| Eval_Lay_Users | 非专家参与**评估** | 非专家只参与生成数据 | 生成数据≠评估 |
| Eval_Human_Experts | 领域专家参与**评估** | 专家参与数据准备 | 区分数据准备vs评估阶段 |
| Eval_LLM_Judge | LLM 做打分/分析/标注/评估 | LLM 仅做特征提取 | G-Eval归入此类 |
| LLM_Judge_Validated | 有 Cohen's Kappa/ICC 验证 | 仅百分比一致 | 百分比一致≠标准化系数 |
| Fidelity | 评估了角色保真度/目标对齐 | 评估通用质量(Helpfulness等) | 通用质量≠保真度 |
| Uses_Dynamic_State | 有前后测或持续状态追踪 | 无动态状态 | — |
| Safety | 评估**测试**了有害输出 | 仅有伦理声明/措施 | 伦理委员会≠安全评估 |
| Utility | 评估了有用性/有效性 | 仅陈述系统有用 | 声明有用≠评估有用 |
| Has_Rubric | 有明确评分标准（Likert 标签算） | 无评分标准 | — |
| Has_Robustness_Testing | 不同模型/条件测试或消融实验 | 数据集设计多样性 | 数据集多样≠鲁棒性测试 |
| Has_Failure_Analysis | 分析了失败案例或局限性 | 无失败分析 | — |
| Has_Longitudinal_Eval | 有纵向跨会话评估 | 系统有长期记忆但未评估 | 系统设计≠评估 |
| Reliability_Reported | 报告了 kappa/alpha/ICC | 仅百分比一致 | — |
| Emotional Plausibility | 评估了**客户**情绪真实性 | 评估咨询师共情能力 | 咨询师≠客户 |
| Realism | 评估了输出是否像人类 | 未评估真实性 | — |
| Sim_Behavior_Realistic | 评估了模拟行为真实性 | 未评估 | — |

### 单选字段

| 字段 | 选项 | 关键区分 | 易错点 |
|------|------|---------|--------|
| Behavior_Eval_Depth | DYNAMIC / PATTERN-LEVEL / STATIC / None | DYNAMIC=分析轮次间变化轨迹；PATTERN-LEVEL=统计频率分布；STATIC=聚合分数或前后测 | 前后测对比=STATIC，不是DYNAMIC |
| Prompt_Disclosure | FULL / PARTIAL / NO | 附录有 prompt ≠ NO | 附录有prompt模板=Full/Partial |
| Interaction_Level | SINGLE-TURN / SHORT MULTI-TURN / EXTENDED DIALOGUE / LONGITUDINAL | 跨会话=LONGITUDINAL | — |
| Persona_Model_Depth | SURFACE / BEHAVIORAL STATE / COGNITIVE / DYNAMIC TRAITS / EXPERT PRINCIPLES | 看建模复杂度 | — |
| Theory_Grounding | STRONG / WEAK / NONE | STRONG=理论指导评估设计 | 提及理论但未用于评估=WEAK |
| Theory_Operationalized | STRONG / PARTIAL / MENTIONED / NONE | STRONG=评估标准明确源于理论 | 仅在讨论中提及=MENTIONED |
| Simulation_Target | CLIENT AGENT / THERAPIST AGENT / DUAL-AGENT / HUMAN TRAINEE | 看模拟的是谁 | — |

## 校验方法论：六大易错模式

从实际校验中总结的高频错误模式。校验时必须逐一排查。

### 模式 1: 阶段混淆 — 数据准备 ≠ 评估

**错误**: 把数据准备阶段的专家参与当作"领域专家评估"。

**正确判断**:
- 专家**审查/修正训练数据** → 数据准备阶段 → 不算 Eval_Human_Experts
- 专家**评估系统输出质量** → 评估阶段 → 算 Eval_Human_Experts

**排查问题**: "专家介入发生在哪个阶段？是数据预处理还是评估系统表现？"

**实际案例** (Paper 18):
```
✗ 错误: Eval_Human_Experts=YES
  理由: 3位心理学专家审查修正主诉链条
✓ 正确: Eval_Human_Experts=NO
  理由: 专家审查主诉链条属于数据准备(Section 3)，
        评估环节完全自动化(BERT-score/G-Eval)(Section 4)
```

### 模式 2: 设计 vs 评估 — 系统设计 ≠ 评估方法

**错误**: 把系统的动态设计当作"动态行为评估"。

**正确判断**:
- 系统**设计**了动态状态追踪（情绪推断器、记忆机制）→ 系统设计
- **评估**方法分析了行为如何随轮次变化 → 评估方法

**排查问题**: "论文的评估部分（不是系统设计部分）是否测量了轮次间变化？"

**实际案例** (Paper 18):
```
✗ 错误: Behavior_Eval_Depth=DYNAMIC
  理由: 系统有情绪推断器和主诉变化链
✓ 正确: Behavior_Eval_Depth=STATIC
  理由: 评估只用BERT-score和G-Eval聚合分数，
        没有分析行为如何随轮次变化
```

### 模式 3: 评估对象混淆 — 咨询师 ≠ 客户

**错误**: 把对咨询师技能的评估当作对客户情绪真实性的评估。

**正确判断**:
- Empathy 评估**咨询师**理解和回应情绪的能力 → 咨询师技能
- Emotional Plausibility 评估**客户**情绪反应是否真实 → 客户真实性

**排查问题**: "这个指标评估的是谁？是咨询师/治疗师的表现，还是客户/模拟对象的真实性？"

**实际案例** (Paper 83):
```
✗ 错误: Emotional Plausibility=YES
  理由: 评估标准包含Empathy
✓ 正确: Emotional Plausibility=NO
  理由: Empathy定义为"咨询师理解和回应客户情绪的能力"(p.13)，
        评估的是咨询师技能，不是客户情绪真实性
```

### 模式 4: 指标分类混淆 — LLM 打分 ≠ 算法自动

**错误**: 把 G-Eval（LLM 按 rubric 打分）当作"算法/公式自动计算"。

**正确判断**:
- BLEU, ROUGE, F1, Accuracy → 算法/公式自动计算 → Eval_Automatic=YES
- G-Eval, GPT-4 打分, LLM-as-judge → LLM 打分 → Eval_LLM_Judge=YES, Eval_Automatic=NO
- PANAS, CTRS, Likert 问卷 → 人工填写 → 不是自动

**排查问题**: "这个指标是算法/公式算出来的，还是 LLM/人类打出来的？"

**注意**: G-Eval 应归入 Eval_LLM_Judge，不归入 Eval_Automatic。两者互斥。

**实际案例** (Paper 83):
```
✗ 错误: Eval_Automatic=YES
  理由: 使用了G-Eval、CTRS、PANAS
✓ 正确: Eval_Automatic=NO
  理由: G-Eval是LLM打分，PANAS是人工问卷，CTRS是专家打分，
        都不是算法自动计算。G-Eval应归入eval_llm_judge。
```

### 模式 5: 聚合 vs 动态 — 前后测 ≠ 轮次间分析

**错误**: 把前后测对比（咨询前 vs 咨询后）当作"动态行为评估"。

**正确判断**:
- 前后测对比（2个时间点）→ 静态比较 → STATIC
- 分析每轮行为如何变化（多个时间点）→ 动态分析 → DYNAMIC
- 统计行为频率分布（不关心变化方向）→ 模式统计 → PATTERN-LEVEL

**排查问题**: "是对比了两个时间点（前/后），还是分析了多个时间点间的变化轨迹？"

**实际案例** (Paper 83):
```
✗ 错误: Behavior_Eval_Depth=DYNAMIC
  理由: PANAS测量咨询前后情绪变化
✓ 正确: Behavior_Eval_Depth=STATIC
  理由: PANAS只对比咨询前和咨询后两个时间点，
        是静态比较，不是轮次间变化分析
```

### 模式 6: 声明 vs 评估 — 说有用 ≠ 证明有用

**错误**: 把论文对系统有用性的声明/愿景当作"实用性评估"。

**正确判断**:
- 论文**声明**系统"提供创新解决方案"、"开辟新路径" → 声明/愿景
- 论文**评估**了系统对任务的实际效果 → 评估

同理适用于：
- Safety: 有伦理审查委员会/数据开源限制 → 伦理声明，不是安全评估
- Fidelity: 评估 Helpfulness/Empathy 等通用质量 → 不是角色保真度评估

**排查问题**: "论文是'声称'系统有用/安全，还是'评估'了系统有用/安全？证据在评估部分还是讨论部分？"

**实际案例** (Paper 18):
```
✗ 错误: Utility=YES, Safety=YES
  理由: 论文说"为缓解资源短缺提供创新方案"，有伦理审查委员会
✓ 正确: Utility=NO, Safety=NO
  理由: "提供创新方案"是声明不是评估；
        伦理审查委员会是伦理措施，不是安全评估
```

---

## 决策流程图

遇到分歧时，按以下流程排查：

```
1. 证据来自哪个阶段？
   ├── 数据准备阶段 → 不算评估相关字段
   └── 评估阶段 → 继续

2. 证据描述的是系统设计还是评估方法？
   ├── 系统设计 → 不能作为评估深度的依据
   └── 评估方法 → 继续

3. 评估的对象是谁？
   ├── 咨询师/治疗师 → 归入咨询师技能相关字段
   └── 客户/模拟对象 → 归入真实性/情绪相关字段

4. 指标是怎么计算的？
   ├── 算法/公式 → Eval_Automatic
   ├── LLM 打分 → Eval_LLM_Judge
   └── 人工打分/问卷 → 都不是

5. 测量了几个时间点？
   ├── 2个（前/后）→ STATIC
   ├── 多个（轮次间）→ DYNAMIC
   └── 不关心变化 → PATTERN-LEVEL

6. 是声明还是评估？
   ├── 在讨论/意义部分 → 声明
   └── 在方法/结果部分 → 评估
```

## 注意事项

- eval_report 的编码值也是 LLM 提取的，可能有错。以证据文字为准，编码值仅供参考。
- 三个证据源矛盾时，必须读 PDF 原文确认。
- Agent 每次处理一篇论文的所有分歧，不要拆成多个 Agent。
- 并发控制：可同时启动多个 Agent 处理不同论文。
- **边界案例标记**: 当判定处于边界（如 PANAS 前后测、专家参与数据准备vs评估），输出 `correct: "confirm"` 而非 `true/false`，让用户人工决定。
- **G-Eval 归类**: G-Eval 是 LLM-as-judge，归入 Eval_LLM_Judge=YES，同时 Eval_Automatic=NO。两者互斥。
