# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

`vibe-quality-plugin` 是一个 Claude Code 插件，用于对 Python 代码进行重构前后的质量对比分析。面向 AI 辅助开发者（vibe coders），通过客观指标和 AI 评估提供量化的质量改善反馈。

**插件入口命令**：
- 单目录模式：`/vibe-quality-plugin:quality-check <dir> [--html]`
- 对比模式：`/vibe-quality-plugin:quality-check <before_dir> <after_dir> [--html]`
- 评分校准：`/vibe-quality-plugin:calibrate <dir> [--level <production|good|prototype>]`

## 无传统构建系统

本项目**没有** Makefile、package.json 或 setup.py。所有文件均为 Markdown 规范文档，驱动 LLM 行为而非编译执行。

**外部依赖工具**（首次运行时由 `hooks/auto-install.sh` 自动安装）：
- `radon` (pip) — 圈复杂度 + 可维护性指数
- `ruff` (pip) — Bug/风格问题检测
- `bandit` (pip) — 安全漏洞扫描
- `jscpd` (npm) — 代码重复率检测

要求：Python ≥ 3.8

## 架构：5 阶段流水线

```
/quality-check
  Phase 0: 参数验证
  Phase 1: hooks/auto-install.sh（检测并安装缺失工具）
  Phase 2: scanner agent → 输出 SCANNER_DONE 信号
  Phase 3: interpreter agent → 输出 INTERPRETER_DONE 信号
  Phase 4: reporter agent → 输出 REPORTER_DONE 信号
  Phase 5: 询问用户是否需要改进建议（可调用 vibe-explain skill）
```

### 关键文件职责

| 文件 | 职责 |
|------|------|
| `.claude-plugin/plugin.json` | 插件清单，声明命令/Agent/Skill/Hook/依赖 |
| `commands/quality-check.md` | 主命令规范：参数验证、流程编排、错误处理 |
| `agents/scanner.md` | 数据采集：运行 5 个外部工具，输出结构化 JSON |
| `agents/interpreter.md` | 评分引擎：6 个维度评分（各 1–10 分）+ delta |
| `agents/reporter.md` | 报告生成：终端报告 + 可选 HTML 报告 |
| `standards/references.md` | **核心评分标准**：学术引用 + 各维度阈值 + 行业基准 |
| `skills/vibe-explain/SKILL.md` | 将技术指标转为建筑隐喻的通俗语言 |
| `hooks/auto-install.sh` | 依赖自动安装脚本 |

## 数据流

```
原始工具输出（5 个工具）
  ↓ Scanner 聚合
  ↓ JSON: metadata + raw outputs + summary stats
  ↓ Interpreter 评分
  ↓ JSON: 6 维度分数 + before/after delta
  ↓ Reporter 格式化
  ↓ 终端报告 + 可选单文件 HTML（内嵌 Chart.js）
```

## 6 维度评分系统（满分 50 分）

| 维度 | 数据来源 | 类型 |
|------|---------|------|
| 复杂度 | `radon cc` 圈复杂度 | 客观 |
| Bug 与健壮性 | `ruff` 错误密度（每百行） | 客观 |
| 安全性 | `bandit` 严重度 × 置信度加权 | 客观 |
| 简洁性 | `jscpd` 重复率 % | 客观 |
| 可读性 | `radon mi`（基础分）+ Claude 调整（±分） | 混合 |
| 可维护性 | Claude 评估耦合/内聚/依赖/可扩展性 | 主观 |

行业基准：54–60 生产就绪 / 42–53 可用 / 30–41 原型质量 / 18–29 典型 vibe 代码 / <18 需重写

## 关键设计约定

- **Agent 规范是行为指令**，而非代码——所有 Agent 均由 LLM 执行，不是程序
- **评分标准引用学术来源**（McCabe 1976、Martin 2008、Hunt & Thomas 1999、MITRE CWE 等），修改前须查阅 `standards/references.md`
- **信号标记**：每个 Agent 完成后必须输出固定信号（`SCANNER_DONE` / `INTERPRETER_DONE` / `REPORTER_DONE`），命令据此判断执行进度
- **优雅降级**：若某工具运行失败，该维度标记为"数据缺失"并跳过，不中断整体流程
- **vibe-explain skill 语言规范**：只使用建筑/房屋隐喻，禁止未解释的技术术语，单次解释不超过 3 句话
