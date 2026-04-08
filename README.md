# vibe-quality-plugin

A Claude Code plugin for comparing Python code quality before and after refactoring. Generates objective, metric-backed scores across 6 dimensions with human-readable reports designed for vibe coders.

## Installation

在 Claude Code 中依次执行：

```
/plugin marketplace add Xuanaaaaaa/vibe-quality-plugin
/plugin install vibe-quality-plugin@Xuanaaaaaa-vibe-quality-plugin
```

**Requirements**: Python ≥ 3.8. External tools (`radon`, `ruff`, `bandit`, `jscpd`) are auto-installed on first run.

## Usage

```
/quality-check <before_dir> <after_dir> [--html]
```

- `before_dir` — directory of original code
- `after_dir` — directory of refactored code
- `--html` — (optional) also generate a single-file HTML report with radar/bar charts

## Scoring

Six dimensions, 10 points each, **60 points total**:

| Dimension | Data Source | Type |
|-----------|-------------|------|
| Complexity | `radon cc` cyclomatic complexity | Objective |
| Bug & Robustness | `ruff` weighted error density | Objective |
| Security | `bandit` severity × confidence | Objective |
| Simplicity | `jscpd` duplication % | Objective |
| Readability | `radon mi` (base) + Claude (adjustment) | Hybrid |
| Maintainability | Claude evaluation of coupling/cohesion | Subjective |

**Reference benchmarks**: 54–60 production-ready / 42–53 usable / 30–41 prototype / 18–29 typical vibe code / <18 needs rewrite

## Standards

Scoring rules are based on academic and industry references: McCabe (1976), Martin *Clean Code* (2008), Hunt & Thomas *The Pragmatic Programmer* (1999), MITRE CWE Top 25, Google Engineering Practices (2019), Oman & Hagemeister (1992).
