# standards/references.md
# 权威标准映射表 — vibe-quality-plugin

## 使用说明（给 interpreter agent 读）

本文件是 interpreter agent 打分时的**唯一依据**。
规则：
- 每个维度的分数必须严格按照本文件的规则计算，禁止主观估分
- 每个分数输出时必须注明"依据来源"字段中的标准名称
- 标注 【待补充】 的字段，当前使用保守默认值，待用户确认后更新

---

## 维度一：复杂度

**数据来源**：🔢 客观（工具测量）
**工具**：`radon cc`
**命令**：`radon cc <目录> -a -s`

### 权威来源
- **McCabe, T.J. (1976)**. "A Complexity Measure". *IEEE Transactions on Software Engineering*, 2(4), 308–320.
  - 提出圈复杂度（Cyclomatic Complexity）概念，V(G) = E - N + 2P
  - 原文建议阈值：单函数复杂度不超过 10
- **radon 官方评级**（直接实现 McCabe 算法）：
  - A：1–5   极低风险
  - B：6–10  低风险（McCabe 原文推荐上限）
  - C：11–15 中等风险，建议重构
  - D：16–20 高风险，需要重构
  - E：21–25 极高风险
  - F：26+   不可测试

### 评分规则
取所有函数复杂度的**平均评级**换算：

| radon 平均评级 | 得分 |
|---------------|------|
| A（均值 ≤ 5） | 10   |
| B（均值 ≤ 10）| 8    |
| C（均值 ≤ 15）| 5    |
| D（均值 ≤ 20）| 3    |
| E/F（均值 > 20）| 1  |

---

## 维度二：潜在 Bug & 健壮性

**数据来源**：🔢 客观（工具测量）
**工具**：`ruff check`
**命令**：`ruff check <目录> --output-format json`

### 权威来源
- **Common Weakness Enumeration（CWE）**，MITRE 维护，部分覆盖：
  - ruff 规则 B 系列（flake8-bugbear）覆盖常见 bug 模式
  - 注意：ruff **不是** CWE 的完整实现，仅部分交叉
- **Martin, R.C. (2008)**. *Clean Code*. Prentice Hall.
  - 函数应只做一件事（Single Responsibility）
  - 避免可变默认参数、裸异常捕获等常见 Python 陷阱
- **ruff 重点规则（与健壮性相关）**：
  - `B006`：可变默认参数（经典 Python 隐性 bug）
  - `B007`：循环变量未使用
  - `B017`：`assertRaises` 未指定异常类型
  - `E711/E712`：与 None/True/False 的错误比较
  - `F811`：变量重复定义
  - `F841`：赋值后从未使用的变量

### 评分规则
ruff 输出区分两个级别，采用**加权折算**后统计等效 error 数：
- **error**：权重 1.0（完整计入）
- **warning**：权重 0.5（折半计入）

等效 error 数 = error 数量 × 1.0 + warning 数量 × 0.5

按**每百行代码的等效 error 数**（密度）计算，避免文件数量影响绝对值：

| 每百行等效 error 数 | 得分 |
|--------------------|------|
| 0                  | 10   |
| 1–3                | 8    |
| 4–8                | 6    |
| 9–15               | 4    |
| 16–25              | 2    |
| > 25               | 1    |

---

## 维度三：安全性

**数据来源**：🔢 客观（工具测量）
**工具**：`bandit`
**命令**：`bandit -r <目录> -f json`

### 权威来源
- **CWE Top 25 Most Dangerous Software Weaknesses**（MITRE，每年更新）
  - bandit 是 Python 安全扫描的**事实标准工具**，规则直接对应 CWE 分类
  - 主要覆盖：
    - CWE-78：OS 命令注入（bandit: B602/B603/B604）
    - CWE-89：SQL 注入（bandit: B608）
    - CWE-502：不安全的反序列化（bandit: B301/B302）
    - CWE-327：使用已知弱加密算法（bandit: B303/B304/B305）
    - CWE-330：随机数不充分（bandit: B311）
    - CWE-676：使用危险函数（bandit: B eval 系列）

### bandit 输出结构
每个问题带有两个维度：
- **severity**：HIGH / MEDIUM / LOW
- **confidence**：HIGH / MEDIUM / LOW

### 评分规则

**第一步：计算加权问题数**

按 severity × confidence 组合计算权重，对每条告警累加：

| 组合 | 权重 |
|------|------|
| HIGH severity + HIGH confidence | 4 |
| HIGH severity + MEDIUM confidence | 3 |
| MEDIUM severity + HIGH confidence | 2 |
| MEDIUM severity + MEDIUM confidence | 1 |
| LOW severity（任意 confidence）| 0.5 |

