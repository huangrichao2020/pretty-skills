#!/bin/bash
# 橙皮书项目初始化脚本
# 在指定目录创建完整的书籍 PDF 项目骨架
#
# 用法：
#   bash init-project.sh <项目目录> <书名>
#   bash init-project.sh ./my-guide "Python完全指南"
#
# 前置依赖：
#   - Node.js >= 16
#   - Playwright: npm install playwright && npx playwright install chromium
#   - (可选) pandoc >= 3.0：DOCX 构建用
#   - (可选) Python 3 + ebooklib：EPUB 构建用
#   - (可选) npm install docx + python3 lxml：DOCX 完整流水线用

set -e

PROJECT_DIR="${1:?用法: bash init-project.sh <项目目录> <书名>}"
TITLE="${2:?请提供书名，如: \"Python完全指南\"}"
TODAY=$(date +%Y-%m-%d)
VERSION_DATE=$(date +%y%m%d)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATES_DIR="$SKILL_DIR/templates"

if [ -d "$PROJECT_DIR" ] && [ "$(ls -A "$PROJECT_DIR" 2>/dev/null)" ]; then
  echo "❌ 目录已存在且非空: $PROJECT_DIR"
  exit 1
fi

echo "📦 初始化项目: $TITLE"
echo "   目录: $PROJECT_DIR"
echo ""

# 创建目录结构
mkdir -p "$PROJECT_DIR"/{fragments,output,versions,research,封面}

# 复制模板文件
cp "$TEMPLATES_DIR/styles.css" "$PROJECT_DIR/styles.css"
cp "$TEMPLATES_DIR/build.js" "$PROJECT_DIR/build.js"
cp "$TEMPLATES_DIR/build-pdf.js" "$PROJECT_DIR/build-pdf.js"
cp "$TEMPLATES_DIR/update.sh" "$PROJECT_DIR/update.sh"
chmod +x "$PROJECT_DIR/update.sh"

# 复制 DOCX/EPUB 构建脚本（如果存在）
[ -f "$TEMPLATES_DIR/build-docx.js" ] && cp "$TEMPLATES_DIR/build-docx.js" "$PROJECT_DIR/build-docx.js"
[ -f "$TEMPLATES_DIR/build-epub.py" ] && cp "$TEMPLATES_DIR/build-epub.py" "$PROJECT_DIR/build-epub.py"
[ -f "$TEMPLATES_DIR/fix-docx-pagebreaks.py" ] && cp "$TEMPLATES_DIR/fix-docx-pagebreaks.py" "$PROJECT_DIR/fix-docx-pagebreaks.py"

# 复制 HTML 模板
if [ -d "$TEMPLATES_DIR/fragments" ]; then
  cp "$TEMPLATES_DIR/fragments/"*.html "$PROJECT_DIR/fragments/" 2>/dev/null || true
fi

# 复制占位符配置（按需替换为自己的真实信息）
if [ -f "$SKILL_DIR/placeholder-config.json" ]; then
  cp "$SKILL_DIR/placeholder-config.json" "$PROJECT_DIR/placeholder-config.json"
fi

# 创建 version.json（使用日期版本号 vYYMMDD）
cat > "$PROJECT_DIR/version.json" << EOF
{
  "version": "$VERSION_DATE",
  "build": 0,
  "lastUpdate": "$TODAY",
  "title": "$TITLE"
}
EOF

# 创建 CHANGELOG.md
cat > "$PROJECT_DIR/CHANGELOG.md" << EOF
# $TITLE 更新日志

