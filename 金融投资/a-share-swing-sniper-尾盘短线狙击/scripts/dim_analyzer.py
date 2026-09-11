#!/usr/bin/env python3
"""
4 维度分析（板块 × 资金 × 基本面 × 消息面）

用法:
    python3 dim_analyzer.py --code 600522 --name 中天科技
"""
import argparse
import sys
import time
from datetime import datetime

import pandas as pd

try:
    import akshare as ak
except ImportError:
    print("❌ 缺依赖: pip install akshare")
    sys.exit(1)


# ============== 4 维度阈值 ==============
# 资金面
FUND_5D_NET_INFLOW_MIN = 0          # 5 日主力净流入 > 0
FUND_5D_SUPER_BUY_MIN = 0           # 5 日超大单净买入 > 0
FUND_VOLUME_RATIO_MIN = 1.5         # 量比 > 1.5
FUND_TURNOVER_MIN = 5.0             # 换手率 > 5%
FUND_TURNOVER_MAX = 10.0            # 换手率 < 10%
FUND_POSITION_RATIO_MIN = 5.0       # 主力增仓占比 > 5%

# 基本面
FUNDAMENTAL_REVENUE_GROWTH_MIN = 20  # 营收增速 > 20%
FUNDAMENTAL_PROFIT_GROWTH_MIN = 30   # 净利增速 > 30%

# 消息面
NEWS_ANNOUNCEMENT = ['业绩预增', '订单', '产能', '重组', '中标', '回购', '股权激励']


def score_sector(code, name):
    """维度 1: 板块景气度"""
    try:
        # 拉行业板块涨跌幅，看个股所在板块
        df_industry = ak.stock_board_industry_summary_ths()
        # 简单按名称匹配行业
        # 这里简化：返回 1（具体行业景气度需要 web_search 验证）
        return 1, f"行业: 待核实 (代码 {code})"
    except Exception as e:
        return 0, f"板块数据获取失败: {e}"


def score_capital(code):
    """维度 2: 资金面（权重最高）"""
    score = 0
    details = []

    try:
        # 1. 5 日主力净流入
        df_fund = ak.stock_individual_fund_flow(stock=code, market='sh' if code.startswith('6') else 'sz')
        if df_fund is not None and len(df_fund) >= 5:
            net_5d = df_fund['主力净流入净额'].tail(5).sum() / 1e8  # 转为亿
            if net_5d > FUND_5D_NET_INFLOW_MIN:
                score += 1
                details.append(f"✅ 5 日主力净流入 {net_5d:+.2f} 亿")
            else:
                details.append(f"❌ 5 日主力净流入 {net_5d:+.2f} 亿 (≤ 0)")
        time.sleep(0.5)

        # 2. 5 日超大单净买入
        if df_fund is not None and len(df_fund) >= 5 and '超大单净流入净额' in df_fund.columns:
            super_5d = df_fund['超大单净流入净额'].tail(5).sum() / 1e8
            if super_5d > FUND_5D_SUPER_BUY_MIN:
                score += 1
                details.append(f"✅ 5 日超大单 {super_5d:+.2f} 亿")
            else:
                details.append(f"❌ 5 日超大单 {super_5d:+.2f} 亿 (≤ 0)")
        time.sleep(0.5)

        # 3. 量比 + 换手率
        df_spot = ak.stock_zh_a_spot_em()
        stock = df_spot[df_spot['代码'] == code]
        if not stock.empty:
            volume_ratio = stock.iloc[0].get('量比', 0)
            turnover = stock.iloc[0].get('换手率', 0)
            if volume_ratio > FUND_VOLUME_RATIO_MIN:
                score += 1
                details.append(f"✅ 量比 {volume_ratio:.2f} (> {FUND_VOLUME_RATIO_MIN})")
            else:
                details.append(f"❌ 量比 {volume_ratio:.2f} (≤ {FUND_VOLUME_RATIO_MIN})")
            if FUND_TURNOVER_MIN < turnover < FUND_TURNOVER_MAX:
                score += 1
                details.append(f"✅ 换手率 {turnover:.2f}% (5-10%)")
            else:
                details.append(f"❌ 换手率 {turnover:.2f}% (不在 5-10%)")
        time.sleep(0.5)

    except Exception as e:
        details.append(f"⚠️  资金面数据获取失败: {e}")

    return 1 if score >= 3 else 0, " / ".join(details)


