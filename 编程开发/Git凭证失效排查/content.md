# Git 凭证失效排查 · env token 抢戏诊断

> git 走 HTTPS 报 `Authentication failed`，但 `gh auth status` 显示 keyring 正常——根因是 shell 里常驻一个「失效却 active」的 `GITHUB_TOKEN` 环境变量，git 优先读 env 覆盖 keyring。本文把 2026-08-20 踩出的诊断与修复 SOP 沉淀为可复用流程。
> 适用于所有走 HTTPS 的 git 操作（SSH 不受影响）。

---

## P0 · 概览与定位

- **一句话**：git HTTPS 401 但 gh 正常 = 常驻失效 `GITHUB_TOKEN` 环境变量抢戏覆盖 keyring。
- **来源**：2026-08-20 踩坑 · Git 拉取认证失败排查。
- **定位**：git 凭证诊断 SOP · env token 劫持 · 跨仓库高频坑。
- **症状**：`git pull/fetch/push` HTTPS 报 `Authentication failed`；`gh auth status` 看着 keyring 正常。
- **影响**：所有走 HTTPS 的 git 操作；SSH 通道不受影响。
- **解法**：清掉 `GITHUB_TOKEN / GH_TOKEN / GITHUB_ACCESS_TOKEN` 再 exec git。
- **认知锚点**：一个「失效却亮着 active 灯」的 env 令牌，像插队者挤掉了排在后面的 keyring 正常凭证，强调「第三者劫持」。

## P1 · 症状与误诊

- **核心主张**：典型症状 = git 401，但 gh / keyring 都「看起来正常」。
- **症状**：`git pull` → `Authentication failed`；`gh auth status` → 显示已登录、keyring 正常。
- **误诊①**：以为要 `gh auth login` 重登（其实 keyring 没坏，重登也救不了）。
- **误诊②**：以为 remote URL 坏了去改 URL（绕开但治标，还可能误改配置）。
- **关键反差**：git 失败 + gh 正常 = 几乎肯定是第三者在抢戏，不是凭证本身。
- **认知锚点**：屏幕左右分屏：左边 git 红字 401，右边 gh 绿字「已登录」，中间打个大问号，强调「反差即线索」。

## P2 · 根因 · env 抢戏

- **核心主张**：shell 常驻一个失效的 `GITHUB_TOKEN`（active=true 但 token invalid），git 优先读 env 覆盖 keyring。
- **机制**：git 凭证解析顺序 env > keyring；失效 env token 顶掉正常 keyring 凭证。
- **陷阱**：这个 token 是「active=true 但 invalid」——gh 读 keyring 没事，git 读 env 就挂。
- **来源**：常驻在 shell profile / 某次 `export`，长期没人清，平时不触发、一拉代码就爆。
- **认知锚点**：一张「凭证解析顺序」图：env（失效）压在 keyring（正常）上面，箭头指向 git 失败，强调「顺序即命门」。

## P3 · 解法1 · 临时救火

- **核心主张**：临时用 `env -u` 去掉 env 变量，让 git 回落到 keyring。
- **命令**：`env -u GITHUB_TOKEN -u GH_TOKEN -u GITHUB_ACCESS_TOKEN git -C <repo> pull`。
- **原理**：单次命令临时清除这三个 env 变量，不改动 shell 常驻状态。
- **范围**：仅本次命令有效，适合急着拉代码立刻用。
- **验证**：执行后 pull 成功 = 确认是 env 抢戏。
- **认知锚点**：一把剪刀剪断 env 与 git 之间的连线，git 自动接回 keyring，强调「临时解耦」。

## P4 · 解法2 · 长期根治

- **核心主张**：建 `git-pull-safe` 包装脚本，自动清 env 再 exec git。
- **脚本**：`~/.local/bin/git-pull-safe`，内容 `unset GITHUB_TOKEN GH_TOKEN GITHUB_ACCESS_TOKEN; exec git "$@"`。
- **用法**：`git-pull-safe -C <repo> pull` 替代 `git pull`。
- **根治**：从根源去掉常驻失效 env，不必每次手敲 `env -u`。
- **延伸**：`gh repo rename` 等同理——`unset GITHUB_TOKEN && gh repo rename`。
- **认知锚点**：一个「清道夫」脚本挡在 git 前面自动扫除 env 地雷，强调「一次配置、长期免疫」。

## P5 · 不要做

- **核心主张**：三条错误操作会浪费时间甚至引入新问题。
- **不要①**：`gh auth login` 重登（解决不了 env 抢戏，且会覆盖 keyring 正常状态）。
- **不要②**：改 git remote URL（绕开但治标，可能误改 SSH/HTTPS 配置、污染仓库）。
- **不要③**：反复重试 git（token 失效，重试 100 次也是 401，纯浪费）。
- **认知锚点**：三个红色「禁止」标志分别挡住 gh login / 改 URL / 重试，强调「别走弯路」。

## P6 · 诊断套路 + 收束

- **核心主张**：固定诊断套路，30 秒定位 env 抢戏。
- **套路**：git 401 → `gh auth status` → keyring OK + git fail = env token 抢戏。
- **验证**：`echo $GITHUB_TOKEN` 看是否有常驻失效值（非空即嫌疑）。
- **收束**：清 env（临时 `env -u` / 长期 `git-pull-safe`）→ 重跑验证成功。
- **关联**：与 NeoData token、GitHub PAT 是三套独立体系，别混为一谈。
- **认知锚点**：一个 30 秒诊断流程图：git 401 → 查 gh → 查 env → 清 env → 成功，强调「套路化、不复乱」。

### Shot List

必画 ≤6 张（防画册陷阱，写给 AI 出图 prompt 用）：

1. 失效 env 令牌插队挤掉 keyring（P0）
2. git 红 401 vs gh 绿已登录 反差屏（P1）
3. 凭证顺序 env 压 keyring 图（P2）
4. 剪刀剪断 env 接回 keyring（P3）
5. 清道夫脚本挡 git 扫雷（P4）
6. 三个禁止标志挡弯路（P5）

选画：30 秒诊断流程图（P6）
