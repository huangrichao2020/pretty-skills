# NeoData 令牌刷新 · 融合稿（公众号 + 自媒体 + AI 阅读三用）

> 一句话：NeoData 的 token 每 12 小时过期一次，过期后你的 AI 炒股助手会 silently 降级成「编数据」——这篇是 2026-08-20 实战踩出的刷新 SOP。

## 公众号版（科普向）

你以为你的 AI 助理在实时看盘，其实它可能已经「失联」12 小时，正在凭模板编答案。

问题出在鉴权 token。NeoData 金融搜索服务的 token **12 小时就过期**，过期后所有调用它的 skill（比如我们的「机会挖掘」微信助理）会走「模板降级」——也就是不再拉真实数据，改用写死的示例。你看不出来，但结论已经不可信。

怎么判断是不是 token 挂了？两个信号：一是 skill 报「数据拉取失败」或明显变模板腔；二是 NeoData 接口直接回 401。关键排除法：**WebSearch 还能用 = 网络正常，那 401 就只可能是 token**。

刷新三步，亲测有效：

1. **拿临时令牌**：调 `connect_cloud_service` 工具，返回一个 24h 有效的 tempToken（2026-08-20 实测拿到 `tk_2Q2p3T...`）。
2. **落盘缓存**：`python3 .../query.py --save-token "<token>"`，写进 `.neodata_token`（权限 600，别泄露）。
3. **验证闭环**：重跑 skill，看到真实板块名和涨停数回来了，才算完。

最后两个坑：别用 `gh auth login` 去修（那是 GitHub 的凭证，两码事）；别把 token 文件提交到 git（含密钥）。

## 自媒体版（短视频脚本）

[钩子] 你的 AI 助理可能正在「编」数据骗你。
[痛点] NeoData token 12h 过期 → 助手默默降级成模板腔。
[判定] 401 但 WebSearch 绿灯 = 网络没问题，是 token 挂了。
[三步] 拿 tempToken → --save-token 落盘 → 重跑验证真数据。
[金句] 别用 gh auth login 修，那是另一套钥匙。
[行动] 设个每 11 小时的 cron，让刷新自动化。

## AI 阅读版（结构化要点）

- 主题：NeoData token 12h 过期导致 skill 降级
- 判定：401 + WebSearch 正常 = token 失效（非网络）
- step1：connect_cloud_service → tempToken（24h）
- step2：query.py --save-token → .neodata_token（权限 600）
- step3：重跑 skill 验证真实数据恢复
- 自动化：cron 每 11h / 启动 probe / 失效告警
- 踩坑：别 gh auth login、别 git add token、与 GitHub PAT 独立

*非投资建议。*
