# Command: quality-check

## 用法

```
/quality-check <before_dir> <after_dir> [--html]
```

**参数说明**：
- `before_dir`：重构前代码目录路径（必填）
- `after_dir`：重构后代码目录路径（必填）
- `--html`：生成 HTML 可视化报告（可选）

**示例**：
```
/quality-check ./my-prototype ./my-refactored-code
/quality-check ./my-prototype ./my-refactored-code --html
```

---

## 执行流程

### 阶段 0：参数校验

检查参数是否完整，若缺少 `before_dir` 或 `after_dir`，输出提示并停止：
```
用法：/quality-check <重构前目录> <重构后目录> [--html]
示例：/quality-check ./before ./after
```

记录是否携带 `--html` 标志，供后续 reporter 使用。

---

### 阶段 1：环境检查与安装

运行 `hooks/auto-install.sh`。

若有工具安装失败，询问用户：
```
工具 <名称> 安装失败，是否继续（跳过对应维度）？[y/n]
```

---

### 阶段 2：数据采集

调用 `agents/scanner.md`，传入两个目录路径。

等待 `SCANNER_DONE` 信号。

若 scanner 报错，输出错误信息并停止，不进入下一阶段。

---

### 阶段 3：评分

调用 `agents/interpreter.md`，传入 scanner 的 JSON 输出。

等待 `INTERPRETER_DONE` 信号。

---

### 阶段 4：报告生成

调用 `agents/reporter.md`，传入 interpreter 的评分 JSON 和 `--html` 标志状态。

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