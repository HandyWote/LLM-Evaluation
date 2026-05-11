# summarize-research-notes Skill 改进设计

> 2026-05-11

## 背景

用户的工作流：选论文 → evaluate.py 打标 → verify skill 验证 → notes.py 生成研究笔记 → 人工阅读笔记 → **summarize skill 总结** → 产出可追溯的总结文档 + 统计。

当前 skill 的问题：
1. 没有批次管理——总是读取全部 eval_reports，无法只总结最新一批
2. 没有幂等性——重复运行会产生重复内容
3. 输出没有标注具体是哪几篇论文的总结
4. 检测和标记逻辑应该由脚本实现，而非纯靠 Claude 解析

## 设计

### 核心机制：反向链接标记

每篇论文的研究笔记被总结后，在 `## 研究笔记` 标记下方插入一行：

```markdown
> 已总结于 summary-1-6-10.md
```

Skill 下次运行时，通过检测此标记跳过已总结的论文。

### 工作流（三步）

```
Step 1: scripts/find_unsummarized.py
        扫描 eval_reports/ → 找出未总结的论文 ID → 输出 JSON

Step 2: Claude 执行总结
        读取未总结论文 → 提取优缺点 → 聚类 → 写 summary-{ids}.md

Step 3: scripts/mark_summarized.py
        在已总结论文的笔记中插入反向链接标记
```

### 脚本 1：find_unsummarized.py

- 位置：`.claude/skills/summarize-research-notes/scripts/find_unsummarized.py`
- 输入：`eval_reports/` 目录路径（命令行参数）
- 输出：JSON 到 stdout
  ```json
  {
    "unsummarized": ["1", "6", "10"],
    "total_with_notes": 10,
    "already_summarized": 7
  }
  ```
- 逻辑：
  1. 扫描目录下所有 `.md` 文件
  2. 检查是否有 `## 研究笔记` section
  3. 检查该 section 下是否有匹配 `> 已总结于 summary-*.md` 的行
  4. 无标记的加入 unsummarized 列表

### 脚本 2：mark_summarized.py

- 位置：`.claude/skills/summarize-research-notes/scripts/mark_summarized.py`
- 输入：`--papers 1,6,10 --summary summary-1-6-10.md --dir eval_reports/`
- 输出：修改对应 `.md` 文件
- 逻辑：
  1. 对每篇论文，在 `## 研究笔记` 行之后插入 `> 已总结于 {summary_filename}`
  2. 如果已有标记 → 跳过（幂等）
  3. 输出修改的文件列表

### 输出文档

文件名：`summary-{id1}-{id2}-...-{idN}.md`（ID 排序，用 `-` 连接）

结构：

```markdown
# 研究笔记总结：Paper {id1}, {id2}, ..., {idN}

> 生成时间：{date}
> 论文列表：{id1} — {title1}，{id2} — {title2}，...

## 一、各论文要点

### Paper {id}: {title}
**优点：** ...（2-4 条）
**缺点：** ...（3-5 条）

（每篇独立成节，方便追溯）

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

### Skill SKILL.md 更新

更新工作流步骤：
1. 运行 `find_unsummarized.py` 获取未总结论文列表
2. 列表为空 → 提示用户，结束
3. 读取论文，提取优缺点
4. 聚类相似项
5. 写 `summary-{ids}.md`
6. 运行 `mark_summarized.py` 打标记
7. 告知用户结果

### 边界情况

- 所有论文已总结 → 脚本返回空列表，skill 提示用户
- summary 文件已存在 → skill 提示用户是否覆盖
- 用户想重新总结 → 删除笔记中的标记行后重跑
- eval_reports 中无研究笔记 → 脚本跳过，不计入总数

### 文件清单

```
.claude/skills/summarize-research-notes/
├── SKILL.md                          (更新)
└── scripts/
    ├── find_unsummarized.py          (新建)
    └── mark_summarized.py            (新建)
```
