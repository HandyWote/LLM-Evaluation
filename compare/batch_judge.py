"""Batch judge remaining disagreements using LLM."""

import csv
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "deepseek-v4-flash")

INPUT = "compare/disagreement_cn.csv"

SYSTEM = """你是学术评估专家。根据以下判定原则，对分歧做出最终判定。

判定原则:
- Eval_Automatic: 人打分后算指标=NO，算法公式自动算=YES
- Eval_Lay_Users: 用户生成数据=NO，用户参与评估=YES
- Eval_Human_Experts: 有领域专家参与评估=YES
- Eval_LLM_Judge: LLM做标注/分析/评估=YES
- LLM_Judge_Validated: 有Cohen's Kappa/ICC等标准化验证=YES，仅百分比一致=NO
- Fidelity: 评估了角色保真度/目标对齐=YES，只评估准确性等其他指标=NO
- Behavior_Eval_Depth: 评估分析轮次间变化=DYNAMIC，统计频率分布=PATTERN-LEVEL，独立评分或聚合分数=STATIC
- Uses_Dynamic_State: 有前后测或持续状态追踪=YES
- Prompt_Disclosure: 完整披露所有prompt=FULL，部分=PARTIAL，无=NO
- Interaction_Level: 1轮=SINGLE-TURN，2-5轮=SHORT MULTI-TURN，6+轮=EXTENDED DIALOGUE，跨会话=LONGITUDINAL
- Safety: 评估测试了有害输出=YES，仅有伦理声明=NO
- Utility: 评估了有用性=YES，仅陈述系统有用=NO
- Has_Robustness_Testing: 不同模型/条件测试或消融实验=YES
- Has_Failure_Analysis: 分析了失败案例或局限性=YES
- Has_Rubric: 有明确评分标准，Likert标签算=YES
- Coding Options/Reliability_Reported: 需标准化系数(Kappa/ICC)，仅百分比一致=NO
- Persona_Model_Depth: 基本人口统计=SURFACE，行为状态=BEHAVIORAL STATE，认知模型=COGNITIVE，动态特质=DYNAMIC TRAITS，专家原则=EXPERT PRINCIPLES
- Theory_Grounding: 明确用公认理论定义测量=STRONG，提及未操作化=WEAK，无=NONE
- Theory_Operationalized: 标准明确源于理论=STRONG，部分操作化=PARTIAL，仅提及=MENTIONED
- Comparable_To_Prior_Work: 有基准框架可对比=YES
- Dataset_Available: 实际可用=YES，"将发布"或"按需"=NO
- Emotional Plausibility: 评估了情绪反应真实性=YES
- Realism: 评估了输出是否像人类=YES
- Sim_Behavior_Realistic: 评估了模拟行为真实性=YES
- Has_Longitudinal_Eval: 有纵向跨会话评估=YES
- Human Learning/Outcomes: 评估了人类进步改变=YES
- Uses_Standard_Metrics: 使用了公认评估指标=YES

cxt补充证据如果与该字段相关且支持cxt值，倾向于cxt。否则以原始证据为准。

请对以下分歧做出判定，输出JSON: {"results": [{"row": 行号, "judgment": "值", "reason": "简短理由"}, ...]}
"""


def main():
    with open(INPUT, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys())

    to_process = [(i, r) for i, r in enumerate(rows) if not r.get("修正判定", "").strip() and i >= 10]
    print(f"待处理: {len(to_process)} 行")

    for batch_start in range(0, len(to_process), 15):
        batch = to_process[batch_start : batch_start + 15]
        prompts = []
        for i, row in batch:
            p = f"[Row {i}] Paper {row['Paper_ID']} — {row['字段中文']}\n"
            p += f"定义: {row['定义']}\n"
            p += f"cxt={row['cxt值']} vs hyh={row['hyh值']}\n"
            p += f"原始证据: {row['原始证据'][:400]}\n"
            ev_cxt = row.get("cxt补充证据", "").strip()
            if ev_cxt:
                p += f"cxt补充: {ev_cxt[:400]}\n"
            prompts.append(p)

        user_msg = "\n---\n".join(prompts)

        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            result = json.loads(resp.choices[0].message.content)
            items = result.get("results", result.get("judgments", []))

            for item in items:
                row_idx = item.get("row")
                if row_idx is not None and 0 <= row_idx < len(rows):
                    rows[row_idx]["修正判定"] = item.get("judgment", "")
                    rows[row_idx]["理由"] = item.get("reason", "")

            print(
                f"Batch {batch_start // 15 + 1}: {len(batch)} rows -> {len(items)} results"
            )

        except Exception as e:
            print(f"Batch {batch_start // 15 + 1} error: {e}")

        # Save every batch
        with open(INPUT, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    done = sum(1 for r in rows if r.get("修正判定", "").strip())
    print(f"\n完成! 已判定 {done}/{len(rows)}")


if __name__ == "__main__":
    main()
