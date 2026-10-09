# Codebook 网页需求确认单

- 日期：2026-10-08（v5，网站已建成）
- 状态：**已实现**（网站位于 `web/`；**数据源权威说明见 `docs/DATA_SOURCES.md`**）
- 用户决策：① 数据源按分组取（见下）；② 页面语言 **英文**；③ 网站为**匿名版**（不含作者/机构/仓库链接/BibTeX）
- 目标：一个静态网站，按 **7 个分组**展示论文的 **40 个 coding fields**，风格仿照参考站点；同时把 reviewer 要的 codebook + coded corpus 变成可浏览的交互内容。
- 依据文件（最终位置，**源数据均为归档、禁止修改**）：
  - `docs/09_appendices.tex`（老师提供，**权威 codebook**：7 组 / 40 字段）
  - `compare/claim_level_FINAL_analysis_ready.csv`（老师提供，**第 7 组数据源**，72 行 / 52 篇）
  - `compare/final-table.csv`（G1–G6 已裁定编码）
  - `table/theory_eval_refined_coding_refined.csv`（G5 理论 3 字段，与论文一致）
  - `docs/codebook.csv`（字段定义草稿，供参考）
  - `docs/drafts/site_draft.html`（早期可视化草稿，仅留档）

---

## 0. 结论先行

**可以做，7 组数据现在齐全**。相比上一版确认稿，两个原先的阻塞项已解决：

| 上版阻塞项 | 现状 |
|---|---|
| Q1「仿照哪个网站」未知 | **已明确**：UKP *Responsible Evaluation of AI for Mental Health*（https://ukplab.github.io/nlp-mh-evals/）。本单一句话描述见 §2。 |
| Q3「Claim–Evidence 组无逐篇数据」 | **已解决**：`claim_level_FINAL_analysis_ready.csv` 提供 72 个 claim–evidence 条目（52 篇），含对齐裁决。见 §1.3 与 §1.5。 |

你已拍板三项：**数据以 `compare/final-table.csv` 为准**、**英文**、**匿名版**。
但由此暴露一处必须先解决的数据一致性冲突（见 §6.1）：`final-table.csv` 的两个理论列是**旧值**，若照抄会与论文附录自相矛盾。

---

## 1. 已确认事实（源文件核对结果）

### 1.1 权威结构 = 7 组 / 40 字段（以 `09_appendices.tex` 的 Coding Scheme 为准）

字段数核算 **5+5+8+3+7+10+2 = 40**，与正文一致。分组命名采用你给的英文名：

| # | 分组 | 字段数 |
|---|---|---|
| G1 | System & Simulation | 5 |
| G2 | Evaluation Methods | 5 |
| G3 | Evaluation Dimensions | 8 |
| G4 | Interaction & Behavior | 3 |
| G5 | Theory & Reliability | 7 |
| G6 | Additional Characteristics | 10 |
| G7 | Claim–Evidence Alignment | 2 |

### 1.2 七组字段 ↔ 数据文件映射（**本次新增，最关键**）

`✅`=存在且数字与论文附录一致；`⚠`=命名/来源需处理；`❌`=该文件没有该列。