**第二步：计算每千行加权密度**

密度 = 加权问题总数 ÷ （总代码行数 / 1000）

与 Bug & 健壮性维度采用相同的密度归一化逻辑，
避免大型代码库因绝对问题数更多而被系统性低估。

**第三步：按密度区间映射得分**

| 每千行加权密度 | 得分 |
|---------------|------|
| 0             | 10   |
| 0–1           | 9    |
| 1–2           | 8    |
| 2–4           | 6    |
| 4–7           | 4    |
| 7–12          | 2    |
| > 12          | 1    |

**已知系统性误报排除列表**

以下 bandit 规则在主流 Python 代码库中具有高误报率，
相关告警**不计入**加权问题数：

| 规则 ID | 误报原因 |
|---------|---------|
| B704 | `markupsafe.Markup` 是 XSS 防护机制本身，非漏洞 |
| B101 | `assert` 是健壮性检查而非安全控制，已由维度二（Bug&健壮性）覆盖，重复计入安全维度 |
| B324 | RFC 协议强制弱算法实现：当代码实现的是 IETF RFC 规定的认证协议（如 HTTP Digest Auth、NTLM），算法选择被协议锁定，不属于开发者安全决策失误 |

**各规则排除条件：**

- **B704**：告警 `issue_text` 中包含 `markupsafe.Markup` 或 `Markup`，且同文件中有 `from markupsafe import Markup` 导入。
- **B101**：无条件排除（assert_used 在任何上下文中均不属于安全漏洞）。
- **B324**：同一文件中存在以下任意协议实现特征——
  - 变量名包含 `nonce`、`cnonce`、`qop`、`realm`、`HA1`、`HA2`
  - 或字符串中同时出现 `Digest` 与 `Authorization`/`WWW-Authenticate`
  - 或注释/docstring 中引用 RFC 2617 / RFC 7616 / RFC 4616 / NTLM

> 注：此列表应保守扩展，只有在多个独立项目校准后
> 确认为系统性误报时才可新增规则。

---

## 维度四：简洁性

**数据来源**：🔢 客观（工具测量）
**工具**：`jscpd`
**命令**：`jscpd <目录> --languages python --min-lines 5 --reporters json`

### 权威来源
- **Hunt, A. & Thomas, D. (1999)**. *The Pragmatic Programmer*. Addison-Wesley.
  - DRY 原则（Don't Repeat Yourself）：
    "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."
- **行业经验阈值**（来自 SonarQube 等工具的生产实践）：
  - < 3%：优秀
  - 3–10%：可接受
  - 10–20%：有技术债
  - > 20%：严重问题

### 参数说明
`--min-lines 5`（jscpd 默认值）：5 行以上才计为重复块。
- 低于此阈值会将正常 import 等短片段误算为重复，导致虚高误报
- 高于此阈值（如 20 行）会漏掉大量真实重复，导致漏报
- 5 行为工具官方默认，符合生产实践经验，采用此值

### 评分规则
按 jscpd 输出的**重复率百分比**计算：

| 重复率 | 得分 |
|--------|------|
| 0–3%   | 10   |
| 3–8%   | 8    |
| 8–12%  | 6    |
| 12–18% | 4    |
| 18–25% | 2    |
| > 25%  | 1    |

---

## 维度五：可读性

**数据来源**：🔢 客观辅助（radon mi）+ 🤖 主观补充（Claude 评估）
**工具**：`radon mi`（客观底座）+ interpreter agent 判断（主观补充）
**命令**：`radon mi <目录> -s`

### 权威来源

**客观部分——Maintainability Index**
- **Oman, P. & Hagemeister, J. (1992)**. "Metrics for Assessing a Software System's Maintainability". *IEEE Conference on Software Maintenance*.
  - 提出可维护性指数（MI）原始公式
- **Microsoft / Visual Studio 团队**（后续修订并广泛推广）：
  - MI = MAX(0, (171 − 5.2 × ln(HV) − 0.23 × CC − 16.2 × ln(LOC)) × 100/171)
  - HV = Halstead Volume（代码信息量）
  - CC = Cyclomatic Complexity（圈复杂度）
  - LOC = Lines of Code
  - radon 直接实现此公式，输出 0–100 分

- **radon 官方评级**：
  - A（20–100）：可维护，代码健康
  - B（10–19）：中等，存在可读性问题
  - C（0–9）：难以维护，需要重构

