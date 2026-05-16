# verify-eval-extraction Skill 优化设计

**日期**: 2026-05-16
**状态**: 待实现

## 问题背景

2026-05-16 验证 5 篇论文（101, 102, 104, 106, 107）时暴露的核心问题：

1. **归一化假阳性**：PDF 换行导致 `"excellent\nperformance"` 无法匹配 `"excellent performance"`，明明在 PDF 中存在却被判 FABRICATED
2. **TEMPLATE → fix → FABRICATED 死循环**：修复 TEMPLATE 字段时，AI 写了总结性证据而非 PDF 逐字引用，结果被标为 FABRICATED
3. **无自动证据提取**：AI 手动搜 PDF 效率低且容易写成总结
4. **批量处理无优先级策略**：183 个字段平铺处理，效率低

## 方案：渐进增强（脚本 + Skill 双改）

---

## Part 1: 脚本改动（verify_extraction.py）

### 1.1 归一化更激进

**当前问题**：`_normalize_whitespace` 处理了连字符断行和引号归一化，但没有处理单词间的正常换行符。

**修改**：在归一化流程中，将所有换行符替换为空格（在连字符处理之后、空格折叠之前）：

```python
def _normalize_whitespace(s):
    # 现有逻辑：引号归一化、连字符断行处理
    s = re.sub(r'[‘’]', "'", s)  # curly single quotes
    s = re.sub(r'[“”]', '"', s)  # curly double quotes
    s = re.sub(r'-\s+', '', s)  # line-break hyphens
    s = re.sub(r'-', '', s)     # all remaining hyphens
    # 新增：换行符 → 空格
    s = re.sub(r'\n', ' ', s)
    # 现有逻辑：空格折叠 + strip + lower
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s
```

**预期效果**：消除因 PDF 换行导致的 FABRICATED 假阳性。

### 1.2 新增 `--extract-evidence` 模式

**功能**：对 TEMPLATE 和 FABRICATED 字段，自动从 PDF 提取候选 verbatim 原文片段。

**关键词提取逻辑**：
- **TEMPLATE 字段**：从 evidence 中提取关键词（去掉模板前缀如 "No evidence of..."），加上字段名
- **FABRICATED 字段**：从 evidence 中提取名词短语和关键术语，加上字段名
- **字段名映射**：预定义每个字段的搜索关键词列表（如 `eval_llm_judge` → ["GPT", "LLM", "judge", "human evaluation", "automatic"]）

**搜索逻辑**：
1. 用 `fitz` 提取 PDF 全文，按句子/段落分割
2. 对每个候选段落，计算与搜索关键词的匹配数
3. 按匹配数降序排序，返回 top-10 个候选
4. 每个候选包含：页码、原文文本（最多 300 字符）、相关度分数

**输出格式**：
```json
{
  "field": "eval_llm_judge",
  "value": "NO",
  "candidates": [
    {"page": 6, "text": "...", "relevance": 3},
    {"page": 7, "text": "...", "relevance": 2}
  ]
}
```

**使用方式**：
```bash
# 单篇论文
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py 102 --extract-evidence

# 多篇
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py 101 102 --extract-evidence
```

### 1.3 扩展 `--fix` 能力

**当前**：`--fix` 只自动修复 page_match 问题。

**扩展**：
1. **Page fix**（已有）：替换 `(p.X)` 为正确页码
2. **Template fix**（新增）：对 TEMPLATE 字段，调用 `--extract-evidence` 逻辑获取最佳候选，自动替换 markdown 中的 evidence 行
3. **标记**：替换后的 evidence 行末尾加 `[AUTO-FIXED]` 标记，提醒 AI 确认

**不自动修复 FABRICATED**：FABRICATED 可能是假阳性（归一化后应为 EXACT），也可能是真正编造，需要 AI 判断。脚本只输出候选，不自动替换。

---

## Part 2: Skill 改动（SKILL.md）

### 2.1 Step 4 前增加"逐字引用铁律"