> 格式：\`[vYYMMDD] YYYY-MM-DD — 摘要\`
> 版本规则：日期版本（vYYMMDD），每天的实质性更新都 +1 天
> 修订（错别字/小修）→ 只增加 build 号
EOF

# 创建 PROJECT.md 模板
cat > "$PROJECT_DIR/PROJECT.md" << EOF
# $TITLE — 项目计划

> 目标：
> 规格：
> 状态：规划中
> 出版方：（自己 / 微信读书 / 出版社）

---

## 章节大纲

| Part | 节 | 标题 | 核心内容 | 信息来源 | 状态 |
|------|----|------|---------|---------|------|
| 1 | 01 | | | | ⬜ |
| 1 | 02 | | | | ⬜ |

---

## 调研资料索引

| # | 文件 | 内容 | 状态 |
|---|------|------|------|
| 1 | research/ | | ⏳ |

---

## 进度追踪

| 步骤 | 状态 | 说明 |
|------|------|------|
| 调研 | ⏳ | |
| 规划 | ⬜ | |
| 写作 | ⬜ | |
| 审校（4 遍） | ⬜ | |
| 事实核查 | ⬜ | |
| 一致性审查 | ⬜ | |
| 构建 | ⬜ | |
| 封面 | ⬜ | |

---

## 关键数据速查

（所有需要复用的事实/数据集中放这里，避免章节间冲突）

-

---

## 占位符替换

打开 \`placeholder-config.json\`，按实际情况填入：
- 作者名、笔名、社交账号
- 公众号名称、二维码图片（替换 \`fragments/gzh-qrcode.jpg\`）
- 官网、GitHub、X、B 站等链接

详见 SKILL.md 的「占位符速查」表。
EOF

# 创建 README.md
cat > "$PROJECT_DIR/README.md" << EOF
# $TITLE

> 状态：规划中 · v$VERSION_DATE

## 一句话定位

（这本书帮谁解决什么问题）

## 章节结构

（待规划）

## 出版方

- PDF 免费版：分发渠道
- DOCX 出版社版：出版社名称
- EPUB 电子版：发布平台

## 进度

- 调研 ⏳
- 规划 ⬜
- 写作 ⬜
- 审校 ⬜
- 构建 ⬜
EOF

# 检查依赖
echo "🔍 检查依赖..."
HAS_NODE=true
HAS_PLAYWRIGHT=true
HAS_PANDOC=true
HAS_PYTHON3=true

if ! command -v node &>/dev/null; then
  HAS_NODE=false
  echo "   ⚠️  未找到 Node.js — 请安装: https://nodejs.org/"
fi

if [ "$HAS_NODE" = true ]; then
  if ! node -e "require('playwright')" 2>/dev/null; then
    HAS_PLAYWRIGHT=false
    echo "   ⚠️  未找到 Playwright — 请运行:"
    echo "      npm install playwright"
    echo "      npx playwright install chromium"
  fi
fi

if ! command -v pandoc &>/dev/null; then
  HAS_PANDOC=false
  echo "   ⚠️  未找到 pandoc（DOCX 构建需要）— brew install pandoc"
fi

if ! command -v python3 &>/dev/null; then
  HAS_PYTHON3=false
  echo "   ⚠️  未找到 python3（EPUB/DOCX 后处理需要）"
fi

if [ "$HAS_NODE" = true ] && [ "$HAS_PLAYWRIGHT" = true ]; then
  echo "   ✅ Node.js + Playwright 就绪（PDF 构建可用）"
fi
if [ "$HAS_PANDOC" = true ] && [ "$HAS_PYTHON3" = true ]; then
  echo "   ✅ pandoc + python3 就绪（DOCX/EPUB 构建可用）"
fi

echo ""
echo "✅ 项目已创建！"
echo ""
echo "   结构:"
echo "   $PROJECT_DIR/"
echo "   ├── README.md / PROJECT.md          # 项目说明 + 详细规划"
echo "   ├── placeholder-config.json         # 占位符配置（替换自己的信息）"
echo "   ├── styles.css / build.js / build-pdf.js / update.sh"
echo "   ├── version.json / CHANGELOG.md"
echo "   ├── fragments/                      # HTML 片段（在这里写内容）"
echo "   ├── research/                       # 调研资料"
echo "   ├── output/                         # 构建输出"
echo "   ├── 封面/                           # 封面设计稿"
echo "   └── versions/                       # 历史 PDF 存档"
echo ""
echo "   下一步:"
echo "   1. 编辑 placeholder-config.json 替换为自己的信息"
echo "   2. 编辑 PROJECT.md 填写大纲"
echo "   3. 编辑 build.js 中的 FRAGMENT_ORDER"
echo "   4. 在 fragments/ 下写 HTML 片段（先读 references/design-system.md）"
echo "   5. ./update.sh 重建 PDF"
