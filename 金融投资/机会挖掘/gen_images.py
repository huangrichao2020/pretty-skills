#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""机会挖掘 3F case 离线出图器（Pillow + numpy · 不调用在线 AI 出图）。
字体：/System/Library/Fonts/STHeiti Light.ttc (index 0)
生成：images/ p0..p6 (7 张=页数) + 锦绣/cover-横屏 + cover-竖屏 + slides/s1..s10
保证：16:9 或 3:4 · ≥1024×576 · ≥50KB · 唯一色 ≥800（渐变+噪声±9+装饰形）。
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FONT = "/System/Library/Fonts/STHeiti Light.ttc"
IMG_DIR = os.path.join(BASE, "images")
JX_DIR = os.path.join(BASE, "锦绣")
SLIDE_DIR = os.path.join(JX_DIR, "slides")
for d in (IMG_DIR, JX_DIR, SLIDE_DIR):
    os.makedirs(d, exist_ok=True)

F = lambda sz, idx=0: ImageFont.truetype(FONT, sz, index=idx)

# 配色（金融投资·暗色科技风；A股惯例 涨红 跌绿）
NAVY = (12, 18, 38)
NAVY2 = (22, 30, 58)
PURPLE = (60, 42, 120)
TEAL = (28, 120, 130)
GOLD = (244, 196, 48)
RED = (230, 57, 70)      # 涨
GREEN = (42, 157, 110)   # 跌
CYAN = (56, 200, 220)
WHITE = (240, 244, 255)
GREY = (150, 162, 190)


def make_canvas(w, h, c1, c2, c3=None):
    """渐变底 + 噪声（保证唯一色）"""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = yy / h
    # 双色对角渐变
    r = c1[0] + (c2[0] - c1[0]) * t
    g = c1[1] + (c2[1] - c1[1]) * t
    b = c1[2] + (c2[2] - c1[2]) * t
    # 横向扰动
    s = xx / w
    r = r + (c3[0] - c1[0]) * s * 0.4 if c3 else r
    g = g + (c3[1] - c1[1]) * s * 0.4 if c3 else g
    b = b + (c3[2] - c1[2]) * s * 0.4 if c3 else b
    r = np.clip(r, 0, 255).astype(np.float32)
    g = np.clip(g, 0, 255).astype(np.float32)
    b = np.clip(b, 0, 255).astype(np.float32)
    arr = np.dstack([r, g, b]).astype(np.uint8)
    # 加噪声 ±9（关键：保证唯一色 ≫800）
    noise = np.random.randint(-9, 10, size=(h, w, 3)).astype(np.int16)
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def decorate(draw, w, h, accents):
    """装饰形：半透明圆 + 细线 + 圆角块（增加唯一色与层次）"""
    for (cx, cy, rad, col, alpha) in accents:
        overlay = Image.new("RGB", (w, h), (0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=col)
        base = draw._image if hasattr(draw, "_image") else None
    # 直接在主图上画半透明圆
    for (cx, cy, rad, col, alpha) in accents:
        # 用椭圆+透明度：先画到临时层再合成
        tmp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        td.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                   fill=(col[0], col[1], col[2], alpha))
        img = draw._image
        img.alpha_composite(tmp)


