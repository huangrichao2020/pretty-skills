#!/usr/bin/env python3
"""
7 条件选股（筹码分歧回补型）

用法:
    python3 stock_filter.py --date 2026-09-11 --limit 5
    python3 stock_filter.py --date 2026-09-11 --output candidates.csv
"""
import argparse
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

try:
    import akshare as ak
except ImportError:
    print("❌ 缺依赖: pip install akshare")
    sys.exit(1)


# ============== 7 条件配置 ==============
CHIP_2DAYS_AGO_MIN = 50      # 前日 chip > 50%
CHIP_YESTERDAY_MAX = 50      # 昨日 chip < 50%
CHIP_TODAY_MIN = 50          # 今日 chip > 50%
YESTERDAY_VOL_RATIO_MAX = 0.5  # 昨日量 < 5日最大 × 50%
TODAY_VOL_RATIO_MIN = 1.2    # 今日量 > 昨日量 × 1.2
PRICE_CHANGE_MAX = 7.0       # 涨幅 ≤ 7%
PRICE_CHANGE_LIMIT = 9.95    # 主板涨停 = 9.95%
MAIN_BOARD_PREFIX = ('60', '00', '30')


def fetch_spot():
    """拉全市场实时行情（一次拿，避免循环单只拉被限流）"""
    print("📡 拉全市场实时行情...")
    df = ak.stock_zh_a_spot_em()
    print(f"   ✅ 拿到 {len(df)} 只")
    return df


def filter_main_board(df):
    """过滤主板（沪 60/00/30 + 深 00，排除科创 688/北交所 8/9/创业板 300）"""
    df = df[df['代码'].str.startswith(MAIN_BOARD_PREFIX)]
    return df


def fetch_kline(code, n_days=10):
    """拉单只股票 N 天 K 线"""
    end = datetime.now().strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=n_days * 3)).strftime('%Y%m%d')
    try:
        df = ak.stock_zh_a_hist(
            symbol=code,
            period='daily',
            start_date=start,
            end_date=end,
            adjust='qfq'
        )
        if df.empty:
            return None
        # 统一列名（akshare 返回 "成交量"，加单位判断）
        return df
    except Exception as e:
        # 限流保护
        time.sleep(1)
        return None


def check_volume_condition(code):
    """检查昨日缩量 + 今日放量"""
    df = fetch_kline(code, n_days=10)
    if df is None or len(df) < 6:
        return False, None

    volumes = df['成交量'].tail(10).tolist()
    if len(volumes) < 6:
        return False, None

    # 最后一天是今天
    today_vol = volumes[-1]
    yesterday_vol = volumes[-2]
    max_5d = max(volumes[-6:-1])  # 5 日最大（不含今天）

    # 昨日缩量
    yesterday_shrink = yesterday_vol < max_5d * YESTERDAY_VOL_RATIO_MAX
    # 今日放量
    today_surge = today_vol > yesterday_vol * TODAY_VOL_RATIO_MIN

    return yesterday_shrink and today_surge, {
        'today_vol': today_vol,
        'yesterday_vol': yesterday_vol,
        'max_5d': max_5d,
        'yesterday_ratio': yesterday_vol / max_5d if max_5d > 0 else 0,
    }


def fetch_chip(code):
    """拉单只股票最近 3 天的筹码分布"""
    try:
        df = ak.stock_cyq_em(symbol=code)
        if df.empty or len(df) < 3:
            return None

        # 取最后 3 天的 chip（前日 / 昨日 / 今日）
        chip_2days_ago = df['获利比例'].iloc[-3]
        chip_yesterday = df['获利比例'].iloc[-2]
        chip_today = df['获利比例'].iloc[-1]

        return {
            'chip_2days_ago': chip_2days_ago,
            'chip_yesterday': chip_yesterday,
            'chip_today': chip_today,
        }
    except Exception as e:
        time.sleep(1)
        return None


def check_7_conditions(stock):
    """对单只股票套 7 条件筛选"""
    code = stock['代码']
    name = stock['名称']
    change_pct = stock['涨跌幅']

    # 1. 涨幅 ≤ 7%
    if change_pct > PRICE_CHANGE_MAX:
        return False, None

    # 2. 主板
    if not code.startswith(MAIN_BOARD_PREFIX):
        return False, None

    # 3. 排除涨停板
    if change_pct >= PRICE_CHANGE_LIMIT:
        return False, None

    # 4. 成交量条件（昨日缩量 + 今日放量）
    vol_ok, vol_data = check_volume_condition(code)
    if not vol_ok:
        return False, None

    # 5-7. 筹码 3 天 chip 满足
    chip = fetch_chip(code)
    if chip is None:
        return False, None

    if not (chip['chip_2days_ago'] > CHIP_2DAYS_AGO_MIN
            and chip['chip_yesterday'] < CHIP_YESTERDAY_MAX
            and chip['chip_today'] > CHIP_TODAY_MIN):
        return False, None

    # 全部通过
    return True, {
        'vol_data': vol_data,
        'chip': chip,
    }