def score_fundamental(code):
    """维度 3: 基本面"""
    try:
        # 拉财务摘要
        df_fin = ak.stock_financial_abstract(symbol=code)
        if df_fin is None or df_fin.empty:
            return 0, "❌ 财务数据为空"

        # 取最新一期的营收增速 + 净利增速
        latest = df_fin.iloc[-1]
        rev_growth = latest.get('营业总收入同比', 0)
        profit_growth = latest.get('归属母公司净利润同比', 0)

        score = 0
        details = []
        if rev_growth > FUNDAMENTAL_REVENUE_GROWTH_MIN:
            score += 1
            details.append(f"✅ 营收增速 {rev_growth:+.2f}%")
        else:
            details.append(f"❌ 营收增速 {rev_growth:+.2f}% (≤ {FUNDAMENTAL_REVENUE_GROWTH_MIN}%)")
        if profit_growth > FUNDAMENTAL_PROFIT_GROWTH_MIN:
            score += 1
            details.append(f"✅ 净利增速 {profit_growth:+.2f}%")
        else:
            details.append(f"❌ 净利增速 {profit_growth:+.2f}% (≤ {FUNDAMENTAL_PROFIT_GROWTH_MIN}%)")

        return 1 if score >= 1 else 0, " / ".join(details)
    except Exception as e:
        return 0, f"⚠️  财务数据获取失败: {e}"


def score_news(code):
    """维度 4: 消息面"""
    try:
        # 拉近期公告
        df_notice = ak.stock_notice_report(symbol=code)
        if df_notice is None or df_notice.empty:
            return 0, "❌ 无近期公告"

        # 看最近 10 条公告是否包含利好关键词
        recent = df_notice.head(10)
        matched = 0
        for kw in NEWS_ANNOUNCEMENT:
            if recent['标题'].str.contains(kw, na=False).any():
                matched += 1

        if matched >= 1:
            return 1, f"✅ 公告含 {matched} 个利好关键词（业绩预增/订单/产能/重组/中标/回购/股权激励）"
        return 0, "❌ 公告无明显利好"
    except Exception as e:
        return 0, f"⚠️  公告数据获取失败: {e}"


def main():
    parser = argparse.ArgumentParser(description='4 维度分析')
    parser.add_argument('--code', required=True, help='股票代码（6 位）')
    parser.add_argument('--name', required=True, help='股票名称')
    args = parser.parse_args()

    print(f"📊 4 维度分析 · {args.name}({args.code}) · {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 70)

    results = {}

    # 维度 1: 板块景气度
    print("\n[1/4] 板块景气度...")
    score, detail = score_sector(args.code, args.name)
    results['板块景气度'] = (score, detail)
    print(f"  {detail}")
    print(f"  评分: {score}/1")
    time.sleep(1)

    # 维度 2: 资金面（★ 最重要）
    print("\n[2/4] 资金面 (★ 权重最高)...")
    score, detail = score_capital(args.code)
    results['资金面'] = (score, detail)
    print(f"  {detail}")
    print(f"  评分: {score}/1")
    time.sleep(1)

    # 维度 3: 基本面
    print("\n[3/4] 基本面...")
    score, detail = score_fundamental(args.code)
    results['基本面'] = (score, detail)
    print(f"  {detail}")
    print(f"  评分: {score}/1")
    time.sleep(1)

    # 维度 4: 消息面
    print("\n[4/4] 消息面...")
    score, detail = score_news(args.code)
    results['消息面'] = (score, detail)
    print(f"  {detail}")
    print(f"  评分: {score}/1")
    time.sleep(0.5)

    # 综合评分
    total = sum(s for s, _ in results.values())
    print(f"\n{'=' * 70}")
    print(f"📈 综合评分: {total}/4")
    print(f"{'=' * 70}")

    if total == 4:
        verdict = "持续行情型 ★"
        suggestion = "重仓 30% × 2 只，持有 3-5 天"
    elif total == 3:
        verdict = "短线冲高型 ★"
        suggestion = "轻仓 20% × 2-3 只，**次日冲高跑路**"
    else:
        verdict = "不建议"
        suggestion = "不操作"

    print(f"  判定: {verdict}")
    print(f"  建议: {suggestion}")
    print()


if __name__ == '__main__':
    main()
