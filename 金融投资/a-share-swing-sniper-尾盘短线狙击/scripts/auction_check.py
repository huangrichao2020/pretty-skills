#!/usr/bin/env python3
"""
竞价信号判断（9:15-9:25 集合竞价）

用法:
    python3 auction_check.py --code 600522
    python3 auction_check.py --code 600522 --prev-close 34.49
"""
import argparse
import sys
import time
from datetime import datetime, timedelta

try:
    import akshare as ak
except ImportError:
    print("❌ 缺依赖: pip install akshare")
    sys.exit(1)


# ============== 3 情景阈值 ==============
GREEN_OPEN_MIN = 3.0          # 乐观开盘价：+3%
GREEN_OPEN_MAX = 5.0          # 乐观开盘价：+5%
YELLOW_OPEN_MIN = -2.0        # 中性开盘价：-2%
RED_OPEN_THRESHOLD = -2.0     # 悲观开盘价：< -2%


def get_yesterday_close(code):
    """获取昨日收盘价"""
    end = datetime.now().strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')
    try:
        df = ak.stock_zh_a_hist(
            symbol=code,
            period='daily',
            start_date=start,
            end_date=end,
            adjust='qfq'
        )
        if df is None or df.empty:
            return None
        return df['收盘'].iloc[-2]  # 昨日
    except Exception as e:
        print(f"⚠️  获取昨日收盘价失败: {e}")
        return None


def get_auction_data(code):
    """
    获取集合竞价数据
    注: akshare 没有直接提供集合竞价数据，这里用 9:30 开盘价作为代理
    实际场景中应该用实时行情 API（如恒生/通达信）
    """
    try:
        df_spot = ak.stock_zh_a_spot_em()
        stock = df_spot[df_spot['代码'] == code]
        if stock.empty:
            return None
        return {
            'open_price': stock.iloc[0].get('今开', 0),
            'current_price': stock.iloc[0].get('最新价', 0),
            'volume_ratio': stock.iloc[0].get('量比', 0),
            'change_pct': stock.iloc[0].get('涨跌幅', 0),
            'main_net_inflow': stock.iloc[0].get('主力净流入', 0),
        }
    except Exception as e:
        print(f"⚠️  获取实时数据失败: {e}")
        return None


def get_recent_main_flow(code, n_days=5):
    """获取近 N 日主力净流入（用于对比竞价阶段）"""
    try:
        df_fund = ak.stock_individual_fund_flow(
            stock=code,
            market='sh' if code.startswith('6') else 'sz'
        )
        if df_fund is None or df_fund.empty:
            return 0
        return df_fund['主力净流入净额'].tail(n_days).sum() / 1e8
    except Exception as e:
        return 0


def determine_scenario(change_pct, volume_ratio, main_net_inflow, prev_close_volume):
    """
    判定 3 情景

    Args:
        change_pct: 开盘价相对昨日收盘的涨跌幅(%)
        volume_ratio: 量比（集合竞价成交量 / 前日同时段）
        main_net_inflow: 竞价阶段主力净流入（亿）
        prev_close_volume: 前日同时段成交量
    """
    # 🟢 乐观
    if (GREEN_OPEN_MIN <= change_pct <= GREEN_OPEN_MAX
            and volume_ratio > 1.0
            and main_net_inflow > 0):
        return '🟢 乐观', '高', '竞价区间分批买入 25-30%'

    # 🔴 悲观
    if change_pct < RED_OPEN_THRESHOLD or (change_pct < 0 and main_net_inflow < 0):
        return '🔴 悲观', '低', '**不买入**，规避大面'

    # 🟡 中性
    return '🟡 中性', '中', '观望 + 等放量突破'


def main():
    parser = argparse.ArgumentParser(description='竞价信号判断（9:15-9:25）')
    parser.add_argument('--code', required=True, help='股票代码（6 位）')
    parser.add_argument('--prev-close', type=float, default=None,
                        help='昨日收盘价（不传则自动拉）')
    args = parser.parse_args()

    now = datetime.now()
    print(f"📊 竞价信号判断 · {args.code} · {now.strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    # 1. 昨日收盘价
    if args.prev_close is None:
        print("\n[1/3] 拉昨日收盘价...")
        prev_close = get_yesterday_close(args.code)
        if prev_close is None:
            print("❌ 无法获取昨日收盘价，请用 --prev-close 手动指定")
            return
    else:
        prev_close = args.prev_close
    print(f"   昨日收盘: {prev_close} 元")

    # 2. 拉集合竞价数据
    print("\n[2/3] 拉集合竞价数据...")
    auction = get_auction_data(args.code)
    if auction is None:
        print("❌ 无法获取集合竞价数据")
        return

    open_price = auction['open_price']
    change_pct = ((open_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
    volume_ratio = auction['volume_ratio']
    main_net_inflow = auction.get('main_net_inflow', 0) / 1e8  # 转为亿

    print(f"   开盘价: {open_price} 元 ({change_pct:+.2f}%)")
    print(f"   量比: {volume_ratio:.2f}")
    print(f"   主力净流入: {main_net_inflow:+.2f} 亿")

    # 3. 判定 3 情景
    print("\n[3/3] 3 情景判断...")
    # 注: 实际场景需要对比"前日同时段成交量"和"竞价阶段成交量"
    # 这里用 volume_ratio 作为代理
    scenario, probability, action = determine_scenario(
        change_pct, volume_ratio, main_net_inflow, None
    )

    print(f"\n{'=' * 70}")
    print(f"📈 判定: {scenario} (冲高概率: {probability})")
    print(f"   建议: {action}")

    # 4. 给出具体操作
    print(f"\n{'=' * 70}")
    print("💡 操作建议")
    print(f"{'=' * 70}")

    if '🟢' in scenario:
        print(f"""
乐观情景操作:
  - 9:20 前:  挂 1/3 仓位 (试探)
  - 9:20-9:23: 加 1/3 仓位 (确认)
  - 9:24-9:25: 加 1/3 仓位 (收尾)
  - 仓位上限: 30% (单只)

⚠️ 9:20 后不能撤单 → 严控仓位
""")
    elif '🟡' in scenario:
        print(f"""
中性情景操作:
  - 9:25-9:30:  不操作, 观察开盘 5 分钟
  - 9:30-9:35:  若放量突破开盘价 + 主力净流入 → 买入 1/2 仓位(12-15%)
  - 9:35 后:    若未突破 → 放弃

⚠️ 中性情景严控仓位 ≤ 15%
""")
    else:  # 悲观
        print(f"""
悲观情景操作:
  - 9:15-9:25:  全部不操作
  - 9:30-9:35:  观察是否修复
  - 9:35 后:    不操作, 放弃

⚠️ 警惕信号:
  - 主力净流出 > 7 亿 + 散户净流入 > 8 亿 (9-4 案例重现)
  - 集合竞价放量但低开 (诱多陷阱)
  - 尾盘最后 3 分钟放量 (高位派发)
""")


if __name__ == '__main__':
    main()
