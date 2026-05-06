# 研究笔记生成脚本设计

## 背景

现有的 agentic 提取管道（evaluate.py）从论文 PDF 中提取 43 个结构化字段，用于量化统计分析。但研究者需要阅读论文全文才能完成综合分析和写结论。本脚本通过 AI 生成研究笔记，追加到 eval_report 末尾，使课题组同学无需阅读原文即可理解论文内容及其评估方法论问题。

## 目标

生成自成体系的研究笔记，读笔记即可替代阅读全文。

## 脚本定位

- **文件：** `extract/notes.py`，独立脚本
- **不修改任何现有文件**
- **依赖：** 复用现有 pyproject.toml 依赖（pymupdf, openai, python-dotenv）

## CLI 接口

```bash
cd extract
uv run notes.py                    # 处理所有有 eval_report 的论文
uv run notes.py --paper 1          # 只处理论文 1
uv run notes.py --force            # 强制覆盖已有笔记
uv run notes.py --dir eval_reports # 指定 eval_reports 目录
```

与 evaluate.py 风格一致。

## 配置

`.env` 新增：

```
NOTES_MODEL=deepseek-chat    # 笔记专用模型，不设则回退到 OPENAI_MODEL
```

`.env.example` 同步更新。

## 幂等性

检测 eval_report 中是否已有 `## 研究笔记` 章节标题，有则跳过（`--force` 时覆盖）。

## 笔记输出结构

追加到 eval_report.md 末尾：

```markdown
## 研究笔记

### 概括

**研究目标：** ...

**方法概述：** ...（重点展开）

**主要结果：** ...

### 评价

（从元评测视角的批判性分析，2-4 段自然段落）
```

## Prompt 设计

### System prompt

角色：学术论文元评测研究助手。从评估方法与目标对齐度的研究视角出发撰写笔记。

### User message 组成

1. 评估维度表（`评估维度表.md` 内容）— 批判视角的参考框架
2. 已有的 eval_report 内容 — 43 字段提取结果，避免重复
3. PDF 全文（1M 上下文，不截取）— 完整信息源
4. 生成指令

### 关键指令约束

- 概括部分：大白话，不用学术黑话堆砌，让没读过原文的课题组同学也能看懂
- 评价部分：聚焦评估方法论问题（维度选取无理论依据、自说自话、cherry-picking 等），不批评论文本身
- 不重复 eval_report 已有的结构化数据，而是基于全文给出综合判断
- 用中文撰写

## 数据流

```
1. 加载 .env（复用 evaluate.py 的 load_dotenv 模式）
2. 找到 paper/{id}.pdf 和 eval_reports/{id}.md
3. 检查 eval_report 是否已有"研究笔记"章节 → 有则跳过
4. 用 pymupdf 提取 PDF 全文
5. 拼接 prompt：评估维度表 + eval_report 内容 + PDF 全文 + 生成指令
6. 调用 LLM（异步，MAX_CONCURRENCY=3）
7. 将返回的笔记追加到 eval_report.md 末尾
```

## 代码组织

- 单文件 `notes.py`，不拆模块
- 异步并发处理多篇论文（与 evaluate.py 一致）
- 进度日志：`INFO: Paper 1 - 生成笔记中...`, `INFO: Paper 1 - 已追加到 1.md`

## 不做的事情

- 不改 evaluate.py 或任何现有文件
- 不生成 CSV（笔记是给人读的文字，不是统计数据）
- 不做证据验证（笔记不引用原文 quote）

## 文件变更清单

| 文件 | 操作 |
|------|------|
| `extract/notes.py` | 新建 |
| `extract/.env.example` | 新增 NOTES_MODEL 字段 |
| `extract/.env` | 新增 NOTES_MODEL 字段 |
| `extract/eval_reports/*.md` | 末尾追加内容（运行后） |
