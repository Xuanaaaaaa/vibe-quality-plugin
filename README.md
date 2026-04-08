# vibe-quality-plugin

> 为 vibe coder 设计的 Python 代码质量对比分析插件

---

## 目录 / Contents

- [中文说明](#中文说明)
- [English](#english)

---

## 中文说明

### 项目意义与价值

AI 辅助编程（vibe coding）正在让越来越多的人能够快速写出可运行的代码，但"能跑"和"质量好"之间存在巨大落差。重构之后代码到底有没有变好？好了多少？这个问题长期缺乏客观答案。

**vibe-quality-plugin** 解决的正是这个问题：

- **量化改善**：用 6 个维度、60 分制给出重构前后的对比评分，让进步看得见
- **有据可查**：评分规则基于 McCabe (1976)、Clean Code (Martin, 2008)、MITRE CWE Top 25、DRY 原则等学术与行业标准，而非主观判断
- **看得懂**：报告用建筑比喻翻译技术指标，即使不熟悉代码质量理论也能理解
- **可追踪**：每次重构后运行一次，持续追踪代码质量演进曲线

---

### 评分体系与设计依据

插件将代码质量分解为 6 个维度，满分 60 分：

| 维度 | 工具 | 类型 | 权威依据 |
|------|------|------|----------|
| 复杂度 | `radon cc` | 🔢 客观 | McCabe (1976) 圈复杂度理论 |
| 潜在 Bug & 健壮性 | `ruff` | 🔢 客观 | MITRE CWE / Clean Code (Martin, 2008) |
| 安全性 | `bandit` | 🔢 客观 | CWE Top 25 (MITRE) |
| 简洁性 | `jscpd` | 🔢 客观 | DRY 原则 / The Pragmatic Programmer (1999) |
| 可读性 | `radon mi` + Claude | 🔢+🤖 混合 | Oman & Hagemeister (1992) / Google Eng Practices |
| 可维护性 | Claude | 🤖 主观 | Yourdon & Constantine (1979) / Google Eng Practices |

**行业基准参考**（估算值，基于各工具官方阈值推导）：

| 综合分 | 参考评级 |
|--------|----------|
| 54–60 | 生产就绪 |
| 42–53 | 基本可用，有改进空间 |
| 30–41 | 原型质量，上线前需重构 |
| 18–29 | vibe coding 典型输出 |
| < 18 | 需要全面重写 |

---

### 架构设计

插件采用**三 Agent 流水线**架构，职责严格分离：

```
用户运行 /quality-check <before_dir> <after_dir>
         │
         ▼
  自动检测并安装依赖工具（radon / ruff / bandit / jscpd）
         │
         ▼
  ┌─────────────┐     读取
  │   Scanner   │ ◄── standards/references.md
  │  并行扫描   │     采集原始数据（5 个工具）
  └──────┬──────┘
         │ JSON（原始数字）
         ▼
  ┌─────────────┐     读取
  │ Interpreter │ ◄── standards/references.md
  │  6 维度评分 │     严格按标准换算分数
  └──────┬──────┘
         │ JSON（评分结果）
         ▼
  ┌─────────────┐
  │  Reporter   │     生成终端报告 + 可选 HTML 报告
  └──────┬──────┘     调用 vibe-explain skill 生成大白话总结
         │
         ▼
  询问是否需要针对最低分维度给出改进建议
```

各组件职责：

- **Scanner**：纯数据采集，不做任何解读，输出结构化 JSON
- **Interpreter**：纯评分，严格对照 `standards/references.md`，不输出建议
- **Reporter**：纯展示，将评分 JSON 转为人类可读报告
- **vibe-explain skill**：语言翻译层，将技术指标转为建筑比喻的通俗语言

---

### 安装

在 Claude Code 中依次执行：

```
/plugin marketplace add Xuanaaaaaa/vibe-quality-plugin
/plugin install vibe-quality-plugin@Xuanaaaaaa-vibe-quality-plugin
/reload-plugins
```

**依赖环境**：Python ≥ 3.8。外部工具（`radon`、`ruff`、`bandit`、`jscpd`）在首次运行时自动安装，无需手动配置。

---

### 使用方法

**基本用法**：
```
/quality-check <重构前目录> <重构后目录>
```

**同时生成 HTML 可视化报告**：
```
/quality-check <重构前目录> <重构后目录> --html
```

**示例**：
```
/quality-check ./my-prototype ./my-refactored
/quality-check ./v1 ./v2 --html
```

运行后插件会：
1. 自动检测并安装缺失工具
2. 并行扫描两个目录，采集原始指标
3. 对 6 个维度打分（before / after 各一份）
4. 输出终端对比报告，含各维度得分变化和综合分 delta
5. （可选）生成 `quality-report.html`，含雷达图和柱状图
6. 询问是否需要针对最低分维度给出具体改进建议

---

---

## English

### Why This Plugin

AI-assisted coding (vibe coding) has made it easy to write working code, but "it runs" and "it's good" are very different things. After a refactor, has the code actually improved? By how much? These questions rarely have objective answers.

**vibe-quality-plugin** addresses exactly this gap:

- **Quantified improvement**: A 6-dimension, 60-point scoring system shows before/after scores so progress is visible
- **Evidence-based**: Scoring rules are grounded in academic and industry standards — McCabe (1976), Clean Code (Martin, 2008), MITRE CWE Top 25, the DRY principle — not subjective opinion
- **Human-readable**: Reports translate technical metrics into building/architecture metaphors anyone can understand
- **Trackable**: Run after every refactor to build a continuous quality history

---

### Scoring System & Design Basis

The plugin measures code quality across 6 dimensions, scored out of 60:

| Dimension | Tool | Type | Authority |
|-----------|------|------|-----------|
| Complexity | `radon cc` | 🔢 Objective | McCabe (1976) Cyclomatic Complexity |
| Bug & Robustness | `ruff` | 🔢 Objective | MITRE CWE / Clean Code (Martin, 2008) |
| Security | `bandit` | 🔢 Objective | CWE Top 25 (MITRE) |
| Simplicity | `jscpd` | 🔢 Objective | DRY Principle / The Pragmatic Programmer (1999) |
| Readability | `radon mi` + Claude | 🔢+🤖 Hybrid | Oman & Hagemeister (1992) / Google Eng Practices |
| Maintainability | Claude | 🤖 Subjective | Yourdon & Constantine (1979) / Google Eng Practices |

**Industry benchmark reference** (estimated from tool official thresholds):

| Score | Rating |
|-------|--------|
| 54–60 | Production-ready |
| 42–53 | Usable, room for improvement |
| 30–41 | Prototype quality, needs refactor before shipping |
| 18–29 | Typical vibe coding output |
| < 18 | Needs full rewrite |

---

### Architecture

The plugin uses a **three-agent pipeline** with strict separation of concerns:

```
User runs /quality-check <before_dir> <after_dir>
         │
         ▼
  Auto-detect and install missing tools (radon / ruff / bandit / jscpd)
         │
         ▼
  ┌─────────────┐     reads
  │   Scanner   │ ◄── standards/references.md
  │  (parallel) │     collects raw metrics from 5 tools
  └──────┬──────┘
         │ JSON (raw numbers)
         ▼
  ┌─────────────┐     reads
  │ Interpreter │ ◄── standards/references.md
  │  6-dim score│     converts metrics to scores strictly by the rules
  └──────┬──────┘
         │ JSON (scores)
         ▼
  ┌─────────────┐
  │  Reporter   │     generates terminal report + optional HTML report
  └──────┬──────┘     uses vibe-explain skill for plain-language summary
         │
         ▼
  Ask if user wants improvement suggestions for lowest-scoring dimension
```

Component responsibilities:

- **Scanner**: Pure data collection. No interpretation. Outputs structured JSON.
- **Interpreter**: Pure scoring. Strictly follows `standards/references.md`. No suggestions.
- **Reporter**: Pure presentation. Converts score JSON to human-readable reports.
- **vibe-explain skill**: Translation layer. Converts technical metrics to plain language using building metaphors.

---

### Installation

Run these commands in Claude Code:

```
/plugin marketplace add Xuanaaaaaa/vibe-quality-plugin
/plugin install vibe-quality-plugin@Xuanaaaaaa-vibe-quality-plugin
/reload-plugins
```

**Requirements**: Python ≥ 3.8. External tools (`radon`, `ruff`, `bandit`, `jscpd`) are auto-installed on first run — no manual setup needed.

---

### Usage

**Basic usage**:
```
/quality-check <before_dir> <after_dir>
```

**With HTML visualization report**:
```
/quality-check <before_dir> <after_dir> --html
```

**Examples**:
```
/quality-check ./my-prototype ./my-refactored
/quality-check ./v1 ./v2 --html
```

After running, the plugin will:
1. Auto-detect and install any missing tools
2. Scan both directories in parallel and collect raw metrics
3. Score all 6 dimensions for both before and after
4. Output a terminal comparison report with per-dimension deltas and total score change
5. *(Optional)* Generate `quality-report.html` with radar and bar charts
6. Ask if you want specific improvement suggestions for the lowest-scoring dimension
