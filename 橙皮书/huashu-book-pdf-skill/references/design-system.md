# 设计系统参考

写作 agent 在编写 HTML 片段时**必读此文件**，了解片段结构规范、可用的 CSS class 和视觉规范。

## ⚠️ 片段结构规范（最重要！）

每个正文片段**必须**遵循以下结构，否则会导致排版错误（无左右边距、目录无法跳转）：

### 正文片段模板

```html
<div class="content">

<h2 class="section-title page-break" id="part1"><span class="num">§01</span> 章节标题</h2>
<p class="section-en">English Section Title</p>
<p class="section-intro">本节概述文字。</p>

<!-- 正文内容写在这里 -->

</div>
```

**三条铁律**：
1. **必须用 `<div class="content">` 包裹整个片段** — 这控制左右 55px 边距，没有它内容会顶边
2. **第一个 `<h2>` 必须带 `id` 属性** — 如 `id="part1"`，用于目录锚点跳转
3. **第一个 `<h2>` 必须带 `page-break` class** — 确保每章从新页开始：`class="section-title page-break"`

### 封面/目录/尾页片段

这三种特殊片段**已有自己的布局 class**（`.cover` / `.toc` / `.back-page`），不需要 `.content` 包裹：

```html
<!-- 封面：用 .cover 包裹 -->
<div class="cover">...</div>

<!-- 目录：用 .toc 包裹 -->
<div class="toc">...</div>

<!-- 尾页：用 .back-page 包裹 -->
<div class="back-page">...</div>
```

### 目录片段模板

目录必须使用 `.toc` 结构，带锚点链接：

```html
<div class="toc">
  <div style="border-top: 3px solid var(--accent); margin-bottom: 20px;"></div>
  <h2>目录</h2>
  <div class="toc-sub">CONTENTS</div>

  <div class="toc-group">Part 1: 分组标题</div>
  <div class="toc-item">
    <a href="#part1"><span class="num">§01</span><span class="title">章节标题</span></a>
  </div>
  <div class="toc-item">
    <a href="#part2"><span class="num">§02</span><span class="title">章节标题</span></a>
  </div>
  <!-- ... -->
</div>
```

**注意**：`href="#partN"` 必须与对应片段中 `<h2 id="partN">` 的 id 一致。

---

## CSS 变量

```css
:root {
  --bg: #FFFFFF;           /* 背景白 */
  --text: #1A1A1A;         /* 主文本 */
  --text-secondary: #6B6B6B;
  --accent: #C2410C;       /* 焦橙强调色（默认主题） */
  --accent-light: #FFF7ED;
  --border: #E5E5E5;
  --code-bg: #F5F5F0;
  --tip-bg: #F0FDF4;       --tip-border: #22C55E;
  --warn-bg: #FEF2F2;      --warn-border: #EF4444;
  --highlight: #FFFBEB;
}
```

## 可换主题

修改 `--accent` 和 `--accent-light` 即可切换主题：

| 主题 | --accent | --accent-light | 适用 |
|------|----------|---------------|------|
| 焦橙（默认） | #C2410C | #FFF7ED | 技术文档 |
| 深蓝 | #1E40AF | #EFF6FF | 企业白皮书 |
| 翠绿 | #15803D | #F0FDF4 | 环保/健康 |
| 暗紫 | #7C3AED | #F5F3FF | 创意/AI |
| 中国红 | #DC2626 | #FEF2F2 | 年度报告 |

## 字体与排版

- 正文：Noto Sans SC + Inter（Google Fonts），10.5pt，行高 1.8
- 代码：JetBrains Mono，9pt
- 封面标题：36pt，font-weight 900
- A4 纸，`@page margin: 18mm 0`（上下 18mm，左右由 HTML 控制）
- ⚠️ 边距分工：`@page` 只控制上下边距，左右边距由 `.content { padding: 0 55px }` 控制
- ⚠️ 绝对不要在 `@page` 和 HTML 元素中同时设置左右边距，否则会叠加导致内容区过窄
- 封面/尾页：单独的 `@page` 命名页 `margin: 0` 实现全出血，通过自身 padding 控制内距

## HTML 组件速查

片段中直接使用以下 class，无需额外定义样式。

### 封面