def main():
    parser = argparse.ArgumentParser(description='7 条件选股（筹码分歧回补型）')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'),
                        help='筛选日期（默认今天）')
    parser.add_argument('--limit', type=int, default=10,
                        help='输出 Top N（默认 10）')
    parser.add_argument('--output', default=None,
                        help='输出 CSV 文件路径（可选）')
    args = parser.parse_args()

    print(f"📊 7 条件筛选 · {args.date}")
    print("=" * 50)

    # 1. 拉全市场
    df_spot = fetch_spot()
    df_spot = filter_main_board(df_spot)
    print(f"   主板过滤后: {len(df_spot)} 只")

    # 2. 涨幅前置过滤（涨幅 ≤ 7% + 排除涨停）
    df_spot = df_spot[df_spot['涨跌幅'] <= PRICE_CHANGE_MAX]
    df_spot = df_spot[df_spot['涨跌幅'] < PRICE_CHANGE_LIMIT]
    print(f"   涨幅 ≤ 7% 过滤后: {len(df_spot)} 只")

    # 3. 逐只套 7 条件
    print(f"\n🔍 逐只套 7 条件...")
    candidates = []
    total = len(df_spot)
    for i, (_, stock) in enumerate(df_spot.iterrows(), 1):
        if i % 50 == 0:
            print(f"   进度: {i}/{total}")
        passed, data = check_7_conditions(stock)
        if passed:
            candidates.append({
                '代码': stock['代码'],
                '名称': stock['名称'],
                '行业': stock.get('行业', 'N/A'),
                '涨跌幅': stock['涨跌幅'],
                '最新价': stock.get('最新价', 0),
                '量比': stock.get('量比', 0),
                '换手率': stock.get('换手率', 0),
                '流通市值': stock.get('流通市值', 0),
                'chip_前日': data['chip']['chip_2days_ago'],
                'chip_昨日': data['chip']['chip_yesterday'],
                'chip_今日': data['chip']['chip_today'],
                '昨日量比': data['vol_data']['yesterday_ratio'],
            })
            # 限流保护
            time.sleep(0.5)

    print(f"\n   ✅ 7 条件全部满足: {len(candidates)} 只")

    # 4. 按资金面排序（量比 + 换手率 + 流通市值）
    if candidates:
        df_candidates = pd.DataFrame(candidates)
        df_candidates['score'] = (
            df_candidates['量比'] * 1.0
            - abs(df_candidates['换手率'] - 7.5) * 0.1
            + df_candidates['流通市值'] / 1e10  # 流通市值（亿）加分
        )
        df_candidates = df_candidates.sort_values('score', ascending=False)
        df_candidates = df_candidates.head(args.limit)

    # 5. 输出
    if not candidates:
        print("\n❌ 没有满足 7 条件的标的")
        return

    print(f"\n📈 Top {min(args.limit, len(df_candidates))} 候选标的")
    print("=" * 90)
    print(f"{'排名':<4} {'代码':<8} {'名称':<8} {'行业':<10} {'涨幅':<8} {'量比':<6} {'换手率':<8} {'chip今':<8}")
    print("-" * 90)
    for i, row in df_candidates.iterrows():
        print(f"{df_candidates.index.get_loc(i)+1:<4} "
              f"{row['代码']:<8} {row['名称']:<8} {row['行业']:<10} "
              f"{row['涨跌幅']:>+6.2f}% {row['量比']:>5.2f}  "
              f"{row['换手率']:>5.2f}%  {row['chip_今日']:>5.1f}%")

    if args.output:
        df_candidates.to_csv(args.output, index=False, encoding='utf-8-sig')
        print(f"\n💾 已保存到: {args.output}")

    print(f"\n✅ 下一步: 跑 4 维分析")
    print(f"   python3 dim_analyzer.py --code {df_candidates.iloc[0]['代码']} --name {df_candidates.iloc[0]['名称']}")


if __name__ == '__main__':
    main()
