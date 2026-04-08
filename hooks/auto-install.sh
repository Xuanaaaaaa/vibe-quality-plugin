#!/bin/bash
#!/bin/bash
# hooks/auto-install.sh
# 自动检测并安装 vibe-quality-plugin 所需的外部工具
# 在 quality-check 命令执行前由 Claude Code 自动调用

set -e

# ── 颜色输出 ──────────────────────────────────────────
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
RESET='\033[0m'

ok()   { echo -e "${GREEN}  ✓ $1${RESET}"; }
warn() { echo -e "${YELLOW}  ⚠ $1${RESET}"; }
fail() { echo -e "${RED}  ✗ $1${RESET}"; }

# ── 工具定义 ──────────────────────────────────────────
# 格式：工具名|pip包名|检测命令|用途|对应维度
TOOLS=(
  "radon|radon|python3 -m radon --version|圈复杂度 & 可维护性指数|复杂度 / 可读性"
  "ruff|ruff|python3 -m ruff --version|潜在 Bug 检测|潜在Bug & 健壮性"
  "bandit|bandit|python3 -m bandit --version|安全漏洞扫描|安全性"
  "jscpd|jscpd|jscpd --version|代码重复率检测|简洁性"
)

# ── 主流程 ────────────────────────────────────────────
echo ""
echo "  检查依赖工具..."
echo "  ─────────────────────────────────────"

FAILED_TOOLS=()
INSTALLED_TOOLS=()

for entry in "${TOOLS[@]}"; do
  IFS='|' read -r tool_name pip_name check_cmd purpose dimension <<< "$entry"

  if eval "$check_cmd" > /dev/null 2>&1; then
    version=$(eval "$check_cmd" 2>/dev/null | head -1)
    ok "$tool_name 已安装（$version）"
  else
    warn "$tool_name 未安装，正在安装..."

    # 优先用 pip，检测 pip3 / pip
    if command -v pip3 > /dev/null 2>&1; then
      PIP="pip3"
    elif command -v pip > /dev/null 2>&1; then
      PIP="pip"
    else
      fail "$tool_name 安装失败：未找到 pip，请手动安装"
      FAILED_TOOLS+=("$tool_name")
      continue
    fi

    # jscpd 需要 npm
    if [ "$tool_name" = "jscpd" ]; then
      if command -v npm > /dev/null 2>&1; then
        if npm install -g jscpd > /dev/null 2>&1; then
          ok "$tool_name 安装成功"
          INSTALLED_TOOLS+=("$tool_name")
        else
          fail "$tool_name 安装失败（npm install -g jscpd 出错）"
          FAILED_TOOLS+=("$tool_name")
        fi
      else
        fail "$tool_name 安装失败：未找到 npm，请先安装 Node.js"
        FAILED_TOOLS+=("$tool_name")
      fi
      continue
    fi

    # pip 安装
    if $PIP install "$pip_name" --quiet 2>/dev/null; then
      ok "$tool_name 安装成功"
      INSTALLED_TOOLS+=("$tool_name")
    else
      fail "$tool_name 安装失败，请手动运行：$PIP install $pip_name"
      FAILED_TOOLS+=("$tool_name")
    fi
  fi
done

echo "  ─────────────────────────────────────"

# ── 结果汇报 ──────────────────────────────────────────
if [ ${#INSTALLED_TOOLS[@]} -gt 0 ]; then
  echo ""
  echo -e "${GREEN}  新安装的工具：${INSTALLED_TOOLS[*]}${RESET}"
fi

if [ ${#FAILED_TOOLS[@]} -gt 0 ]; then
  echo ""
  warn "以下工具安装失败，对应维度将标记为「数据缺失」："
  for t in "${FAILED_TOOLS[@]}"; do
    echo "    - $t"
  done
  echo ""
  # 输出机器可读的失败列表，供 quality-check.md 读取
  echo "FAILED_TOOLS=${FAILED_TOOLS[*]}"
  exit 1
fi

echo ""
echo "  所有依赖工具已就绪，开始扫描..."
echo ""
exit 0