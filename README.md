# vibe-quality-plugin

> A Python code quality comparison plugin for vibe coders

**[中文版](README.zh.md)** | **English**

---

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

### Updating

To update to the latest version without reinstalling:

```
/plugin update vibe-quality-plugin@Xuanaaaaaa-vibe-quality-plugin
/reload-plugins
```

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
