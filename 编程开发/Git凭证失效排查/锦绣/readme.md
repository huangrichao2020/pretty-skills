# Git 凭证失效排查 · 融合稿（公众号 + 自媒体 + AI 阅读三用）

> 一句话：`git pull` 报 401，但 `gh auth status` 明明显示已登录——这不是凭证坏了，是 shell 里一个「失效却 active」的 `GITHUB_TOKEN` 环境变量在抢戏。

## 公众号版（科普向）

你有没有遇到过这种诡异场面：`git pull` 突然报 `Authentication failed`，你赶紧 `gh auth status` 一看——显示已登录、keyring 正常。重启、重登、改 URL，全都白搭，git 还是 401。

问题不在凭证本身，而在「第三者」。git 解析凭证的顺序是 **环境变量 > keyring**。如果你的 shell 里常驻着一个 `GITHUB_TOKEN`（显示 active 但实际已失效），git 会优先读这个失效的 env token，把正常的 keyring 凭证顶掉。gh 读的是 keyring 所以没事，git 读 env 就挂——这就是「git 红、gh 绿」反差的来历。

怎么修？两步：

- **临时救火**：`env -u GITHUB_TOKEN -u GH_TOKEN -u GITHUB_ACCESS_TOKEN git -C <repo> pull`，单次命令去掉这三个变量，git 立刻回落 keyring。
- **长期根治**：建个 `~/.local/bin/git-pull-safe`，内容就一行 `unset GITHUB_TOKEN GH_TOKEN GITHUB_ACCESS_TOKEN; exec git "$@"`，以后用 `git-pull-safe pull` 替代 `git pull`。

两个坑别踩：别 `gh auth login` 重登（覆盖 keyring 也救不了 env 抢戏）；别改 remote URL（治标还会污染配置）。

## 自媒体版（短视频脚本）

[钩子] git 报 401，gh 却说你已登录？不是玄学。
[痛点] 一个失效却 active 的 GITHUB_TOKEN 环境变量，正在顶掉你的 keyring。
[机制] git 凭证顺序：env > keyring，第三者插队。
[解法] 临时 env -u 三变量；长期 git-pull-safe 包装脚本。
[金句] 别重登、别改 URL，清掉 env 才是正解。
[行动] 把 git-pull-safe 配上，从此拉代码不再 401。

## AI 阅读版（结构化要点）

- 主题：git HTTPS 401 但 gh 正常 = env token 抢戏
- 机制：git 凭证顺序 env > keyring；失效 env 顶掉 keyring
- 临时：env -u GITHUB_TOKEN GH_TOKEN GITHUB_ACCESS_TOKEN git ...
- 长期：git-pull-safe（unset 再 exec git）
- 不要做：别 gh auth login / 别改 remote URL / 别反复重试
- 套路：git 401 → gh status → keyring OK+git fail = env 抢戏
- 关联：与 NeoData token、GitHub PAT 三套独立体系

*非投资建议。*
