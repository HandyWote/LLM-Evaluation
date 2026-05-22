# 目录重排实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将项目从 extract/ 单目录结构拆分为 extract/、evaluate/、note/、compare/ 四模块结构，根目录用 uv 统一管理。

**Architecture:** 按流程拆分：extract/ 只保留提取相关代码，evaluate/ 放评估代码，note/ 放笔记代码，lib/ 放共用模块。根目录 pyproject.toml 定义 uv scripts 作为统一入口。

**Tech Stack:** Python 3.12, uv, pymupdf, openai, python-dotenv

---

### Task 1: 创建根目录 pyproject.toml

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: 创建根目录 pyproject.toml**

```toml
[project]
name = "llm-evaluate"
version = "0.1.0"
description = "LLM mental health counseling evaluation research"
requires-python = ">=3.12"
dependencies = [
    "pymupdf",
    "openai",
    "python-dotenv",
    "openpyxl",
]

[dependency-groups]
dev = ["pytest>=8.0", "pytest-asyncio>=0.24"]

[project.scripts]
extract = "extract.extract:main"
evaluate = "evaluate.evaluate:main"
note = "note.notes:main"
```

- [ ] **Step 2: 运行 uv sync 安装依赖**

Run: `uv sync`
Expected: 依赖安装成功，生成 uv.lock

- [ ] **Step 3: 提交**

```bash
git add pyproject.toml uv.lock .python-version
git commit -m "feat: add root pyproject.toml with uv scripts"
```

---

### Task 2: 创建 lib/ 目录，移动共用模块

**Files:**
- Create: `lib/__init__.py`
- Move: `extract/schemas.py` → `lib/schemas.py`
- Move: `extract/prompts.py` → `lib/prompts.py`
- Move: `extract/tools.py` → `lib/tools.py`

- [ ] **Step 1: 创建 lib/ 目录和 __init__.py**

```bash
mkdir -p lib
touch lib/__init__.py
```

- [ ] **Step 2: 移动共用模块**

```bash
git mv extract/schemas.py lib/schemas.py
git mv extract/prompts.py lib/prompts.py
git mv extract/tools.py lib/tools.py
```

- [ ] **Step 3: 修复 lib/prompts.py 的 import**

文件 `lib/prompts.py` 第 4 行：
```python
# 原
from schemas import PHASES, FIELD_DEFINITIONS, METADATA_FIELDS, BOOL_FIELDS
# 改为
from lib.schemas import PHASES, FIELD_DEFINITIONS, METADATA_FIELDS, BOOL_FIELDS
```

- [ ] **Step 4: 修复 lib/tools.py 的 import**

文件 `lib/tools.py` 第 4 行：
```python
# 原
from pdf_index import PDFIndex, SearchResult
# 改为
from extract.pdf_index import PDFIndex, SearchResult
```

- [ ] **Step 5: 提交**

```bash
git add lib/ extract/prompts.py extract/tools.py extract/schemas.py
git commit -m "refactor: move shared modules to lib/"
```

---

### Task 3: 创建 evaluate/ 目录，移动评估文件

**Files:**
- Create: `evaluate/` directory
- Move: `extract/evaluate.py` → `evaluate/evaluate.py`
- Move: `extract/test_evaluate.py` → `evaluate/test_evaluate.py`
- Move: `extract/eval_results.csv` → `evaluate/eval_results.csv`

- [ ] **Step 1: 创建目录并移动文件**

```bash
mkdir -p evaluate
git mv extract/evaluate.py evaluate/evaluate.py
git mv extract/test_evaluate.py evaluate/test_evaluate.py
git mv extract/eval_results.csv evaluate/eval_results.csv
```

- [ ] **Step 2: 修复 evaluate/evaluate.py 的 import**

文件 `evaluate/evaluate.py`，修改以下行：

```python
# 第 28-32 行，原：
from schemas import (
    PHASES, FIELD_DEFINITIONS, METADATA_FIELDS, BOOL_FIELDS, JUDGMENT_FIELDS
)
# 改为：
from lib.schemas import (
    PHASES, FIELD_DEFINITIONS, METADATA_FIELDS, BOOL_FIELDS, JUDGMENT_FIELDS
)

# 第 33 行，原：
from pdf_index import PDFIndex
# 改为：
from extract.pdf_index import PDFIndex

# 第 34 行，原：
from agent_loop import agent_loop
# 改为：
from extract.agent_loop import agent_loop
```

- [ ] **Step 3: 修复 evaluate/evaluate.py 的数据路径**

文件 `evaluate/evaluate.py`：

```python
# 第 41 行，原：
REPORTS_DIR = Path(__file__).parent / "eval_reports"
# 改为：
REPORTS_DIR = Path(__file__).parent.parent / "eval_reports"
```

注意：`OUTPUT_CSV = Path(__file__).parent / "eval_results.csv"` 不需要改，因为 eval_results.csv 现在就在 evaluate/ 目录下。

- [ ] **Step 4: 提交**

```bash
git add evaluate/
git commit -m "refactor: move evaluate module to evaluate/"
```

---

### Task 4: 创建 note/ 目录，移动笔记文件

**Files:**
- Create: `note/` directory
- Move: `extract/notes.py` → `note/notes.py`
- Move: `extract/test_notes.py` → `note/test_notes.py`

