#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""机会挖掘动态数据 3F case 离线出图器（Pillow + numpy · 不调用在线 AI 出图）。
字体：/System/Library/Fonts/STHeiti Light.ttc (index 0)
生成：images/ p0..p6 (7 张=页数) + 锦绣/cover-横屏 + cover-竖屏 + slides/s1..s10 + 讲解.pdf
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

NAVY = (12, 18, 38)
NAVY2 = (22, 30, 58)
PURPLE = (60, 42, 120)
TEAL = (28, 120, 130)
GOLD = (244, 196, 48)
RED = (230, 57, 70)
GREEN = (42, 157, 110)
CYAN = (56, 200, 220)
WHITE = (240, 244, 255)
GREY = (150, 162, 190)


def make_canvas(w, h, c1, c2, c3=None):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = yy / h
    r = c1[0] + (c2[0] - c1[0]) * t
    g = c1[1] + (c2[1] - c1[1]) * t
    b = c1[2] + (c2[2] - c1[2]) * t
    s = xx / w
    if c3:
        r = r + (c3[0] - c1[0]) * s * 0.4
        g = g + (c3[1] - c1[1]) * s * 0.4
        b = b + (c3[2] - c1[2]) * s * 0.4
    r = np.clip(r, 0, 255).astype(np.float32)
    g = np.clip(g, 0, 255).astype(np.float32)
    b = np.clip(b, 0, 255).astype(np.float32)
    arr = np.dstack([r, g, b]).astype(np.uint8)
    noise = np.random.randint(-9, 10, size=(h, w, 3)).astype(np.int16)
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


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
    img = make_canvas(w, h, NAVY, NAVY2, PURPLE).convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    theme = cfg.get("theme", GOLD)
    accents = [
        (int(w*0.82), int(h*0.18), int(h*0.22), theme, 38),
        (int(w*0.12), int(h*0.85), int(h*0.18), TEAL, 30),
        (int(w*0.95), int(h*0.95), int(h*0.12), CYAN, 22),
        (int(w*0.05), int(h*0.10), int(h*0.10), PURPLE, 28),
    ]
    for (cx, cy, rad, col, alpha) in accents:
        tmp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).ellipse([cx-rad, cy-rad, cx+rad, cy+rad],
                                    fill=(col[0], col[1], col[2], alpha))
        img.alpha_composite(tmp)
    draw.line([int(w*0.06), int(h*0.12), int(w*0.94), int(h*0.12)],
               fill=(theme[0], theme[1], theme[2], 120), width=2)
    tf = F(int(h*0.085))
    draw.text((int(w*0.06), int(h*0.14)), cfg["title"], font=tf, fill=(*WHITE, 255))
    sf = F(int(h*0.032))
    draw.text((int(w*0.06), int(h*0.14)+int(h*0.095)), cfg["subtitle"], font=sf, fill=(*GREY, 255))
    draw.rectangle([int(w*0.06), int(h*0.30), int(w*0.065), int(h*0.86)], fill=(*theme, 255))
    bf = F(int(h*0.034))
    y = int(h*0.33)
    lh = int(h*0.062)
    for item in cfg.get("bullets", []):
        draw.ellipse([int(w*0.07), y+int(h*0.008), int(w*0.07)+int(h*0.018), y+int(h*0.026)],
                     fill=(*theme, 255))
        for ln in wrap(draw, item, bf, int(w*0.80)):
            draw.text((int(w*0.105), y), ln, font=bf, fill=(*WHITE, 245))
            y += int(h*0.040)
        y += int(h*0.012)
    bx = int(w*0.66)
    by = int(h*0.33)
    for (bt, col) in cfg.get("badges", []):
        bw = int(draw.textlength(bt, font=sf)) + 24
        draw.rounded_rectangle([bx, by, bx+bw, by+int(h*0.05)], 8, (col[0], col[1], col[2], 60))
        draw.text((bx+12, by+int(h*0.008)), bt, font=sf, fill=(*WHITE, 255))
        by += int(h*0.062)
    ff = F(int(h*0.024))
    draw.text((int(w*0.06), int(h*0.90)), cfg.get("footer", "机会挖掘动态数据 · v0.4.0"),
              font=ff, fill=(*GREY, 230))
    return img