| 分组 | 字段 | `final-table.csv` | `theory csv` | `claim csv` |
|---|---|---|---|---|
| **G1** | Focus_Type | ✅ | | |
| | Simulation_Target | ✅ | | |
| | Persona_Model_Depth | ✅ | | |
| | Uses_Dynamic_State | ✅ | | |
| | Temporal_Modeling_Details (free text) | ✅ | | |
| **G2** | Eval_Human_Experts | ✅ | | |
| | Eval_Lay_Users | ✅ | | |
| | Eval_User_Study | ✅ | | |
| | Eval_LLM_Judge | ✅ | | |
| | Eval_Automatic | ✅ | | |
| **G3** | Safety | ✅ | | |
| | Realism | ✅ | | |
| | Consistency | ✅ | | |
| | Fidelity | ✅ | | |
| | Human Learning / Outcomes | ✅ | | |
| | Utility | ✅ | | |
| | Emotional Plausibility | ✅ | | |
| | Raw Eval Metrics (free text) | ✅ | | |
| **G4** | Interaction_Level | ✅ | | |
| | Behavior_Eval_Depth | ✅ | | |
| | Intervention_Sensitivity | ⚠ 拼写为 `Interention_Sensitivity` | | |
| **G5** | Theory_Operationalized | ❌（值是旧的 35/10/5） | ✅ | |
| | Theory_Grounding | ❌（值是旧的 36/Weak 15） | ✅ | |
| | Theory_Eval_Type | ❌ | ✅ | |
| | Prompt_Disclosure | ✅ | | |
| | Clinical_Theory (free text) | ✅ | | |
| | Reliability_Reported | ✅ | | |
| | Agreement Method (free text) | ✅ | | |
| **G6** | Has_Rubric | ✅ | | |
| | LLM_Judge_Validated | ✅ | | |
| | Uses_Standard_Metrics | ✅ | | |
| | Metric_Interpretable | ✅ | | |
| | Comparable_To_Prior_Work | ✅ | | |
| | Has_Longitudinal_Eval | ✅ | | |
| | Has_Robustness_Testing | ✅ | | |
| | Has_Failure_Analysis | ✅ | | |
| | Sim_Behavior_Realistic | ✅ | | |
| | Dataset_Available | ✅ | | |
| **G7** | Claim (C1/C2) | ❌ | | ✅ |
| | Claim_Evidence_Alignment | ❌ | | ✅ |

### 1.3 第 7 组数据实况（`claim_level_FINAL_analysis_ready.csv`）

- **72 行 = 52 篇 × claim slot**：32 篇只有 C1，20 篇有 C1+C2。
- 一行 = 一个 (claim, evidence) 配对，行内 1:1；每行都带 claim 原文+页码+章节、evidence 原文+页码+章节+细定位。
- 对齐分类（**展示用的 4 个类别**，附录定义为 Aligned / Partial / Exceeds / Unclear）：

| 取值 | 初判(Provisional) | 复核(Codex) | 最终(Final) |
|---|---|---|---|
| ALIGNED | 41 | 41 | **41** |
| PARTIAL | 21 | 19 | **19** |
| EXCEEDS | 10 | 12 | **12** |

  - 一致性：AGREE 67 / DISAGREE 5；最终对齐取复核结果（`Final_Alignment ≡ Codex_Alignment`）。
  - 决策：RETAIN_VERIFIED 60 / ADOPT_CODEX_WORDING 7 / ADOPT_CODEX_DISAGREEMENT 5；人工复核标记 32 行。
  - **17 篇论文的 C1 与 C2 对齐类别不同**（论文内部不一致，是很好的叙事点）。
- 附录 `tab:claim-evidence-examples` 只给了 3 个例子并声明"完整记录随 released coding materials 发布"——本 CSV 就是那份材料，正好补上。

### 1.4 数字自洽性核对（重要，决定数据源）

- 评估者：Human 34 / LLM 30 / Auto 35 / 三者 15 → 与附录 `tab:evaluator-types` **一致**。
- 维度：Utility 44 / Fidelity 33 / Realism 29 / Emotional Plausibility 28 / Consistency 20 / Safety 14 / Human Learning 10 → 与附录 `tab:eval-dimensions` **一致**。
- 交互：Extended Dialogue 31 / Uses_Dynamic_State Yes 13 / Has_Longitudinal_Eval Yes 3 → 与正文 §4.4 **一致**。
- 信度：Reliability_Reported = Yes 16 → 与正文 §4.1 **一致**。
- ⚠ **理论组不一致（已解决）**：附录 `tab:theory-stats` 为 Grounding `40/10/2`、Op `30/16/6`，与 `theory csv` 完全吻合，而 `final-table.csv` 是旧值（Grounding 36/Weak 15、Op 35/10/5/2 空）。
  → **最终处理（方案 C，构建时覆盖）**：网站 G5 理论 3 字段取 `table/theory_eval_refined_coding_refined.csv`，其余取 `compare/final-table.csv`；**不改动任何源文件**。详见 `docs/DATA_SOURCES.md` §1、§5。

