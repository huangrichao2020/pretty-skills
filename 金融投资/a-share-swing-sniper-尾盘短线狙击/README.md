# a-share-swing-sniper · 尾盘短线狙击

> A 股 14:30 尾盘选股 → 次日冲高跑路 · 4 步法 + 7 条件 + 4 维 + 3 选 1
> 砍掉中长线 / 求是 / SMC 那些不相关的，专心做一件事

## 拿到这个 skill 你能做什么

| 你想做 | 拿到后能怎么用 |
|--------|----------------|
| 14:30 尾盘选股 | `python3 scripts/stock_filter.py` 一键套 7 条件，输出 Top 5 候选 |
| 14:50 4 维分析 | `python3 scripts/dim_analyzer.py --code 600522` 自动算 4 维评分 |
| 次日 9:15 竞价判断 | `python3 scripts/auction_check.py --code 600522` 输出 3 情景判断 |
| 9:30 开盘后监控 | 跟 3 选 1 卖出铁律对比，逐项检查 |
| 复盘 + 风险控制 | 套接盘防御 5 铁律 + 9-4 大面案例 |

## 30 分钟上手

```bash
# 1. 装依赖
pip install akshare pandas numpy

# 2. 14:30 跑 7 条件选股
python3 scripts/stock_filter.py --date 2026-09-11 --limit 5

# 3. 14:50 对候选做 4 维分析
python3 scripts/dim_analyzer.py --code 600522 --name 中天科技

# 4. 次日 9:15 跑竞价信号判断
python3 scripts/auction_check.py --code 600522
```

## 4 步法一览

```
[Step 1 · 14:30 选股]   7 条件筛选 → 排除涨停 → 按资金面排序
[Step 2 · 14:50 分析]   4 维评分 → ≥3 维 = 短线冲高型
[Step 3 · 9:15 竞价]    3 情景判断 → 🟢 买 / 🟡 观望 / 🔴 不买
[Step 4 · 9:30 执行]    买入 OR 3 选 1 卖出 OR 止盈止损
```

## 关键决策点速查

| 触发 | 立即做 |
|------|--------|
| 主力净流出 > 7 亿 + 散户净流入 > 8 亿 | **立即减仓**（9-4 案例）|
| 放量但涨幅 < 1% | **减仓**（主力派发）|
| 收盘价 < 5 日均线 | **减仓**（短线趋势破坏）|
| 主力净流出 > 前日净流入 50% | **减仓**（主力出逃）|
| 高开 5%+ + 竞价量 < 前日 | **警惕诱多** |
| 低开 2%+ + 竞价放量 + 主力净流出 | **不买**（悲观）|
| chip > 85% | **绝对不追**（接刀区）|
| 9-4 / 9-10 主力-散户结构重现 | **立即减仓** |

## 量化疗效

| 维度 | 没有 skill | 用了 skill |
|------|----------|----------|
| 14:30 选股 | 凭感觉 / 看新闻 / 翻研报 1-2 小时 | **7 条件筛选 3 分钟** · 输出 Top 5 |
| 14:50 4 维分析 | 凭记忆 | **4 维评分 5 分钟** · 输出明确操作 |
| 次日 9:15 竞价 | 凭感觉追 | **3 情景判断 1 分钟** · 不追诱多 |
| 风险控制 | 凭运气 / 凭胆量 | **9-4 案例 + 3 选 1 铁律** · 大面预警 |
| 复盘 | 没体系 | **鱼头/身/尾 + 季节×chip 过滤** · 长期复利 |

## 适合 vs 不适合

**适合**：
- 14:30 后想找次日冲高标的
- 持仓需要快速判断"该跑还是该守"
- 想避免接盘（9-4 大面案例）

**不适合**：
- 中长线持有（→ 走卡脖子 / 5 维评分）
- 涨停板首板追入（接盘防御 5 铁律 #1 禁止）
- 20cm 跟风股（创业板/科创板/北交所）
- 大资金（> 1000 万）操作

## 与其他 skill 的关系

| 场景 | 用这个 | 用别的 |
|------|--------|--------|
| 尾盘短线 + 次日跑路 | ✅ | - |
| 中长线 + 主题投资 | ❌ | 卡脖子猎手（5 维评分）|
| 事件驱动 + 中线 | ❌ | stock-orange-book（被本 skill 替代）|
| 涨停股池 + 鱼尾检测 | ⚠️ 辅助 | serenity-stock-choke（产业链）|
| 每日复盘 | ❌ | daily-market-review |
| 持仓诊断 | ❌ | portfolio-diagnosis |

## 详细文档

- [SKILL.md](SKILL.md) — 主入口（4 步法 + 全部硬阈值）
- [references/7-conditions.md](references/7-conditions.md) — 7 条件详解
- [references/4-dim-analysis.md](references/4-dim-analysis.md) — 4 维评分详解
- [references/auction-strategy.md](references/auction-strategy.md) — 竞价 3 情景
- [references/risk-control.md](references/risk-control.md) — 5 铁律 + 鱼头身尾
- [references/9-4-case.md](references/9-4-case.md) — 9-4 大面复盘
- [examples/zhongtian-600522-2026-09-11.md](examples/zhongtian-600522-2026-09-11.md) — 中天科技实战

## 致谢

- short-swing-trade（原 skill，2026-09-11 沉淀）— 4 步法核心
- stock-orange-book（原 skill，15 篇方法论）— 6 路径 / 鱼头身尾 / 季节×chip / 微信快评（部分吸收）
- 9-4 大面案例（用户实战复盘，2026-09-04）
- 中天科技 600522 实战（2026-09-11 收盘示范）

**重要声明**：本 skill 是用户私有方法论，仅供个人实战参考，不构成投资建议。
