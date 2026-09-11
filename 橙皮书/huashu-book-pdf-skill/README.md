# huashu-book-pdf · 橙皮书全流程 Skill

> 用写一本书的方法，快速搞懂一个陌生领域，并沉淀成可分发的书籍级成果。

## 拿到这个 skill 你能做什么

| 你想做 | 拿到后能怎么用 |
|--------|----------------|
| 快速搞懂一个陌生行业/工具/赛道 | 5 阶段流水线：调研→规划→写作→审校→构建 |
| 做一本完整的电子书/手册 | 30 分钟搭起项目骨架，半天写完 5-10 章 |
| 团队知识库沉淀成可分发的书 | 多 Agent 并行写，4 遍审校保证质量 |
| 出版社交稿 | 一次生成 PDF / DOCX / EPUB 三种产物 |
| 系列化出书 | 统一视觉（企鹅三段式封面），统一风格 |

## 5 阶段流水线一览

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  1.调研  │ → │  2.规划  │ → │  3.写作  │ → │  4.审校  │ → │  5.构建  │
│ 拆领域   │   │ 列大纲   │   │ 并行写   │   │ 4遍审校  │   │ 出产物   │
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
   6-10 板块    有逻辑的        多 Agent     内容/风格/      PDF/DOCX
   知识地图     章节大纲        并行写       细节/事实       /EPUB
```

**核心不是「出书」，是用写一本书的方法快速搞懂一个陌生领域。**

## 30 分钟上手

```bash
# 1. 新建项目
bash scripts/init-project.sh ./我的新书 "我的新书标题"

# 2. 填占位符（替换为自己的真实信息）
$EDITOR 我的新书/placeholder-config.json
python3 scripts/render-placeholders.py ./我的新书

# 3. 写大纲
$EDITOR 我的新书/PROJECT.md

# 4. 多 Agent 并行写章节（详见 SKILL.md 阶段 3）
# ...

# 5. 4 遍审校（详见 SKILL.md 阶段 4）
# ...

# 6. 构建 PDF
cd 我的新书 && ./update.sh
```

## 目录结构

```
huashu-book-pdf/
├── SKILL.md                          # 主文档 · 5 阶段 SOP
├── README.md                         # 本文件
├── placeholder-config.json           # 占位符配置（填自己的信息）
├── references/
│   ├── design-system.md              # CSS 变量 + HTML 组件速查
│   ├── cover-system.md               # 企鹅三段式封面规范
│   ├── fact-check-sop.md             # 怀疑者三问 + 易错场景
│   └── style-guide.md                # 降 AI 味检查清单
├── scripts/
│   ├── init-project.sh               # 一键生成项目骨架
│   └── render-placeholders.py        # 批量替换占位符
└── templates/
    ├── styles.css                    # 共享 CSS（焦橙主题）
    ├── build.js                      # HTML 合并脚本
    ├── build-pdf.js                  # Playwright → PDF
    ├── update.sh                     # 一键版本更新 + 重建
    └── fragments/
        ├── 00-cover.html             # 封面模板（含占位符）
        └── 99-backpage.html          # 尾页模板（含占位符）
```

## 关键设计决策

### 为什么用日期版本号（vYYMMDD）而不是语义版本（1.0.0）？

- 一眼能看出什么时候的版本（不用查 CHANGELOG）
- 每天的实质性更新 = 1 天
- `build` 字段管同一天内的多次构建
- 不需要决定「这是 minor 还是 patch」

### 为什么要 4 遍审校？

| 审校 | 解决的问题 | 不解决的问题 |
|------|----------|------------|
| 内容审校 | 章节内信息是否完整、逻辑是否通 | 写得对不对 |
| 风格审校 | 降 AI 味，加个性化语感 | 写得对不对 |
| 细节打磨 | 句子长度、段落长度、标点 | 写得对不对 |
| **事实核查** | **写得对不对**（用 WebSearch 查一手） | 跨章节重复 |
| 一致性审查 | 跨章节重复、冲突、术语 | - |

**事实核查是 4 遍审校里唯一必须用 WebSearch 查一手的**。其他 3 遍用同一个模型知识库校验，错误会在同一个信息茧房里反复传播。

### 为什么用企鹅三段式封面？

- 系列识别度强（一眼能认出是「橙皮书系列」）
- 视觉简单（不用复杂插画也能出彩）
- 印刷友好（色块而非渐变）
- 竖版 3:4 适配主流电子书和实体书比例

## 适用 vs 不适用

**适合**：
- 想系统搞懂一个陌生行业、工具、赛道
- 想做一份能交付给别人的系统化资料
- 团队知识库沉淀为可分发的书籍级成果
- 有几万字的长内容生产需求

**不适合**：
- 几页的快速参考（→ 直接 markdown）
- 单页海报 / PPT（→ 用对应 skill）
- 实时更新的内部 wiki（→ 走 docs 系统）
- 1-3 页的简短文档

## 量化疗效

| 维度 | 没有 skill | 用了 skill |
|------|----------|----------|
| 项目启动 | 2 小时摸目录结构 | **30 秒一条命令** |
| 章节写作（5 章） | 一个人熬 1 周 | **多 Agent 并行，1-2 天** |
| 事实核查 | 凭印象，错了不察觉 | **WebSearch 查一手 + 存疑清单** |
| 风格一致性 | 章节间风格漂移 | **4 遍审校流水线** |
| 三种产物（PDF/DOCX/EPUB） | 各自折腾半天 | **`./update.sh` 一条命令** |
| 版本管理 | 手动改文件名 | **日期版本号 + 自动 build** |

## 详细文档

按需读取：
- [SKILL.md](SKILL.md) — 主文档，必读
- [references/design-system.md](references/design-system.md) — 写 HTML 片段时
- [references/cover-system.md](references/cover-system.md) — 做封面时
- [references/fact-check-sop.md](references/fact-check-sop.md) — 事实核查时
- [references/style-guide.md](references/style-guide.md) — 风格审校时

## 致谢

这个 skill 的方法论来自花叔写 9 本橙皮书的实战沉淀。已发布的内容版权归原作者所有，本 skill 只沉淀「方法论 + 工具链」，不复制任何已发布内容。