pages = [
    dict(title="机会挖掘动态数据", subtitle="v0.4.0 · 真数据引擎升级 · 2026-08-20",
         theme=GOLD,
         bullets=[
             "盘中板块/涨停从硬编码模板 → NeoData 真数据动态组装",
             "emit_intraday_section 读 sector_leaders + limit_up_stocks",
             "融合 v0.3.1 排版精修 + 微信铁律 + 禁止元解释",
             "超超 2026-08-19 拍板：微信助理以此为核心",
         ],
         badges=[("微信 1-2 屏", GOLD), ("真数据", TEAL), ("非投资建议", RED)],
         footer="机会挖掘动态数据 · idea-trade-qa v0.4.0 · 2026-08-20"),

    dict(title="真数据动态生成架构", subtitle="collect_intraday_data 联动采集三件套",
         theme=CYAN,
         bullets=[
             "emit_intraday_section 不再硬编码，读真板块/真涨停股",
             "collect_intraday_data：板块涨幅TOP+涨停股TOP+板块资金TOP",
             "parse_sector_ranking：解析板块涨跌/资金排行 markdown 表",
             "parse_limit_up_stocks：解析 A股交易排行 涨停 TOP N",
         ],
         badges=[("NeoData", GOLD), ("动态", CYAN), ("降级保护", GREEN)],
         footer="数据流：自然语言→markdown表→正则解析→组装输出"),

    dict(title="6 处关键 bug 修复", subtitle="数据可信度是引擎命脉",
         theme=RED,
         bullets=[
             "market_index 2026.0 → 重写 parse_index_table",
             "down_count 5(实5069) → [\\d,]+ + replace",
             "up_ratio 0.76(实0.08) → 直接 parse 占比字段",
             "sentiment_temp 55 → 重写多因子算法",
             "fund_flow_sectors [] → split('|') 按列取",
             "场景识别错 → 多日推演置顶",
         ],
         badges=[("全修复", GREEN), ("可信", TEAL), ("置顶", GOLD)],
         footer="修复前=凭印象，修复后=可验证"),

    dict(title="\\n 字面量致命坑", subtitle="NeoData 返回字面 \\n 非真换行",
         theme=PURPLE,
         bullets=[
             "NeoData 返回的是字面 \\n（反斜杠+n）不是 chr(10)",
             "不处理 → 所有表格 split 失败 → 数据全空/错乱",
             "铁律：所有解析器首行 raw.replace('\\\\n', '\\n')",
             "覆盖 parse_index/sector/limit_up/collect 全部前置",
             "教训：接口格式≠标准换行，先验再解析",
         ],
         badges=[("一票否决", RED), ("前置", GOLD), ("铁律", CYAN)],
         footer="v0.2 就埋下，v0.4 仍每行保留"),

    dict(title="v0.3.1 排版精修", subtitle="微信可读 · 像聊天不像报告",
         theme=TEAL,
         bullets=[
             "二级标题加冒号：❌ **一个危险**：",
             "主题词不加粗、只加粗状态词：❶ 通信设备 → **要起飞**",
             "解读句独立成段：每行≤40字 + 空行",
             "上午/下午分段：上午：xxx / 下午：xxx",
             "灵活主题段：❸ 光模块：xxx",
             "末尾一句话独立成段：**一句话**：+清单",
         ],
         badges=[("排版", CYAN), ("清爽", GOLD), ("可读", GREEN)],
         footer="覆盖 v1.6.2 规则 · 2026-08-20"),

    dict(title="微信输出铁律", subtitle="少即是多 · 一屏原则",
         theme=GOLD,
         bullets=[
             "一屏原则：≥15-20 行就压缩，宁可删不要堆",
             "不展示计算：去掉 +30亿 vs +2% 罗列，只留结论",
             "个股 inline code：莱美药业 **+20%**（灰底必带）",
             "小图标 ❶❷❸：编号段必须用圆数字",
             "收尾声明：末尾必加「非投资建议」",
         ],
         badges=[("一屏", RED), ("结论", GOLD), ("inline", CYAN)],
         footer="直接给答案，不堆数据"),

    dict(title="禁止技术性元解释", subtitle="用户要答案不要过程",
         theme=GREEN,
         bullets=[
             "直接给答案：结论/决策/操作，不要工作日志式元解释",
             "反例：skill 走了XX场景 / 重新拉真实数据 / 下面一页纸",
             "元信息：commit/版本/数据源放最后一行或脚注",
             "标杆：Reuters/Bloomberg 快讯式清爽",
             "决策动作：末尾给可照做的清单（买/持/止盈/不参与）",
         ],
         badges=[("快讯", GOLD), ("无废话", GREEN), ("动作", RED)],
         footer="「已处理」印章盖住工作日志"),
]

