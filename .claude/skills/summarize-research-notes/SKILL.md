---
name: summarize-research-notes
description: Summarize and cross-compare research notes from eval_reports. Use when the user asks to summarize research notes, do cross-paper comparison, find commonalities/differences, or says "总结研究笔记", "跨论文对比", "求同求异", "总结评估方法论问题". Triggers on eval_reports/*.md analysis requests.
---

# Summarize Research Notes

你正在综合多篇 eval_reports 的评估方法论批判。目标是找出跨论文的共性模式——哪些做得好、哪些系统性缺失——为后续研究建议提供依据。

## 工作流

### Step 1: 检测未总结的论文

运行检测脚本，找出尚未被总结的研究笔记：

```bash
cd extract && uv run ../.claude/skills/summarize-research-notes/scripts/find_unsummarized.py eval_reports
```

脚本输出 JSON：
```json
{"unsummarized": ["1", "6", "10"], "total_with_notes": 10, "already_summarized": 7}
```

**如果 `unsummarized` 为空**：告诉用户"所有研究笔记都已总结，没有新论文需要处理"，结束。

### Step 2: 读取未总结论文的研究笔记

读取 `eval_reports/` 下 `unsummarized` 列表中的每篇 `.md` 文件。重点关注 `## 研究笔记` section。

### Step 3: 逐篇提取优缺点

对每篇论文，从研究笔记中提取具体的优点和缺点。不预设维度，用论文自己的语言。

每篇通常 2-4 个优点、3-5 个缺点。提取实际存在的内容，不编造。

### Step 4: 跨论文聚类

按语义相似度把优点/缺点归类。每个聚类包含：
- 标签（短中文短语）
- 一句话描述
- 涉及的论文 ID 列表

### Step 5: 生成总结文档

文件名：`summary-{id1}-{id2}-...-{idN}.md`（ID 排序，`-` 连接）

输出到 `extract/eval_reports/summary-{ids}.md`，结构如下：

```markdown
# 研究笔记总结：Paper {id1}, {id2}, ..., {idN}

> 生成时间：{date}
> 论文列表：{id1} — {title1}，{id2} — {title2}，...

## 一、各论文要点

### Paper {id}: {title}
**优点：**
- ...
**缺点：**
- ...

## 二、跨论文模式

### 优点模式
#### {标签}（{M}/{N} 篇）
{解释}
- Paper {id}: {表现}

### 缺点模式
#### {标签}（{M}/{N} 篇）
{解释}
- Paper {id}: {表现}

## 三、量化矩阵
| Paper | 模式1 | 模式2 | ... |
|-------|:-----:|:-----:|:---:|

## 四、关键发现
{2-3 段洞察}
```

如果 summary 文件已存在，提示用户是否覆盖。

### Step 6: 打标记

运行标记脚本，在已总结论文的 `## 研究笔记` 下方插入反向链接：

```bash
cd extract && uv run ../.claude/skills/summarize-research-notes/scripts/mark_summarized.py \
  --papers {id1},{id2},... --summary summary-{ids}.md --dir eval_reports
```

### Step 7: 告知用户

告诉用户：
1. 总结文件的位置
2. Top 3 最常见优点（按论文数）
3. Top 3 最常见缺点（按论文数）
4. 哪篇论文表现突出（特别好或特别差）

## 写作风格

- 文字说人话，不要学术八股
- 表格做量化，打勾打叉清晰
- 缺点分析要尖锐但有建设性
- 引用具体论文用 Paper {id} 格式

## 注意事项

- 一篇论文可以同时出现在不同维度的优点和缺点里
- 只出现 1 次的优点/缺点单独列出，标注"仅见于 Paper {id}"，不强行归类
- 频次统计是辅助，不为凑数字合并不同类项
- 没有研究笔记的论文跳过，在开头注明