```html
<div class="cover">
  <div class="cover-badge">标签文字</div>
  <h1><em>强调词</em><br>副标题</h1>
  <p class="cover-subtitle">描述文字</p>
  <p class="cover-en">English Subtitle</p>
  <div class="cover-meta"><strong>标签：</strong>值<br></div>
  <div class="cover-author"><strong>{作者名}</strong><br>{作者名}</div>
  <div class="cover-exclusive">{知识星球名} 专属内容</div>
  <div class="cover-disclaimer">免责声明</div>
</div>
```

### 尾页

**注意**：class 必须是 `back-page`（带连字符），不是 `backpage`。

⚠️ **二维码图片**：每个新项目将公众号二维码 `gzh-qrcode.jpg` 复制到 `fragments/` 目录，用相对路径引用。

⚠️ **社交链接**：按 placeholder-config.json 替换为自己的社媒账号，不可遗漏。

```html
<div class="back-page">
  <div class="back-page-title">手册标题</div>
  <div class="back-page-subtitle">{知识星球名}</div>
  <div class="back-page-qr-wrapper">
    <img src="gzh-qrcode.jpg" alt="{公众号二维码描述}" class="back-page-qr" style="width:360px;">
  </div>
  <div class="back-page-info">
    <strong>{作者名} · AI Native Coder</strong><br>
    我一行代码都不会写，却用 AI 做出了 {代表作成就} 的 {代表作名}，写了 {书数量} 本技术书。<br>
    所有产品，全部 AI 写的，我只负责想清楚要做什么。<br>
    开源了 {开源项目列表} 等项目，GitHub {GitHub粉丝数}。<br>
    我始终相信：<strong>AI 生成内容不稀缺，稀缺的是判断力</strong>。
  </div>
  <div class="back-page-social">
    <a href="https://space.bilibili.com/{B站UID}/">B站：{B站用户名}</a>
    <span class="social-sep">·</span>
    <span>公众号：{公众号名}</span>
    <span class="social-sep">·</span>
    <a href="https://x.com/{X用户名}">X/Twitter</a>
    <span class="social-sep">·</span>
    <a href="https://www.youtube.com/{YouTube频道}">YouTube</a>
    <span class="social-sep">·</span>
    <a href="https://github.com/{GitHub用户名}">GitHub</a>
    <span class="social-sep">·</span>
    <a href="{官网}">官网</a>
  </div>
  <div class="back-page-footer">
    Created by {作者名} · v1.0 · {YYYY}年<br>
    本文档在 AI 辅助下整理编写，内容仅供参考。
  </div>
</div>
```

### 章节标题（完整格式）

```html
<!-- ⚠️ 必须带 id 和 page-break class -->
<h2 class="section-title page-break" id="part1"><span class="num">§01</span> 章节标题</h2>
<p class="section-en">English Section Title</p>
<p class="section-intro">本节概述文字。</p>
```

### 子标题

```html
<h3>子标题</h3>
<h4>四级标题</h4>
```

### 提示框

```html
<div class="tip">提示内容（自动显示「核心建议」标签）</div>
<div class="warning">警告内容（自动显示「注意」标签）</div>
<div class="callout"><strong>要点：</strong>高亮说明内容</div>
```

### 步骤流程

```html
<div class="step">
  <div class="step-num">1</div>
  <div class="step-content">
    <h4>步骤标题</h4>
    <p>步骤说明</p>
  </div>
</div>
```

### 流程图

```html
<div class="flow">
  <div class="flow-item">步骤A</div>
  <div class="flow-arrow">→</div>
  <div class="flow-item">步骤B</div>
</div>
```

### 对比框

```html
<div class="compare">
  <div class="compare-good">推荐做法（自动显示「推荐」标签）</div>
  <div class="compare-bad">不推荐做法（自动显示「不推荐」标签）</div>
</div>
```

### 其他

```html
<div class="file-tree">├── folder/<br>│   └── file.txt</div>
<div class="page-break"></div>  <!-- 强制分页 -->
```

表格、代码块、步骤、提示框自带 `page-break-inside: avoid`。

## 视觉红线

1. 禁止赛博霓虹风格和深蓝底（#0D1117）
2. 白底为主，强调色点缀，不要大面积色块
3. 封面不加个人署名/水印
4. 不混用字体（Inter/Noto Sans SC/JetBrains Mono 三种以外不用）
5. 图片最高 2K 分辨率，不用 4K