在 Step 4（Fix）开头添加醒目警告：

```
> ⚠️ **逐字引用铁律**
> 证据必须是 PDF 原文逐字引用。绝对不能自己写总结、改写、缩写。
> 如果你写出来的文字不是 PDF 里原封不动抄出来的，就是错的。
>
> ✅ 正确：We recruited 7 mental health professionals with professional expertise.
> ❌ 错误：The paper uses human evaluation by mental health professionals.
> （第二种是总结，不是原文，会被判为 FABRICATED）
```

### 2.2 简化工作流

将当前 5 步简化为更清晰的优先级流程：

**Step 1**: 跑脚本
```bash
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py {ids}
```

**Step 2**: 看结果，按优先级分类
- TEMPLATE 字段（最优先）→ Step 3a
- FABRICATED 字段 → Step 3b
- PARAPHRASED 字段 → 跳过（可接受）
- EXACT 字段 → 跳过

**Step 3a**: 修复 TEMPLATE
```bash
# 用 --extract-evidence 获取候选
cd extract && uv run ../.claude/skills/verify-eval-extraction/scripts/verify_extraction.py {id} --extract-evidence
# 从候选中选择 verbatim 文本，替换 evidence
# 逐字引用！不要总结！
```

**Step 3b**: 处理 FABRICATED
1. 先检查是否假阳性（归一化问题）→ 重新跑脚本确认
2. 不是假阳性？→ 用 `--extract-evidence` 获取候选，选择 verbatim 文本替换
3. 值可能错了？→ Step 4

**Step 4**: 判断值验证
- 用已验证的证据 + 字段定义判断值是否正确
- 值错了？→ 改值 + 同步 CSV

**Step 5**: 重新跑脚本确认修复干净

### 2.3 添加证据修复模板

在 Skill 中添加正确 vs 错误的修复示例：

```
## 证据修复示例

### TEMPLATE → EXACT（正确做法）

原始 evidence：
> **Evidence** (N/A): No evidence of using LLM as judge for evaluation found in the paper.

PDF 原文搜索结果：
> p.6: To comprehensively evaluate the model's performance...we adopted a series of automatic evaluation metrics.
> p.7: Our evaluation team consisted of four senior psychology students and an experienced psychotherapist.

修复后 evidence（逐字引用）：
> **Evidence** (p.6-7): To comprehensively evaluate the model's performance...we adopted a series of automatic evaluation metrics. Our evaluation team consisted of four senior psychology students and an experienced psychotherapist.

### TEMPLATE → FABRICATED（错误做法）

修复后 evidence（总结，不是原文）：
> **Evidence** (p.6-7): The paper uses automatic metrics and human expert evaluation, with no LLM judge employed.
                                   ↑ 这是 AI 总结的，不是 PDF 原文，会被判为 FABRICATED
```

---

## Part 3: 实现计划

| 步骤 | 内容 | 预估时间 |
|------|------|----------|
| 1 | 脚本：归一化修复（`\n` → 空格） | 10 分钟 |
| 2 | 脚本：新增 `--extract-evidence` 逻辑 | 30 分钟 |
| 3 | 脚本：扩展 `--fix` 支持 TEMPLATE | 15 分钟 |
| 4 | Skill：添加铁律警告 + 修复模板 | 10 分钟 |
| 5 | Skill：简化工作流步骤 | 10 分钟 |
| 6 | 测试：用 Paper 102 验证改进效果 | 15 分钟 |

**总计**：约 90 分钟

---

## 预期效果

| 指标 | 当前 | 改进后 |
|------|------|--------|
| TEMPLATE 清除 | 手动，容易引入 FABRICATED | 自动提取候选，AI 选择 |
| FABRICATED 假阳性 | 常见（归一化问题） | 大幅减少 |
| 修复一个字段耗时 | 2-5 分钟（手动搜 PDF） | 30 秒（选候选） |
| AI 犯写总结的错误 | 高频 | 低频（有铁律警告 + 模板） |