def rrect(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def wrap(draw, text, font, maxw):
    lines = []
    cur = ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        t = cur + ch
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = ch
    if cur:
        lines.append(cur)
    return lines


def build(w, h, cfg):
    """cfg: title, subtitle, bullets(list), footer, theme_color, badges(list of (text,color))"""
    img = make_canvas(w, h, NAVY, NAVY2, PURPLE).convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    theme = cfg.get("theme", GOLD)
    # 装饰
    accents = [
        (int(w*0.82), int(h*0.18), int(h*0.22), theme, 38),
        (int(w*0.12), int(h*0.85), int(h*0.18), TEAL, 30),
        (int(w*0.95), int(h*0.95), int(h*0.12), CYAN, 22),
        (int(w*0.05), int(h*0.10), int(h*0.10), PURPLE, 28),
    ]
    # 用 alpha_composite 合成装饰
    for (cx, cy, rad, col, alpha) in accents:
        tmp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).ellipse([cx-rad, cy-rad, cx+rad, cy+rad],
                                    fill=(col[0], col[1], col[2], alpha))
        img.alpha_composite(tmp)
    # 顶部细线
    draw.line([int(w*0.06), int(h*0.12), int(w*0.94), int(h*0.12)],
               fill=(theme[0], theme[1], theme[2], 120), width=2)

    # 标题
    tf = F(int(h*0.085))
    draw.text((int(w*0.06), int(h*0.14)), cfg["title"], font=tf, fill=(*WHITE, 255))
    # 副标题
    sf = F(int(h*0.032))
    draw.text((int(w*0.06), int(h*0.14)+int(h*0.095)), cfg["subtitle"], font=sf, fill=(*GREY, 255))

    # 左侧竖条
    draw.rectangle([int(w*0.06), int(h*0.30), int(w*0.065), int(h*0.86)], fill=(*theme, 255))

    # bullets
    bf = F(int(h*0.034))
    y = int(h*0.33)
    lh = int(h*0.062)
    for item in cfg.get("bullets", []):
        # 项目符号
        draw.ellipse([int(w*0.07), y+int(h*0.008), int(w*0.07)+int(h*0.018), y+int(h*0.026)],
                     fill=(*theme, 255))
        for ln in wrap(draw, item, bf, int(w*0.80)):
            draw.text((int(w*0.105), y), ln, font=bf, fill=(*WHITE, 245))
            y += int(h*0.040)
        y += int(h*0.012)

    # badges（右侧小标签）
    bx = int(w*0.66)
    by = int(h*0.33)
    for (bt, col) in cfg.get("badges", []):
        bw = int(draw.textlength(bt, font=sf)) + 24
        rrect(draw, [bx, by, bx+bw, by+int(h*0.05)], 8, (col[0], col[1], col[2], 60))
        draw.text((bx+12, by+int(h*0.008)), bt, font=sf, fill=(*WHITE, 255))
        by += int(h*0.062)

    # footer
    ff = F(int(h*0.024))
    draw.text((int(w*0.06), int(h*0.90)), cfg.get("footer", "机会挖掘 · idea-trade-qa · v0.3.0"),
              font=ff, fill=(*GREY, 230))
    return img


