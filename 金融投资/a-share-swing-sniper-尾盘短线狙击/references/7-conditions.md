# 7 条件选股法（筹码分歧回补型 · 核心）

> **核心形态**："缩量企稳 + 放量回补"——昨日缩量说明卖盘枯竭，今日放量说明资金重新介入，涨幅克制说明资金以吸筹为主而非情绪炒作。

## 一、7 条件硬阈值

| # | 条件 | 阈值 | 含义 | 不满足 → 操作 |
|---|------|------|------|--------------|
| 1 | 前日获利比例 | **> 50%** | 中期筹码偏强 | 排除（纯弱势股）|
| 2 | 昨日获利比例 | **< 50%** | 短线获利盘出逃 | 排除（无分歧）|
| 3 | 昨日成交量 | **< 5 日最大 × 50%** | 卖盘枯竭 | 排除（抛压未释放）|
| 4 | 今日获利比例 | **> 50%** | 资金重新介入 | 排除（资金未回补）|
| 5 | 今日放量 | **是**（今日量 > 昨日量 × 1.2）| 资金真实介入 | 排除（缩量 = 没真买）|
| 6 | 今日涨幅 | **≤ 7%** | 涨幅克制 | 排除（涨停买不进去）|
| 7 | 板块 | **主板**（沪 60/00/30 + 深 00）| 流动性好 | 排除（科创/北交所/创业板 20cm 风险）|

**任一不满足 → 排除（不打折）**

## 二、形态示意

```
         昨日                 今日
前日:  ████████ (chip>50%)    ████ (chip<50%)    ████████ (chip>50%)
      缩量(卖盘枯竭)         放量(资金回补)

具体路径:
  Day-2: chip=55%, 涨 3%      → 中期筹码偏强(过滤)
  Day-1: chip=35%, 缩量 40%   → 短线获利盘出逃,卖盘枯竭(制造分歧)
  Day-0: chip=60%, 放量 1.5x, 涨 5%   → 资金回补,涨幅克制(吸筹)
```

## 三、为什么是这 7 条？

想象一个鸡尾酒会：
- **前天**——大家都聊得很开心，气氛很好（前日 chip > 50%）
- **昨天**——有人突然离场，气氛有点尴尬（昨日 chip < 50%，缩量 = 没人接盘）
- **今天**——主角（主力）重新登场，带着新朋友（资金）加入，气氛又热闹起来（今日 chip > 50%，放量）
- **而且**——主角的加入不是表演，涨得不夸张（涨幅 ≤ 7%）

**这种"恢复热闹"的过程，大概率会持续到明天。**

**但要警惕**：昨天离场的人没回来，主角也没来，只是几个喝醉的人在角落自嗨（放量滞涨 + 主力净流出 + 散户接盘）—— 9-4 大面案例就是这种"假热闹"。

## 四、执行流程（3 步）

### Step 1: 拉数据 + 7 条件筛选

```python
import akshare as ak
import pandas as pd

# 1. 拉全市场实时行情
df_spot = ak.stock_zh_a_spot_em()

# 2. 主板过滤
df_spot = df_spot[df_spot['代码'].str.startswith(('60', '00', '30'))]

# 3. 涨幅 ≤ 7% 过滤
df_spot = df_spot[df_spot['涨跌幅'] <= 7.0]

# 4. 排除涨停板（涨跌幅 ≥ 9.95%）
df_spot = df_spot[df_spot['涨跌幅'] < 9.95]
```

### Step 2: 拉 5 日 K 线算昨日缩量

```python
def check_yesterday_shrink(code, n_days=5):
    """检查昨日成交量是否 < 5 日最大 × 50%"""
    end = datetime.now().strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=n_days*2)).strftime('%Y%m%d')

    df = ak.stock_zh_a_hist(symbol=code, period='daily',
                              start_date=start, end_date=end, adjust='qfq')
    if df.empty or len(df) < n_days:
        return False

    max_5d = df['成交量'].tail(n_days).max()
    yesterday_vol = df['成交量'].iloc[-2]  # 昨日（不包含今日）

    return yesterday_vol < max_5d * 0.5
```

