#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NeoData令牌刷新 3F case 离线出图器（Pillow + numpy · 不调用在线 AI 出图）。
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

NAVY = (10, 20, 30)
NAVY2 = (16, 32, 44)
PURPLE = (44, 62, 120)
TEAL = (28, 120, 130)
GOLD = (244, 196, 48)
RED = (230, 57, 70)
GREEN = (42, 157, 110)
CYAN = (56, 200, 220)
WHITE = (240, 248, 255)
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
    img = make_canvas(w, h, NAVY, NAVY2, TEAL).convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    theme = cfg.get("theme", CYAN)
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
    draw.text((int(w*0.06), int(h*0.90)), cfg.get("footer", "NeoData 令牌刷新 · 12h"),
              font=ff, fill=(*GREY, 230))
    return img


pages = [
    dict(title="NeoData 令牌刷新", subtitle="12h 过期 · 数据管道鉴权运维 · 2026-08-20",
         theme=CYAN,
         bullets=[
             "token 12h 过期 → skill 走模板降级 → 输出假数据",
             "connect_cloud_service → tempToken → --save-token → 重跑",
             "影响所有调 NeoData 的 agent（机会挖掘等）",
             "实测 2026-08-20 全链路跑通",
         ],
         badges=[("12h", RED), ("降级", GOLD), ("刷新", GREEN)],
         footer="NeoData 令牌刷新 SOP · 2026-08-20"),

    dict(title="失效信号与判定", subtitle="401 但网络通 = token 过期",
         theme=RED,
         bullets=[
             "skill 报「数据拉取失败」/ 输出变模板降级",
             "query.py 直接返回 401 / token invalid",
             "判定：.neodata_token saved_at 超 12h",
             "误判排除：WebSearch 还能用 = 网络正常",
         ],
         badges=[("401", RED), ("12h", GOLD), ("网络OK", GREEN)],
         footer="先排除网络，再判 token"),

    dict(title="刷新 step1 · 拿 tempToken", subtitle="connect_cloud_service 工具",
         theme=GOLD,
         bullets=[
             "调 connect_cloud_service → 返回 tempToken",
             "时效：tempToken 24h 有效（留刷新窗口）",
             "实测：tk_2Q2p3TbahZ4rQmJddSnvK6pr0zAPV8n3",
             "注意：临时凭证，必须立刻落盘才持久",
         ],
         badges=[("24h", GREEN), ("临时", GOLD), ("落盘", CYAN)],
         footer="token 不写缓存 = 白拿"),

    dict(title="刷新 step2 · 写入缓存", subtitle="query.py --save-token",
         theme=TEAL,
         bullets=[
             "命令：query.py --save-token \"<token>\"",
             "落点：SKILLS_DIR/.neodata_token（JSON）",
             "权限：写入时 600，防 token 泄露",
             "校验：重跑 query.py 不带参读到有效 token",
         ],
         badges=[("600", RED), ("落盘", GREEN), ("校验", CYAN)],
         footer="权限 600 防泄露"),

    dict(title="刷新 step3 · 验证", subtitle="重跑 skill 确认真数据",
         theme=GREEN,
         bullets=[
             "python3 idea_trade_qa.py --query \"...\"",
             "预期：出现真实板块/涨停数据",
             "emit_intraday_section 输出真 sector_leaders",
             "兜底：仍失败查 token 复制是否完整",
         ],
         badges=[("真数据", GREEN), ("验证", CYAN), ("闭环", GOLD)],
         footer="验证闭环才算完"),

    dict(title="自动化与监控", subtitle="自愈优于救火",
         theme=PURPLE,
         bullets=[
             "包装脚本：调 NeoData 前自动 detect 过期并刷新",
             "cron 每 11h 跑一次 --save-token",
             "skill 启动先 probe token 有效性，失效即告警",
             "注意：tempToken 24h ≠ 缓存 12h 有效期",
         ],
         badges=[("cron", GOLD), ("probe", CYAN), ("自愈", GREEN)],
         footer="12h 刷新做成定时"),

    dict(title="踩坑与收束", subtitle="别走错路 · 别泄露",
         theme=RED,
         bullets=[
             "别用 gh auth login 修（那是 GitHub 凭证）",
             "别把 .neodata_token 提交到 git（含密钥）",
             "GitHub PAT 与 NeoData token 是两套体系",
             "收尾：重跑验证 + 末尾非投资建议",
         ],
         badges=[("禁 gh", RED), ("禁 git", GOLD), ("独立", CYAN)],
         footer="别混体系、别泄露"),
]

