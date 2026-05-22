# 目录重排设计方案

日期：2026-05-22

## 背景

当前项目结构混乱：`extract/` 是个"大杂烩"，包含提取、评估、笔记三个模块的代码和数据；`evluate/`、`compare/`、`note/` 是空目录。需要按职责重新组织。

## 目标

将项目按流程拆分为四个模块目录（extract、evaluate、note、compare），共用代码放 lib/，根目录用 uv 统一管理依赖和运行入口。

## 最终目录结构

```
LLM-Evaluate/
├── .env                     # 从 extract/ 移到根目录
├── .env.example             # 从 extract/ 移到根目录
├── pyproject.toml           # 根目录 uv init，定义所有依赖和 scripts
├── uv.lock
├── .python-version
├── .gitignore
├── CLAUDE.md
│
├── eval_reports/            # 研究笔记 markdown（根目录，evaluate 写入，note 读取）
│
├── extract/                 # 提取模块
│   ├── extract.py           # PDF 元数据提取
│   ├── pdf_index.py         # PDF 全文索引
│   ├── agent_loop.py        # 提取 agent 流程
│   ├── test_pdf_index.py
│   ├── test_agent_loop.py
│   ├── paper/               # 原始 PDF
│   └── paper_back/          # PDF 备份
│
├── evaluate/                # 评估模块
│   ├── evaluate.py          # 评估代码
│   ├── test_evaluate.py
│   └── eval_results.csv     # 评估结果数据
│
├── note/                    # 笔记模块
│   ├── notes.py             # 笔记生成代码
│   └── test_notes.py
│
├── compare/                 # 对比模块（未来用）
│
├── lib/                     # 共用模块
│   ├── __init__.py
│   ├── schemas.py           # 数据结构定义
│   ├── prompts.py           # 共用 prompt
│   └── tools.py             # 共用工具
│
├── docs/                    # 文档（不变）
│   ├── plans/
│   ├── specs/
│   ├── paper_metadata.csv
│   ├── citation_bibtex.csv
│   ├── citations.bib
│   ├── generate_bib.py
│   ├── theme_track.csv
│   └── 评估维度表.md
│
└── table/                   # 表生成（不变）
    ├── generate_tables.py
    └── ...
```

## uv scripts 配置

```toml
[project.scripts]
extract = "extract.extract:main"
evaluate = "evaluate.evaluate:main"
note = "note.notes:main"
```

运行方式：
```bash
uv run extract      # 原来是 cd extract && uv run extract.py
uv run evaluate     # 原来是 cd extract && uv run evaluate.py
uv run note         # 原来是 cd extract && uv run notes.py
```

## 路径引用修复

### Import 路径（相对于根目录）

| 原 import | 新 import |
|-----------|-----------|
| `from schemas import ...` | `from lib.schemas import ...` |
| `from pdf_index import ...` | `from extract.pdf_index import ...` |
| `from tools import ...` | `from lib.tools import ...` |
| `from prompts import ...` | `from lib.prompts import ...` |
| `from agent_loop import ...` | `from extract.agent_loop import ...` |

需要修改的文件：
- `lib/prompts.py`：`from schemas import` → `from lib.schemas import`
- `lib/tools.py`：`from pdf_index import` → `from extract.pdf_index import`
- `extract/agent_loop.py`：所有 from import 改为绝对路径
- `evaluate/evaluate.py`：所有 from import 改为绝对路径
- `note/notes.py`：无本地 import，无需修改
- `extract/extract.py`：无本地 import，无需修改

### 数据路径

| 文件 | 原路径 | 新路径 |
|------|--------|--------|
| evaluate.py | `Path(__file__).parent / "eval_reports"` | `Path(__file__).parent.parent / "eval_reports"` |
| evaluate.py | `Path(__file__).parent / "eval_results.csv"` | `Path(__file__).parent / "eval_results.csv"`（不变） |
| notes.py | `Path(__file__).parent / "eval_reports"` | `Path(__file__).parent.parent / "eval_reports"` |
| extract.py | `Path(__file__).parent / "paper"` | 不变（paper/ 仍在 extract/） |
| .env | `extract/.env` | 根目录 `.env`（`load_dotenv()` 从 cwd 向上搜索） |

## 文件移动清单

| 源路径 | 目标路径 |
|--------|----------|
| `extract/schemas.py` | `lib/schemas.py` |
| `extract/prompts.py` | `lib/prompts.py` |
| `extract/tools.py` | `lib/tools.py` |
| `extract/evaluate.py` | `evaluate/evaluate.py` |
| `extract/test_evaluate.py` | `evaluate/test_evaluate.py` |
| `extract/eval_results.csv` | `evaluate/eval_results.csv` |
| `extract/notes.py` | `note/notes.py` |
| `extract/test_notes.py` | `note/test_notes.py` |
| `extract/eval_reports/` | `eval_reports/`（根目录，不进 note/） |
| `extract/.env` | `.env`（根目录） |
| `extract/.env.example` | `.env.example`（根目录） |
| `extract/pyproject.toml` | 删除（用根目录的） |
| `extract/uv.lock` | 删除（用根目录的） |

## 清理清单

删除以下运行时目录：
- `extract/__pycache__/`
- `extract/.obsidian/`
- `extract/.pytest_cache/`
- `extract/.venv/`
- `extract/.DS_Store`

删除空目录：
- `evluate/`（typo，功能已被 `evaluate/` 替代）
- `extract/.env`（已移到根目录）
- `extract/.env.example`（已移到根目录）

## 根目录 pyproject.toml

```toml
[project]
name = "llm-evaluate"
version = "0.1.0"
description = "LLM mental health counseling evaluation research"
requires-python = ">=3.12"
dependencies = [
    "openai>=1.0.0",
    "pymupdf>=1.0.0",
    "python-dotenv>=1.0.0",
]

[project.scripts]
extract = "extract.extract:main"
evaluate = "evaluate.evaluate:main"
note = "note.notes:main"
```

## 风险与注意事项

1. **Import 路径**：uv scripts 从根目录运行，所有本地 import 必须用绝对路径（相对于项目根目录）
2. **eval_reports 路径**：evaluate.py 和 notes.py 都用 `Path(__file__).parent.parent / "eval_reports"` 引用根目录的 eval_reports/
3. **.env 路径**：从 extract/ 移到根目录，`load_dotenv()` 从 cwd 向上搜索，uv run 从根目录运行时能找到
4. **paper/ 路径**：extract.py 中 `Path(__file__).parent / "paper"` 不变，因为 paper/ 仍在 extract/
5. **测试**：移动后需要运行所有测试确认 import 正确