# ---- 7 张 base 图 ----
pages = [
    dict(title="机会挖掘", subtitle="微信级股市问答 · v0.3.0 · 8/19 暴跌日实战验证",
         theme=GOLD,
         bullets=[
             "带数据源 + 接盘防御 + 鱼身定位 的股市助手",
             "9 类场景模板 · 5 方法论速查表 · 4 段式输出",
             "A股 / 美股 / 港股 · 数据驱动 · 高准确率",
             "超超 2026-08-19 拍板：微信助理以此为核心",
         ],
         badges=[("微信 1-2 屏", GOLD), ("≤500 字", TEAL), ("非投资建议", RED)],
         footer="机会挖掘 · idea-trade-qa · v0.3.0 · 2026-08-19"),

    dict(title="4 段式输出范式", subtitle="v0.3 排版规范 · ≤500字 · 1-2屏微信可读完",
         theme=CYAN,
         bullets=[
             "判断 / 依据 / 动作 / 风险 · 4 类图标 ⚠️✅❌🟡",
             "每段 ≤3 处加粗（数字 / 关键词 / 股票名）",
             "标的用 inline code： `股票名` `股票名` `股票名`",
             "箭头 → · = 必带；删除标签块 / @源后缀 / 引用块 / 表格",
         ],
         badges=[("判断", RED), ("依据", CYAN), ("动作", GOLD), ("风险", GREEN)],
         footer="methodology/09-layout-spec v1.6.1"),

    dict(title="三通道数据获取", subtitle="没有数据不回答 · 每条判断必标源",
         theme=TEAL,
         bullets=[
             "① NeoData 自然语言：板块涨跌 / 资金流 / 涨停梯队",
             "② westockdata 命令行：K线 / 财务 / 技术指标 / 公告",
             "③ WebSearch 全球消息：美股 / 港股 / 突发新闻",
             "优先级 NeoData → westockdata → WebSearch",
         ],
         badges=[("NeoData", GOLD), ("westockdata", CYAN), ("WebSearch", GREEN)],
         footer="数据缺失 → 明确说缺数据，不瞎编"),

    dict(title="接盘防御 5 铁律", subtitle="决策类回答前置检查 · 触发≥3条不参与",
         theme=RED,
         bullets=[
             "① 不追首板（次日分歧才是介入点）",
             "② 不追板块涨幅前 3（鱼尾诱多）",
             "③ 不接机构减持（7日内减持拉黑）",
             "④ 不抄底无量阴跌（量<20日均60%）",
             "⑤ 不参与 20cm 跟风股（炸板率>60%）",
         ],
         badges=[("0 触发=执行", GREEN), ("1-2 谨慎", GOLD), ("≥3 不参与", RED)],
         footer="接盘防御 = 龙头矩阵 双重过滤 · 胜率 30%→65%"),

    dict(title="鱼身定位", subtitle="每个回答必带 · 鱼头 / 鱼身 / 鱼尾",
         theme=GOLD,
         bullets=[
             "鱼头：底部启动 · 20日≤15% · 买入建仓",
             "鱼身：主升浪中段 · 量价齐升 · 持有+移动止盈",
             "鱼尾：末段加速 · 量比≥1.5 / 换手>15% · 止盈不参与",
             "5 鱼尾信号（量比/换手/振幅/放量滞涨/前3未进）≥3 → 不参与",
         ],
         badges=[("鱼头", GREEN), ("鱼身", GOLD), ("鱼尾", RED)],
         footer="高位放量滞涨 = 5 信号全触发 → 止盈离场"),

    dict(title="龙头矩阵 + 情绪温度", subtitle="个股分三段 · 大盘带温度",
         theme=PURPLE,
         bullets=[
             "🥇 龙头（持有）：涨幅/量能前3 + 业务最纯",
             "🥈 跟风（减仓）：涨幅前10 + 业务相关",
             "🥉 补涨（观望）：涨幅末位 + 业务边缘",
             "情绪温度 6 阶段（冰点→退潮）· 多周期对比 · 量价关系",
         ],
         badges=[("🥇龙头", GOLD), ("🥈跟风", CYAN), ("🥉补涨", GREY), ("温度", RED)],
         footer="今日-20日均 ≥15° → 顶部区域警惕分化"),

    dict(title="9 类场景 + 暴跌日验证", subtitle="2026-08-19 实战判断全准",
         theme=GREEN,
         bullets=[
             "追涨决策 / 次日推演 / 盘中机会 / 多日推演",
             "全球联动 / 持仓解套 / 公告驱动 / 财报埋伏 / 产业链联动",
             "暴跌日实测：严禁参与 / 控仓为主 / 等企稳再判",
             "判断全部精准（基于真实盘面）",
         ],
         badges=[("9 场景", GOLD), ("全准", GREEN), ("实战", RED)],
         footer="python3 idea_trade_qa.py --query \"你的问题\""),
]

W, H = 1280, 720
for i, cfg in enumerate(pages):
    img = build(W, H, cfg)
    img.save(os.path.join(IMG_DIR, f"p{i}.png"))
    print("saved", f"images/p{i}.png")


# ---- 锦绣 cover 横屏 (16:9) ----
cover_h = build(1280, 720, dict(
    title="机会挖掘", subtitle="微信级股市问答 · 数据驱动 · 高准确率",
    theme=GOLD,
    bullets=["带数据源 + 接盘防御 + 鱼身定位 的股市助手",
             "9 类场景 · 5 方法论速查表 · 4 段式输出",
             "超超 2026-08-19 拍板：微信助理以此为核心"],
    badges=[("A股", RED), ("美股", CYAN), ("港股", GREEN)],
    footer="idea-trade-qa · v0.3.0 · 2026-08-19"))