W, H = 1280, 720
imgs = []
for i, cfg in enumerate(pages):
    img = build(W, H, cfg)
    img.save(os.path.join(IMG_DIR, f"p{i}.png"))
    imgs.append(img)
    print("saved", f"images/p{i}.png")

cover_h = build(1280, 720, dict(
    title="NeoData 令牌刷新", subtitle="12h 过期 · 数据管道鉴权运维",
    theme=CYAN,
    bullets=["token 过期→降级→假数据", "connect_cloud_service 拿 token",
             "query.py --save-token 落盘", "重跑验证真数据"],
    badges=[("12h", RED), ("600", GOLD), ("自愈", GREEN)],
    footer="NeoData 令牌刷新 SOP · 2026-08-20"))
cover_h.save(os.path.join(JX_DIR, "cover-横屏.png"))

cover_v = build(1080, 1440, dict(
    title="NeoData 令牌刷新", subtitle="12h 过期鉴权运维",
    theme=CYAN,
    bullets=["401 判定", "tempToken 24h", "--save-token", "重跑验证", "cron 自愈", "禁 git"],
    badges=[("12h", RED), ("600", GOLD), ("自愈", GREEN)],
    footer="NeoData 令牌刷新 SOP"))
cover_v.save(os.path.join(JX_DIR, "cover-竖屏.png"))

slides = [
    dict(title="01 为什么刷", subtitle="12h 过期导致降级",
         bullets=["token 12h 过期", "失效→模板降级", "影响所有 NeoData skill",
                  "2026-08-20 实战"], theme=CYAN),
    dict(title="02 失效判定", subtitle="401 但网络通",
         bullets=["skill 报拉取失败", "query.py 401", "看 saved_at 超 12h",
                  "WebSearch 绿灯=网络正常"], theme=RED),
    dict(title="03 step1 拿 token", subtitle="connect_cloud_service",
         bullets=["返回 tempToken", "24h 有效", "实测 tk_2Q2p...",
                  "临时·要落盘"], theme=GOLD),
    dict(title="04 step2 写缓存", subtitle="query.py --save-token",
         bullets=["写 .neodata_token", "JSON{token,saved_at}", "权限 600",
                  "重跑校验可读"], theme=TEAL),
    dict(title="05 step3 验证", subtitle="重跑确认真数据",
         bullets=["idea_trade_qa.py --query", "真板块/涨停出现", "emit 输出真字段",
                  "兜底查复制完整"], theme=GREEN),
    dict(title="06 自动化", subtitle="自愈优于救火",
         bullets=["包装脚本自动 detect", "cron 每 11h", "启动时 probe",
                  "失效即告警"], theme=PURPLE),
    dict(title="07 踩坑", subtitle="别走错路",
         bullets=["别 gh auth login", "别 git add token", "PAT 与 token 独立",
                  "收尾验证"], theme=RED),
    dict(title="08 影响面", subtitle="谁会中招",
         bullets=["机会挖掘", "板块监控 agent", "任何 NeoData 调用",
                  "金融问答"], theme=CYAN),
    dict(title="09 时效对比", subtitle="tempToken vs 缓存",
         bullets=["tempToken 24h", "缓存 12h 有效期", "别混两套",
                  "留刷新窗口"], theme=TEAL),
    dict(title="10 总结", subtitle="SOP 一句话",
         bullets=["检测→拿 token→落盘", "→验证→自愈",
                  "禁 gh/禁 git", "周期性必做"], theme=GREEN),
]
for i, cfg in enumerate(slides, 1):
    img = build(W, H, cfg)
    img.save(os.path.join(SLIDE_DIR, f"s{i}.png"))
    print("saved", f"锦绣/slides/s{i}.png")

pdf_path = os.path.join(BASE, "NeoData令牌刷新讲解.pdf")
imgs[0].save(pdf_path, "PDF", save_all=True, append_images=imgs[1:], resolution=100.0)
print("saved", pdf_path)
print("ALL DONE")