- [ ] **Step 1: 创建目录并移动文件**

```bash
mkdir -p note
git mv extract/notes.py note/notes.py
git mv extract/test_notes.py note/test_notes.py
```

- [ ] **Step 2: 修复 note/notes.py 的数据路径**

文件 `note/notes.py`：

```python
# 第 28 行，原：
REPORTS_DIR = Path(__file__).parent / "eval_reports"
# 改为：
REPORTS_DIR = Path(__file__).parent.parent / "eval_reports"

# 第 29 行，原：
PAPER_DIR = Path(__file__).parent / "paper"
# 改为：
PAPER_DIR = Path(__file__).parent.parent / "extract" / "paper"
```

- [ ] **Step 3: 提交**

```bash
git add note/
git commit -m "refactor: move notes module to note/"
```

---

### Task 5: 移动 eval_reports/ 和 .env 到根目录

**Files:**
- Move: `extract/eval_reports/` → `eval_reports/`（根目录）
- Move: `extract/.env` → `.env`（根目录）
- Move: `extract/.env.example` → `.env.example`（根目录）

- [ ] **Step 1: 移动 eval_reports/**

```bash
git mv extract/eval_reports eval_reports
```

- [ ] **Step 2: 移动 .env 文件**

```bash
git mv extract/.env .env
git mv extract/.env.example .env.example
```

- [ ] **Step 3: 提交**

```bash
git add eval_reports/ .env .env.example
git commit -m "refactor: move eval_reports and .env to root"
```

---

### Task 6: 修复 extract/agent_loop.py 的 import

**Files:**
- Modify: `extract/agent_loop.py`

- [ ] **Step 1: 修复 import 路径**

文件 `extract/agent_loop.py`：

```python
# 第 9 行，原：
from schemas import PHASES, METADATA_FIELDS
# 改为：
from lib.schemas import PHASES, METADATA_FIELDS

# 第 10 行，原：
from pdf_index import PDFIndex
# 改为：
from extract.pdf_index import PDFIndex

# 第 11 行，原：
from tools import TOOL_DEFINITIONS, execute_tool
# 改为：
from lib.tools import TOOL_DEFINITIONS, execute_tool

# 第 12 行，原：
from prompts import build_system_prompt, build_phase_user_message, build_correction_message
# 改为：
from lib.prompts import build_system_prompt, build_phase_user_message, build_correction_message
```

- [ ] **Step 2: 提交**

```bash
git add extract/agent_loop.py
git commit -m "fix: update agent_loop imports for new directory structure"
```

---

### Task 7: 删除旧文件和运行时目录

**Files:**
- Delete: `extract/pyproject.toml`
- Delete: `extract/uv.lock`
- Delete: `extract/__pycache__/`
- Delete: `extract/.obsidian/`
- Delete: `extract/.pytest_cache/`
- Delete: `extract/.venv/`
- Delete: `extract/.DS_Store`
- Delete: `evluate/`（空目录，typo）

- [ ] **Step 1: 删除 extract/ 下的运行时目录**

```bash
rm -rf extract/__pycache__ extract/.obsidian extract/.pytest_cache extract/.venv extract/.DS_Store
```

- [ ] **Step 2: 删除旧的 pyproject.toml 和 uv.lock**

```bash
git rm extract/pyproject.toml extract/uv.lock
```

- [ ] **Step 3: 删除 evluate/ 空目录**

```bash
rmdir evluate
```

- [ ] **Step 4: 提交**

```bash
git add -A
git commit -m "chore: clean up runtime files and old config"
```

---

### Task 8: 验证和测试

- [ ] **Step 1: 检查目录结构**

Run: `find . -type d -not -path '*/\.*' -not -path '*/__pycache__/*' -not -path '*/node_modules/*' | sort`
Expected: 目录结构符合 spec

- [ ] **Step 2: 验证 import 不报错**

Run: `uv run python -c "from lib.schemas import PHASES; print('lib.schemas OK')"`
Expected: `lib.schemas OK`

Run: `uv run python -c "from lib.prompts import build_system_prompt; print('lib.prompts OK')"`
Expected: `lib.prompts OK`

Run: `uv run python -c "from lib.tools import TOOL_DEFINITIONS; print('lib.tools OK')"`
Expected: `lib.tools OK`

Run: `uv run python -c "from extract.pdf_index import PDFIndex; print('extract.pdf_index OK')"`
Expected: `extract.pdf_index OK`

Run: `uv run python -c "from extract.agent_loop import agent_loop; print('extract.agent_loop OK')"`
Expected: `extract.agent_loop OK`

- [ ] **Step 3: 运行测试**

Run: `uv run pytest extract/ evaluate/ note/ -v`
Expected: 所有测试通过

- [ ] **Step 4: 验证 uv scripts 入口**

Run: `uv run python -c "from evaluate.evaluate import main; print('evaluate entry OK')"`
Expected: `evaluate entry OK`

Run: `uv run python -c "from note.notes import main; print('note entry OK')"`
Expected: `note entry OK`

Run: `uv run python -c "from extract.extract import main; print('extract entry OK')"`
Expected: `extract entry OK`

- [ ] **Step 5: 最终提交（如有修复）**

```bash
git add -A
git commit -m "fix: resolve import issues after directory reorganization"
```
