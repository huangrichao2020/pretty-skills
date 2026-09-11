#!/bin/bash
#
# swing-sniper 定时运行脚本
# 9-14 周一 9:35 触发：跑 7 条件选股 + 写结果 + 弹 macOS 通知
#
set -e

# 显式清代理（launchd 环境下默认走代理，但东财限流时代理会 RST）
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY

# 路径
SKILL_DIR="/Users/tingchi/.mavis/knowledge/pretty-skills/金融投资/a-share-swing-sniper-尾盘短线狙击"
WORK_DIR="/Users/tingchi/.mavis/sessions/mvs_68a3ee544b6b4afb887fa76445e8ab99/workspace"
LOG="/tmp/swing-sniper-2026-09-14.log"
RESULT_CSV="/tmp/swing-sniper-candidates-2026-09-14.csv"
RUN_DATE=$(date +%Y-%m-%d)
RUN_TIME=$(date +%H:%M:%S)

echo "========================================" > "$LOG"
echo "🚀 swing-sniper 定时任务 · ${RUN_DATE} ${RUN_TIME}" >> "$LOG"
echo "========================================" >> "$LOG"

# 1. 跑 7 条件选股
cd "$SKILL_DIR"
echo "" >> "$LOG"
echo "[1/3] 跑 7 条件选股..." >> "$LOG"
if /opt/homebrew/bin/python3 scripts/stock_filter.py --date "$RUN_DATE" --limit 5 --output "$RESULT_CSV" >> "$LOG" 2>&1; then
    STATUS="✅ 成功"
else
    STATUS="❌ 失败（看 log）"
fi
echo "  状态: $STATUS" >> "$LOG"

# 2. 读结果
echo "" >> "$LOG"
echo "[2/3] 读取结果..." >> "$LOG"
if [ -f "$RESULT_CSV" ]; then
    CANDIDATES=$(head -10 "$RESULT_CSV" | tail -8)
    echo "  结果预览:" >> "$LOG"
    echo "$CANDIDATES" >> "$LOG"
else
    CANDIDATES="（无结果）"
    echo "  ❌ 结果文件未生成" >> "$LOG"
fi

# 3. 复制结果到工作区（让 Mavis 看到）
echo "" >> "$LOG"
echo "[3/3] 复制结果到工作区..." >> "$LOG"
mkdir -p "$WORK_DIR/results"
cp "$RESULT_CSV" "$WORK_DIR/results/candidates-${RUN_DATE}.csv" 2>/dev/null && echo "  ✅ 已复制" >> "$LOG" || echo "  ❌ 复制失败" >> "$LOG"

# 4. 弹 macOS 通知
NOTIF_TITLE="Mavis · 9-14 9:35 7 条件选股"
NOTIF_BODY="${STATUS} · 结果见 ${RESULT_CSV}"
osascript -e "display notification \"${NOTIF_BODY}\" with title \"${NOTIF_TITLE}\" subtitle \"点击查看\"" 2>> "$LOG"

# 5. 写 done 标记
touch /tmp/swing-sniper-2026-09-14.done

echo "" >> "$LOG"
echo "✅ 完成: ${RUN_DATE} ${RUN_TIME}" >> "$LOG"
echo "========================================" >> "$LOG"