### 1.5 需要清理的列

- `Interention_Sensitivity`（缺 v）→ 页面与脚本统一改 `Intervention_Sensitivity`。
- `Coding Options` → 与 `Reliability_Reported` 重复，且不在 40 字段内 → **丢弃**。
- `Unnamed: 45`（空列）→ 丢弃。
- 元数据列 `Paper_ID / Citation_Key / Bibtex / Title / Year / Venue / Domain` 不计入 40 字段，但页面要用（论文卡片头部）。

---

## 2. 参考站点风格（UKP nlp-mh-evals 拆解）

单页静态站（React SPA），结构简单、信息密度低：

1. **Hero**：标题 + 一句副标题 + 作者 + arXiv + BibTeX 框；`Analysis of 135 ACL papers (2020–2025)`。
2. **叙事段**：The Evaluation Crisis / 分类叙事文字。
3. **交互模块** *The Metric Bridge*：点一个 NLP 指标 → 显示对应 clinical anchor + 解释（4 个手写例子）。
4. **Literature Survey 表**：可搜索、分页；列 `Paper | Metrics 徽章 | Human ✅/❌ | Expert ✅/❌ | Guidelines`；**点行展开**显示 Limitations。每篇只露 6 个字段。

**借鉴点**：Hero + 分组叙事 + 可搜索的语料表 + 行展开详情 + 克制的配色（teal 系）。
**我们的差异/优势**：40 字段（远多于他们的 6 个）；每个编码可回溯到论文原文引文+页码；自报编码信度（κ）；第 7 组 claim–evidence 对齐是独有内容。

---

## 3. 网站信息架构（建议）

```
Header  : 论文标题 + 副标题 + badges（52 papers × 40 fields · Evidence-linked coding · κ 0.61）
Nav     : 7 个分组锚点 + Overview + Corpus Explorer + Codebook + Download

① Overview        : 4~5 张"落差"统计卡（如 45 有 rubric → 仅 16 报信度；Utility 44 → Human Learning 10）
② G1…G6 六节       : 每组一节 = 组说明 + 字段表（名称/类型/取值/定义）+ 该组关键分布小图
③ G7 Claim–Evidence: 见 §4.4（对齐分布 + 可展开的 claim↔evidence 卡片）
④ Corpus Explorer : 52×40 全矩阵；搜索/按字段筛选；点单元格 → 证据弹层；导出 CSV
⑤ Codebook        : 40 字段定义卡（定义 + 取值 + 判断规则 + 正反例）
⑥ Download/Footer : codebook.csv · coded corpus CSV · 我们的 κ 统计
```

---

## 4. 可视化方案（按组）

- **① Overview 统计卡**：强调"落差"——`45 有 rubric → 16 报信度`、`30 用 LLM judge → 24 验证`、`44 评 utility → 10 评 human learning`、`52 → 31 长对话 → 13 动态状态 → 3 纵向`。
- **G2 Evaluation Methods**：UpSet / 组合条形（Human 34 · LLM 30 · Auto 35 · 三者 15）。
- **G3 Evaluation Dimensions**：7 维度横向条形（Utility 44 → Human Learning 10，突出"测表面质量、不测疗效"）。
- **G4 Interaction & Behavior**：漏斗（52→31→13→3）+ 交互层级 × 行为深度热力。
- **G5 Theory & Reliability**：理论梯度堆叠条（Grounding 40/10/2，Op 30/16/6）+ 提示词披露 40/9/3。
- **G6 Additional**：10 个 Yes/No 字段的 `Yes 计数` 条形。
- **G7 Claim–Evidence**：
  1. 对齐分布条/堆叠（41/19/12，n=72）；
  2. **可展开卡片墙**：claim 原文(章节+页) → evidence 原文(章节+页+表/图) + 对齐色标；C1/C2 折叠；
  3. 论文级组合（17 篇 C1≠C2）。
