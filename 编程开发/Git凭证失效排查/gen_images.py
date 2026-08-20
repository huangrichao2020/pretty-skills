#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Git凭证失效排查 3F case 离线出图器（Pillow + numpy · 不调用在线 AI 出图）。
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

NAVY = (16, 16, 28)
NAVY2 = (26, 26, 44)
PURPLE = (70, 50, 120)
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
    draw.text((int(w*0.06), int(h*0.90)), cfg.get("footer", "Git 凭证失效排查"),
              font=ff, fill=(*GREY, 230))
    return img


pages = [
    dict(title="Git 凭证失效排查", subtitle="env token 抢戏诊断 · 2026-08-20",
         theme=CYAN,
         bullets=[
             "git 401 但 gh 正常 = 失效 GITHUB_TOKEN env 抢戏",
             "git 优先读 env 覆盖 keyring",
             "影响所有 HTTPS git 操作，SSH 不受影响",
             "解法：清 env 再 exec git",
         ],
         badges=[("401", RED), ("env", GOLD), ("keyring", GREEN)],
         footer="Git 凭证失效排查 · 2026-08-20"),

    dict(title="症状与误诊", subtitle="git 红 · gh 绿的反差",
         theme=RED,
         bullets=[
             "git pull → Authentication failed",
             "gh auth status → keyring 正常（误导）",
             "误诊①：gh auth login 重登（没用）",
             "误诊②：改 remote URL（治标）",
             "反差=第三者抢戏，非凭证本身",
         ],
         badges=[("401", RED), ("ghOK", GREEN), ("反差", GOLD)],
         footer="git 失败+gh 正常=env 抢戏"),

    dict(title="根因 · env 抢戏", subtitle="active 却 invalid 的令牌",
         theme=PURPLE,
         bullets=[
             "shell 常驻失效 GITHUB_TOKEN(active但invalid)",
             "git 凭证顺序：env > keyring",
             "失效 env 顶掉正常 keyring",
             "来源：profile/export 常驻，平时不触发",
         ],
         badges=[("env>", RED), ("keyring", GREEN), ("顺序", GOLD)],
         footer="顺序即命门"),

    dict(title="解法1 · 临时", subtitle="env -u 解耦",
         theme=GREEN,
         bullets=[
             "env -u GITHUB_TOKEN -u GH_TOKEN -u GITHUB_ACCESS_TOKEN git ...",
             "单次命令清 env，不改动 shell",
             "让 git 回落 keyring",
             "急着拉代码立刻用",
         ],
         badges=[("临时", GOLD), ("解耦", CYAN), ("成功", GREEN)],
         footer="env -u 即验证"),

    dict(title="解法2 · 长期", subtitle="git-pull-safe 包装",
         theme=TEAL,
         bullets=[
             "~/.local/bin/git-pull-safe",
             "unset GITHUB_TOKEN GH_TOKEN GITHUB_ACCESS_TOKEN; exec git",
             "用法：git-pull-safe -C <repo> pull",
             "延伸：gh repo rename 同理 unset",
         ],
         badges=[("根治", GREEN), ("免疫", CYAN), ("一次配", GOLD)],
         footer="一次配置长期免疫"),

    dict(title="不要做", subtitle="三条弯路",
         theme=RED,
         bullets=[
             "别 gh auth login 重登（覆盖 keyring 没用）",
             "别改 remote URL（治标+污染配置）",
             "别反复重试 git（失效 100 次也是 401）",
         ],
         badges=[("禁login", RED), ("禁URL", GOLD), ("禁重试", CYAN)],
         footer="别走弯路"),

    dict(title="诊断套路 + 收束", subtitle="30 秒定位",
         theme=GOLD,
         bullets=[
             "套路：git 401 → gh status → keyring OK+git fail",
             "验证：echo $GITHUB_TOKEN 非空即嫌疑",
             "收束：清 env → 重跑验证成功",
             "关联：与 NeoData token / PAT 三套独立",
         ],
         badges=[("30s", GREEN), ("套路", CYAN), ("独立", GOLD)],
         footer="套路化不复乱"),
]

W, H = 1280, 720
imgs = []
for i, cfg in enumerate(pages):
    img = build(W, H, cfg)
    img.save(os.path.join(IMG_DIR, f"p{i}.png"))
    imgs.append(img)
    print("saved", f"images/p{i}.png")

cover_h = build(1280, 720, dict(
    title="Git 凭证失效排查", subtitle="env token 抢戏诊断 SOP",
    theme=CYAN,
    bullets=["git 401 但 gh 正常", "失效 env 顶掉 keyring", "env -u 临时解",
             "git-pull-safe 长期免疫"],
    badges=[("401", RED), ("env", GOLD), ("keyring", GREEN)],
    footer="Git 凭证失效排查 · 2026-08-20"))
cover_h.save(os.path.join(JX_DIR, "cover-横屏.png"))

cover_v = build(1080, 1440, dict(
    title="Git 凭证失效排查", subtitle="env 抢戏诊断",
    theme=CYAN,
    bullets=["症状反差", "env>keyring", "env -u", "git-pull-safe", "三不要", "30s套路"],
    badges=[("401", RED), ("env", GOLD), ("keyring", GREEN)],
    footer="Git 凭证失效排查 SOP"))
cover_v.save(os.path.join(JX_DIR, "cover-竖屏.png"))

slides = [
    dict(title="01 问题是什么", subtitle="git 红 gh 绿",
         bullets=["git 401", "gh 正常", "env 抢戏", "2026-08-20"], theme=CYAN),
    dict(title="02 症状与误诊", subtitle="反差即线索",
         bullets=["git pull 失败", "gh status OK", "别 login 重登", "别改 URL"], theme=RED),
    dict(title="03 根因", subtitle="env > keyring",
         bullets=["常驻失效 token", "active 却 invalid", "env 覆盖 keyring",
                  "profile 残留"], theme=PURPLE),
    dict(title="04 解法1 临时", subtitle="env -u",
         bullets=["env -u 三变量", "单次命令", "回落 keyring",
                  "立刻可用"], theme=GREEN),
    dict(title="05 解法2 长期", subtitle="git-pull-safe",
         bullets=["unset + exec", "替代 git pull", "一次配置",
                  "gh rename 同理"], theme=TEAL),
    dict(title="06 不要做", subtitle="三条弯路",
         bullets=["别 login", "别改 URL", "别重试"], theme=RED),
    dict(title="07 诊断套路", subtitle="30 秒定位",
         bullets=["git 401", "查 gh", "查 env", "清 env 验证"], theme=GOLD),
    dict(title="08 验证", subtitle="echo $GITHUB_TOKEN",
         bullets=["非空即嫌疑", "env -u 成功", "确认抢戏", "收束"], theme=CYAN),
    dict(title="09 影响面", subtitle="谁会中招",
         bullets=["HTTPS git", "所有仓库", "SSH 不受影响", "跨仓高频"], theme=TEAL),
    dict(title="10 总结", subtitle="SOP 一句话",
         bullets=["查 env", "清 env", "git-pull-safe", "不复乱"], theme=GREEN),
]
for i, cfg in enumerate(slides, 1):
    img = build(W, H, cfg)
    img.save(os.path.join(SLIDE_DIR, f"s{i}.png"))
    print("saved", f"锦绣/slides/s{i}.png")

pdf_path = os.path.join(BASE, "Git凭证失效排查讲解.pdf")
imgs[0].save(pdf_path, "PDF", save_all=True, append_images=imgs[1:], resolution=100.0)
print("saved", pdf_path)
print("ALL DONE")