cover_h.save(os.path.join(JX_DIR, "cover-横屏.png"))

# ---- 锦绣 cover 竖屏 (3:4) ----
cover_v = build(1080, 1440, dict(
    title="机会挖掘", subtitle="微信级股市问答",
    theme=GOLD,
    bullets=["数据驱动 · 高准确率", "9 类场景模板", "5 方法论速查表",
             "4 段式输出范式", "接盘防御 + 鱼身定位", "龙头矩阵 + 情绪温度"],
    badges=[("A股", RED), ("美股", CYAN), ("港股", GREEN)],
    footer="idea-trade-qa v0.3.0"))
cover_v.save(os.path.join(JX_DIR, "cover-竖屏.png"))

# ---- 锦绣 slides (10 张 16:9) ----
slides = [
    dict(title="01 机会挖掘是什么", subtitle="微信级股市问答助手",
         bullets=["带数据源+接盘防御+鱼身定位", "基于 idea-to-trade v1.8 方法论",
                  "A股/美股/港股 · 30 秒内回答", "超超 2026-08-19 拍板为核心"],
         theme=GOLD),
    dict(title="02 4 段式输出", subtitle="判断 / 依据 / 动作 / 风险",
         bullets=["每段 ≤3 处加粗", "标的用 inline code", "箭头 → · = 必带",
                  "≤500字 · 1-2屏"], theme=CYAN),
    dict(title="03 v0.3 排版规范", subtitle="methodology/09 v1.6.1",
         bullets=["4 类图标 ⚠️✅❌🟡", "删除标签块/@源后缀/引用块/表格",
                  "数字加粗 + 股票名独立", "末尾「非投资建议」"], theme=TEAL),
    dict(title="04 三通道数据", subtitle="没有数据不回答",
         bullets=["NeoData 自然语言行情", "westockdata 命令行精确",
                  "WebSearch 全球消息", "每条必标源"], theme=TEAL),
    dict(title="05 接盘防御 5 铁律", subtitle="决策类前置检查",
         bullets=["不追首板 / 不追涨幅前3", "不接机构减持", "不抄底无量阴跌",
                  "不参与 20cm 跟风 · ≥3触发不参与"], theme=RED),
    dict(title="06 鱼身定位", subtitle="鱼头 / 鱼身 / 鱼尾",
         bullets=["鱼头买入 · 鱼身持有", "鱼尾止盈不参与",
                  "5 鱼尾信号 ≥3 触发", "高位放量滞涨=全触发"], theme=GOLD),
    dict(title="07 龙头矩阵", subtitle="个股分三段",
         bullets=["🥇龙头 持有 · 涨幅/量能前3", "🥈跟风 减仓 · 业务相关",
                  "🥉补涨 观望 · 业务边缘", "胜率 30%→65%"], theme=PURPLE),
    dict(title="08 情绪温度", subtitle="6 阶段 + 多周期",
         bullets=["冰点→修复→升温→高潮→分化→退潮", "今日/5日/10日/20日均对比",
                  "量价关系必查", "偏离≥15° 警惕分化"], theme=RED),
    dict(title="09 九类场景模板", subtitle="覆盖全交易场景",
         bullets=["追涨/次日/盘中/多日推演", "全球联动/持仓解套",
                  "公告驱动/财报埋伏/产业链联动", "CLI 一键调用"], theme=GREEN),
    dict(title="10 暴跌日实战验证", subtitle="2026-08-19",
         bullets=["暴跌市 → 严禁参与", "盘中恐慌 → 控仓为主",
                  "套牢 → 等反弹再减", "判断全准（真实盘面）"], theme=GREEN),
]
for i, cfg in enumerate(slides, 1):
    img = build(W, H, cfg)
    img.save(os.path.join(SLIDE_DIR, f"s{i}.png"))
    print("saved", f"锦绣/slides/s{i}.png")

print("ALL DONE")
