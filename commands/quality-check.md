---
description: 对 Python 代码进行重构前后的质量对比分析，生成六维评分报告
allowed-tools: Bash, Read, Write, Glob, Grep, Agent
---

# Command: quality-check

## 用法

```
/quality-check <目录> [--html]
/quality-check <before_dir> <after_dir> [--html]
```

**参数说明**：
- 单目录模式：传入 1 个目录路径，对该目录进行绝对质量评分，与行业基准对比
- 对比模式：传入 2 个目录路径（重构前/后），进行对比评分
- `--html`：生成 HTML 可视化报告（可选）

**示例**：
```
/quality-check ./my-library
/quality-check ./my-library --html
/quality-check ./my-prototype ./my-refactored-code
/quality-check ./my-prototype ./my-refactored-code --html
```

---

## 执行流程

### 阶段 0：参数校验

统计非 `--html` 参数的数量，判断运行模式：

- **单目录模式**（1 个参数）：对该目录进行绝对质量评分，与行业基准对比
- **对比模式**（2 个参数）：对 before/after 两个目录进行对比评分（原有行为）
- **参数错误**（0 个或 3 个以上）：输出提示并停止：

```
用法：
  /quality-check <目录>                    # 单目录评分
  /quality-check <重构前目录> <重构后目录>  # 对比评分
可选参数：--html（生成 HTML 报告）
```

记录运行模式（`single` / `compare`）和 `--html` 标志，供后续阶段使用。

---

### 阶段 1：环境检查与安装

运行 `hooks/auto-install.sh`。

若有工具安装失败，询问用户：
```
工具 <名称> 安装失败，是否继续（跳过对应维度）？[y/n]
```

---

### 阶段 2：数据采集

调用 `agents/scanner.md`，传入运行模式和目录路径：
- single 模式：传入 `MODE=single`、`DIR=<目录路径>`
- compare 模式：传入 `MODE=compare`、`BEFORE_DIR=<重构前>`、`AFTER_DIR=<重构后>`

等待 `SCANNER_DONE` 信号。

若 scanner 报错，输出错误信息并停止，不进入下一阶段。

---

### 阶段 3：评分

调用 `agents/interpreter.md`，传入 scanner 的 JSON 输出。

- single 模式：只对 current 打分，跳过 delta 计算
- compare 模式：对 before/after 分别打分并计算 delta

等待 `INTERPRETER_DONE` 信号。

---

### 阶段 4：报告生成

调用 `agents/reporter.md`，传入 interpreter 的评分 JSON 和 `--html` 标志状态。

- single 模式：使用单列格式，与行业基准对比
- compare 模式：使用双列对比格式

等待 `REPORTER_DONE` 信号。

---

### 阶段 5：询问是否需要修改建议

报告输出完毕后，询问用户：

```
────────────────────────────────────────
是否需要针对得分最低的维度给出改进建议？

  得分最低：<维度名>（<分数>/10）
  输入 y 继续，输入 n 结束

────────────────────────────────────────
```

**若用户选择 y**：
针对得分最低的 1–2 个维度，给出具体的、可操作的改进建议。建议格式：
- 问题描述（用大白话）
- 具体改法（代码示例或操作步骤）
- 预期效果

**若用户选择 n**：
```
好的，扫描完成。你可以随时重新运行 /quality-check 来追踪代码质量变化。
```

---

## 输出文件

| 文件 | 条件 |
|------|------|
| 终端报告 | 始终输出 |
| `./quality-report.html` | 携带 `--html` 参数时生成 |

---

## 错误码参考

| 情况 | 行为 |
|------|------|
| 目录不存在 | 报错并停止，提示检查路径 |
| 目录无 .py 文件 | 警告但继续，相关维度得分为 0 |
| 工具未安装且用户拒绝安装 | 跳过对应维度，在报告中标注"数据缺失" |
| scanner 超时 | 询问用户是否重试或跳过 |