- **Corpus Explorer**：52 行 × 40 列矩阵，Yes/No 用实心/空心色块；点格子 → 弹窗显示该字段的 `eval_reports/<pid>.md` 原文证据（标注"证据来自自动抽取，可能与最终裁定值不同"）。

---

## 5. 数据管线与目录/部署（文字方案）

### 5.1 数据管线

```
compare/final-table.csv ─┐
table/theory_eval_...csv ─┼─► web/build/build_data.py ─► web/data/papers.json（52×40；理论组取值口径见 §6.1）
claim_level_FINAL...csv ──┤                             ─► web/data/claims.json（72 条 claim–evidence）
docs/codebook.csv / tex ──┘                             ─► web/data/codebook.json（7 组×40 字段定义）
```

- 原则：**不手工把数据写进 HTML**；所有数字由脚本一键重算，保证与论文一致。
- 归一化：UTF-8 BOM、拼写（Interention→Intervention）、丢弃 `Coding Options`/`Unnamed`。**理论组字段最终取值待 §6.1 决定**（默认按你的指示取 `final-table.csv`）。

### 5.2 目录结构（新建 `web/`）

```
web/
├── index.html                # 单页（或按节拆分）
├── assets/ styles.css, app.js
├── data/ papers.json, claims.json, codebook.json   # 由脚本生成
├── build/build_data.py       # CSV → JSON
└── README.md
.github/workflows/pages.yml   # 构建 + 部署到 GitHub Pages
```

### 5.3 GitHub Pages 方案（文字）

- 触发：push 到 `main`（或手动 dispatch）。
- 步骤：checkout → 安装 python → `python web/build/build_data.py` 生成 JSON → 上传 `web/` 目录为 Pages artifact → `actions/deploy-pages` 发布。
- 仓库已有 remote `github:HandyWote/LLM-Evaluation`，Pages 源设为 **GitHub Actions** 即可。
- 形态：纯静态、无后端、无 CDN 依赖，双击 `web/index.html` 也能本地打开。

---

## 6. 决策记录与遗留问题

### 6.1 ★ 数据一致性裁定（已用最终版论文定案，无需再纠结）

**裁定依据**：最终版论文 `Rethiniking_Evaluation___ARR_October_2026.pdf`（ARR Oct 2026，29 页）。逐项把论文正文/附录的实际数字与三个数据文件比对，结论：

> **三个文件合起来可 100% 复现论文；唯一真正的错误数据是 `final-table.csv` 的两个理论列。**

**复现对照表**（论文实际值 ← 匹配的文件）：

| 论文中的数字 | 论文值 | 匹配的文件 |
|---|---|---|
| 评估者 Human / LLM / Auto / 三者 | 34 / 30 / 35 / 15 | `final-table.csv` ✅ |
| 维度 Utility/Fidelity/Realism/Emo/Cons/Safety | 44 / 33 / 29 / 28 / 20 / 14 | `final-table.csv` ✅ |
| ≥1 维度 / ≥3 维度 | 50 / **40**（6 维口径） | `final-table.csv`（6 维）✅ |
| 长对话 / 动态状态 / 纵向 | 31 / 13 / 3 | `final-table.csv` ✅ |
| 长对话内行为深度 Static/Pattern/Dynamic | 16 / 7 / 7 | `final-table.csv` ✅ |
| LLM judge 验证（∩ 使用 LLM judge） | **23** | `final-table.csv`（交集=23）✅ |
| 用 rubric / 其中报信度 | 45 / **13** | `final-table.csv`（交集=13）✅ |
| 理论 Grounding | **40 / 10 / 2** | **`theory csv` ✅**（`final-table.csv`=36/15 ✗）|
| 理论 Operationalization | **30 / 16 / 6** | **`theory csv` ✅**（`final-table.csv`=35/10/5 ✗）|
| 理论评估类型 scale/编码系统/rubric/benchmark | 9 / 7 / 35 / 26 | **`theory csv`(Theory_Eval_Type) ✅** |
| 编码信度 平均 raw / Cohen κ | 82.5% / 0.61 | 论文 §Coding Reliability（无对应数据列）|
| Claim–Evidence C1（n=52） | 41 / 7 / 4 | `claim csv` ✅ |
| Claim–Evidence C2（n=20） | 12 / 8 / 0 aligned | `claim csv` ✅ |