**主观部分**
- **Google Engineering Practices**（2019，开源）：
  - 命名必须能自我说明意图（self-documenting）
  - 代码应该让不熟悉该代码库的人也能读懂
- **Martin, R.C. (2008)**. *Clean Code*. Prentice Hall.
  - 命名：有意义、可发音、可搜索
  - 函数：建议不超过 20 行，参数不超过 3 个
  - 注释：解释"为什么"，而非"做了什么"

### 评分规则

**第一步：radon mi 客观底分（0–7 分）**

| radon mi 均值 | 评级 | 客观底分 |
|--------------|------|---------|
| 20–100       | A    | 7       |
| 10–19        | B    | 4       |
| 0–9          | C    | 1       |

**第二步：interpreter agent 主观修正（−2 至 +3 分）**

在客观底分基础上，根据以下子维度调整：

| 子维度 | 判断标准 | 修正幅度 |
|--------|----------|---------|
| 命名质量 | 变量/函数名是否能直接看出意图 | ±1 |
| 注释质量 | 复杂逻辑是否有解释性注释 | ±1 |
| 代码结构 | 模块/文件组织是否直观 | ±1 |

**最终得分** = 客观底分 + 主观修正，上限 10 分，下限 1 分。

输出时**必须同时注明**：
1. radon mi 数值和对应评级（客观来源）
2. 一句大白话说明主观修正的理由

---

## 维度六：可维护性

**数据来源**：🤖 主观（Claude 评估）
**工具**：无，由 interpreter agent 直接判断（`pydeps` 可作辅助参考）

### 权威来源
- **Yourdon, E. & Constantine, L. (1979)**. *Structured Design*. Prentice Hall.
  - 耦合（Coupling）：模块间依赖越少越好
  - 内聚（Cohesion）：模块内部功能越集中越好
  - 理想状态：低耦合 + 高内聚
- **Google Engineering Practices**（2019）：
  - 代码改动应该局限在合理范围内，不应"牵一发而动全身"
  - 依赖关系应该有明确方向，避免循环依赖

### 评分维度（interpreter agent 逐项判断）
| 子维度 | 判断标准 |
|--------|----------|
| 耦合度 | 修改一处是否会影响很多不相关的地方 |
| 内聚性 | 每个模块/函数是否职责单一 |
| 依赖清晰度 | import 结构是否清晰，有无循环依赖迹象 |
| 扩展难度 | 添加新功能是否需要大量改动现有代码 |

### 评分规则
综合以上子维度给出 1–10 分，**必须附一句大白话说明理由**。

---

## 行业基准分

> **说明**：以下区间为估算值，基于各工具官方阈值推导，非实测数据。
> 实际项目得分受代码规模、类型、领域差异影响，请将本区间作为参考方向，而非绝对标准。
> （方案C：估算区间，后续可对 requests / flask / httpx 实测后校准）

| 代码类型 | 典型得分区间 |
|----------|-------------|
| 优秀生产级代码（如知名开源库） | 50–58 / 60 |
| 普通生产级代码（规范但不追求极致） | 40–49 / 60 |
| vibe coding 原型（AI 生成、未经重构） | 24–36 / 60 |
| 快速脚本 / 一次性代码 | 12–24 / 60 |

---

## 综合分计算

总分 = 各维度得分之和，满分 60 分（6 个维度 × 10 分）

| 综合分 | 参考评级 |
|--------|----------|
| 54–60  | 生产就绪 |
| 42–53  | 基本可用，有改进空间 |
| 30–41  | 原型质量，上线前需重构 |
| 18–29  | vibe coding 典型输出 |
| < 18   | 需要全面重写 |

---

## 版本记录

| 版本 | 变更内容 |
|------|----------|
| v0.1 | 初始版本，6 维度框架，评分阈值待用户确认 |
| v0.2 | 维度五引入 radon mi 作为客观底座，可读性从纯主观改为客观辅助 + 主观修正 |
| v0.3 | 补全4处待确认内容：ruff error/warning 权重区分、bandit 最低0分、jscpd min-lines=5、基准分方案C |
| v0.4 | 安全维度改为密度加权评分（每千行加权密度），新增已知系统性误报排除列表（B704）（基于 flask 校准，共 2 处修改） |
| v0.5 | 安全维度误报排除列表新增 B101（assert 属健壮性非安全）和 B324（RFC 协议强制弱算法实现）（基于 requests 校准，共 2 处修改） |
| v0.6 | 简洁性评分区间细化：8–15%→5 拆分为 8–12%→6 / 12–18%→4 / 18–25%→2，减少边界附近评分落差（基于 fastapi 校准，共 1 处修改） |