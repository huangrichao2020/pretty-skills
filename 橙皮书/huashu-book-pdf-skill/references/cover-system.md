# 封面系统参考 · 企鹅三段式

橙皮书系列的视觉标识。**企鹅出版社经典三段式布局**，让任意一本书都一眼可识别为这个系列。

## 布局规范（严格遵守）

```
┌─────────────────────────┐
│    焦橙色 #C4531A        │  30% — 书名（白色大字）+ 「橙皮书」
├─────────────────────────┤
│    米白底 #F5F0E8         │  45% — 手绘墨水插画 + 副标题（灰色小字）
├─────────────────────────┤
│    焦橙色 #C4531A        │  25% — 「{作者名} 著」（白色居中）
└─────────────────────────┘
```

## 关键参数

| 项 | 值 |
|----|----|
| 比例 | 竖版 3:4（绝对不要正方形） |
| 主色 | 焦橙 `#C4531A` |
| 底色 | 米白 `#F5F0E8` |
| 字色 | 白 `#FFFFFF` / 灰 `#6B6B6B` |
| 分辨率 | 2K（2048px 长边） |
| 风格 | 编辑级手绘墨水插画（像经典企鹅封面） |

## 角色参考（系列内识别度）

不同主题用不同的手绘角色，**保持手绘墨水+橙色点缀风格一致**：

| 主题 | 插画角色 |
|------|---------|
| AI 编程工具 | 方块机器人坐在电脑前 / 拿放大镜 |
| 智能体框架 | 戴眼镜的龙虾抱着花括号 |
| Agent 技能 | 方块机器人读书/拿魔法棒 |
| 自动化工程 | 蚂蚁/工蜂搭建齿轮结构 |
| 预测市场 | 水晶球+预测图表/猫头鹰 |
| 通用技术 | 抽象几何 + 工具图标 |

## 生成规则（⚠️ 必须全部满足）

1. **工具**：必须用 AI 一步生成（nano-banana-pro / Midjourney / GPT-Image-1），**不用 HTML 拼接**
2. **每次生成 3 版候选**让作者选
3. **分辨率**：2K（2048px）
4. **封面不加署名/水印**（底部「{作者名} 著」除外）
5. **填满整个画布**：图像本身就是封面，不要 3D 书本模型/阴影/边距

## Prompt 模板（直接复用，替换 `{变量}`）

```
Flat 2D book cover, portrait 3:4 aspect ratio. The image IS the cover itself,
filling 100% of the canvas edge-to-edge. NO 3D book mockup, NO drop shadow,
NO external background, NO border, NO book spine effect.

Classic Penguin Books tri-band layout:
- TOP BAND (30% height): solid burnt orange (#C4531A). '{书名}' in large bold
  white sans-serif font centered. '橙皮书' in medium white text below.
- MIDDLE BAND (45% height): cream off-white (#F5F0E8) background.
  Hand-drawn ink illustration of {角色描述}. Black ink line art with orange
  accent colors. Charming editorial illustration style like classic Penguin
  book covers. Small muted gray text '{副标题}' below the illustration.
- BOTTOM BAND (25% height): same solid burnt orange (#C4531A).
  '{作者名} 著' centered in white text.

The cover fills the entire frame, no visible edges or margins.
```

## 禁忌清单

- ❌ 橙底+黑字
- ❌ 赛博霓虹/深蓝底
- ❌ 3D 书籍效果/阴影/透视
- ❌ 正方形比例（必须竖版 3:4）
- ❌ HTML 拼接（必须 AI 一步生成）
- ❌ 写实照片风（破坏系列一致性）
- ❌ 复杂渐变（保持色块感）
- ❌ 透明/半透明元素（保证印刷效果）

## 选封面 SOP

1. 跑 prompt，生成 3 版候选
2. 视觉打分（构图/角色可爱度/字与图协调）
3. 让作者选 1 版
4. 高清出图（2K）
5. 放进项目 `封面/` 目录
6. 在 `PROJECT.md` 记录选择理由