**结论**：`final-table.csv` **除理论组 2 列（+缺 `Theory_Eval_Type`）外，其余全部与最终论文一致**，可作主数据源。必须处理的只有这 3 处：`Theory_Grounding`→40/10/2、`Theory_Operationalized`→30/16/6、`Theory_Eval_Type` 从 `theory csv` 追加。

**处理方式（最终采用 (C)）**：
- **(C) ✅ 已采用**：构建时覆盖 —— `compare/final-table.csv`、`table/theory_eval_refined_coding_refined.csv`、`compare/claim_level_FINAL_analysis_ready.csv`、`docs/09_appendices.tex` **均保持原样（归档，禁止修改）**；仅 G5 理论 3 字段在 `web/build/build_data.py` 里取自 theory csv。
- **(B) 未采用**：把订正写回 `final-table.csv`（会改掉归档文件，不做）。

> 说明：「(A) 照抄 final-table 旧值」会让网站与最终论文自相矛盾，已排除。**数据源权威说明见 `docs/DATA_SOURCES.md`。**

### 6.2 已拍板（无需再问）
- **Q1 数据源**：以 `compare/final-table.csv` 为准（理论组一致性见 §6.1）。
- **Q2 页面语言**：**英文**（全站英文，与论文一致）。
- **Q3 网站定位**：**匿名版**——不含作者、机构、GitHub 仓库链接、BibTeX；页脚只写数据来源与版本。

### 6.3 非阻塞（已采用默认值，如要改请说）
- Q4 逐格证据弹层：**要**（标注「证据来自自动抽取，可能与最终裁定值不同」）。
- Q5 第 7 组：**完整 72 条卡片墙**，按对齐类别排序 + 搜索。
- Q6 提供 **codebook.csv / coded corpus 下载**：**要**。
- Q7 Corpus Explorer：**矩阵总览 + 「选一篇看全部编码」两者都要**，矩阵为主。
- Q8 `docs/drafts/site_draft.html` 的 5 张图：**保留形态，数字全部由脚本重算**。

---

## 7. 建议里程碑

| 阶段 | 产出 | 依赖 |
|---|---|---|
| P0 | 本确认单拍板（§6） | 用户 |
| P1 | `web/build/build_data.py` → `papers.json / claims.json / codebook.json` | P0 |
| P2 | `web/index.html`：Header + 7 组导航 + codebook 字段表 | P1 |
| P3 | Overview 统计卡 + G2/G3/G4/G5/G6 分布图 | P2 |
| P4 | G7 claim–evidence 卡片墙 + Corpus Explorer（含证据弹层） | P3 |
| P5 | 下载入口 + `.github/workflows/pages.yml` 部署 | P4 |

**验收（草案）**：7 组 40 字段的名称/类型/取值/定义与 `09_appendices.tex` 完全一致；理论组数字与论文附录一致（口径以 §6.1 的最终决定为准）；G7 覆盖 72 条；所有数字由 P1 脚本可复现；**全站英文**；移动端可用。

---

## 附：已知风险

- 理论组数据源不一致（§1.4）是本需求最容易被忽略的坑，务必先确认。
- claim CSV 的 `Claim_Section` / `Evidence_Section` 命名未标准化，展示前需归一化。
- `eval_reports/` 有 6 篇不在 52 篇语料内，做证据 join 时必须按 Citation_Key 过滤。
- `docs/drafts/site_draft.html` 旧图数字与最终数据有出入，一律重算，不复用硬编码。