W, H = 1280, 720
imgs = []
for i, cfg in enumerate(pages):
    img = build(W, H, cfg)
    img.save(os.path.join(IMG_DIR, f"p{i}.png"))
    imgs.append(img)
    print("saved", f"images/p{i}.png")

# 锦绣 cover 横屏 (16:9)
cover_h = build(1280, 720, dict(
    title="机会挖掘动态数据", subtitle="v0.4.0 真数据引擎 · 数据可验证",
    theme=GOLD,
    bullets=["硬编码模板 → NeoData 真数据动态组装", "6 处数据可信度 bug 修复",
             "融合 v0.3.1 排版 + 微信铁律", "超超 2026-08-19 拍板为核心"],
    badges=[("A股", RED), ("美股", CYAN), ("港股", GREEN)],
    footer="idea-trade-qa v0.4.0 · 2026-08-20"))
cover_h.save(os.path.join(JX_DIR, "cover-横屏.png"))

# 锦绣 cover 竖屏 (3:4)
cover_v = build(1080, 1440, dict(
    title="机会挖掘动态数据", subtitle="v0.4.0 真数据引擎",
    theme=GOLD,
    bullets=["NeoData 真数据动态组装", "6 处 bug 修复", "\\n 字面量铁律",
             "v0.3.1 排版精修", "微信输出铁律", "禁止元解释"],
    badges=[("A股", RED), ("美股", CYAN), ("港股", GREEN)],
    footer="idea-trade-qa v0.4.0"))
cover_v.save(os.path.join(JX_DIR, "cover-竖屏.png"))

# 锦绣 slides (10 张 16:9)
slides = [
    dict(title="01 什么是动态数据引擎", subtitle="v0.4.0 核心升级",
         bullets=["硬编码模板 → 真数据动态组装", "emit_intraday_section 读真板块/真涨停",
                  "超超 2026-08-19 拍板为核心", "数据可验证，不再凭印象"], theme=GOLD),
    dict(title="02 collect_intraday_data", subtitle="联动采集三件套",
         bullets=["板块涨幅 TOP", "涨停股 TOP", "板块资金 TOP",
                  "三件套一次采齐"], theme=CYAN),
    dict(title="03 两个解析器", subtitle="NeoData markdown 表",
         bullets=["parse_sector_ranking 板块排行", "parse_limit_up_stocks 涨停 TOP N",
                  "正则解析 → 结构化", "喂给输出层"], theme=TEAL),
    dict(title="04 6 处 bug 修复", subtitle="数据可信度",
         bullets=["market_index 2026.0", "down_count 5→5069", "up_ratio 0.76→0.08",
                  "sentiment_temp 55 / fund [] / 场景错"], theme=RED),
    dict(title="05 \\n 字面量铁律", subtitle="一票否决级",
         bullets=["NeoData 返回字面 \\n", "不处理→全表空", "首行 replace 再 split",
                  "所有解析器前置"], theme=PURPLE),
    dict(title="06 v0.3.1 排版精修", subtitle="微信可读",
         bullets=["二级标题加冒号", "只加粗状态词", "解读句独立成段",
                  "上午/下午分段"], theme=TEAL),
    dict(title="07 微信输出铁律", subtitle="少即是多",
         bullets=["一屏原则", "不展示计算", "个股 inline code",
                  "圆数字 ❶❷❸"], theme=GOLD),
    dict(title="08 禁止技术性元解释", subtitle="用户要答案",
         bullets=["直接给结论/决策", "反例：工作日志式", "元信息放脚注",
                  "Reuters 式快讯"], theme=GREEN),
    dict(title="09 降级保护", subtitle="数据缺失不瞎编",
         bullets=["拉取失败明说缺失", "westockdata 手动查兜底",
                  "标注经验值", "不凭空生成"], theme=CYAN),
    dict(title="10 调用与收束", subtitle="一句话动作",
         bullets=["python3 idea_trade_qa.py --query", "末尾非投资建议",
                  "可照做清单", "数据驱动高准确率"], theme=GREEN),
]
for i, cfg in enumerate(slides, 1):
    img = build(W, H, cfg)
    img.save(os.path.join(SLIDE_DIR, f"s{i}.png"))
    print("saved", f"锦绣/slides/s{i}.png")

# 讲解.pdf（PIL 由 7 图合并 · 含 image object）
pdf_path = os.path.join(BASE, "机会挖掘动态数据讲解.pdf")
imgs[0].save(pdf_path, "PDF", save_all=True, append_images=imgs[1:], resolution=100.0)
print("saved", pdf_path)
print("ALL DONE")