### Step 3: 拉筹码分布算 chip

```python
def get_chip_status(code):
    """获取最近 3 天的获利比例（前日 / 昨日 / 今日）"""
    df = ak.stock_cyq_em(symbol=code)
    if df.empty or len(df) < 3:
        return None

    return {
        '前日_chip': df['获利比例'].iloc[-3],
        '昨日_chip': df['获利比例'].iloc[-2],
        '今日_chip': df['获利比例'].iloc[-1],
    }
```

### Step 4: 7 条件整合筛选

```python
def filter_7_conditions(stock):
    """对单只股票套 7 条件筛选"""
    code = stock['代码']

    # 1. 涨幅 ≤ 7%（前置已过滤）
    if stock['涨跌幅'] > 7.0:
        return False

    # 2. 主板（前置已过滤）
    if not code.startswith(('60', '00', '30')):
        return False

    # 3. 昨日缩量
    if not check_yesterday_shrink(code):
        return False

    # 4. 今日放量
    end = datetime.now().strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
    df = ak.stock_zh_a_hist(symbol=code, period='daily',
                              start_date=start, end_date=end, adjust='qfq')
    if df.empty or len(df) < 2:
        return False
    if df['成交量'].iloc[-1] <= df['成交量'].iloc[-2] * 1.2:
        return False

    # 5-7. 筹码 3 天 chip 满足
    chip = get_chip_status(code)
    if chip is None:
        return False
    if not (chip['前日_chip'] > 50 and chip['昨日_chip'] < 50 and chip['今日_chip'] > 50):
        return False

    return True
```

### Step 5: 按资金面排序

```python
def sort_by_capital_flow(df_candidates, top_n=5):
    """按资金面 + 量比 + 换手率 + 流通市值排序"""
    df_candidates['score'] = (
        df_candidates['主力净流入'] * 1.0 +       # 主力净流入最大
        df_candidates['量比'] * 0.5 +              # 量比最大
        -abs(df_candidates['换手率'] - 7.5) * 0.1  # 换手率适中(5-10%)
    )
    return df_candidates.nlargest(top_n, 'score')
```

## 五、完整脚本

直接跑：`python3 scripts/stock_filter.py --date 2026-09-11 --limit 5`

输出示例：
```
📊 7 条件筛选结果 · 2026-09-11 收盘
═══════════════════════════════════════════
| 排名 | 代码     | 名称     | 行业 | 涨幅  | 主力净流入 | 量比 | 换手率 |
|------|----------|----------|------|-------|-----------|------|--------|
| 1    | 600522   | 中天科技 | 通信 | +3.57% | +7.85 亿 | 1.63 | 7.78%  |
| 2    | 002465   | 海格通信 | 通信 | +4.20% | +3.20 亿 | 1.80 | 6.50%  |
| 3    | ...      |          |      |       |          |      |        |

✅ Top 5 已生成，下一步: 跑 4 维分析
```

## 六、常见误判

| 误判 | 症状 | 正确做法 |
|------|------|----------|
| 追涨停板 | 看到龙头涨停想买后排 | 涨幅 > 7% 一律排除 |
| 缩量未确认 | 昨日只缩了 10% 就想买 | 严格 < 5 日最大 × 50% |
| chip 数据延迟 | 用 13:00 中间数据判断 | 收盘后（15:00 后）再拉数据 |
| 忽略主板 | 看到 20cm 涨停想追 | 主板 ≤ 7%，其他排除 |
| 排序看错 | 按涨跌幅排序 | 按资金面 + 量比综合排序 |

## 七、口诀

> **前日赚（>50%），昨日亏（<50%），昨日缩（<50% 量），今日赚（>50%），今日放（>1.2x），涨幅克（≤7%），主板稳。**
